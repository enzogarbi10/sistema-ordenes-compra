from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.forms import inlineformset_factory
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.mail import EmailMessage
import io
import json
import threading

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from .models import ControlCalidad, ImagenControl, Maquinista, OperarioInspeccion, TipoDefecto, OpcionDefecto, NotificacionEmail
from ordenes_trabajo.models import Cliente
from .forms import ControlCalidadForm, ImagenControlForm

# --- Permissions ---
def calidad_group_required(user):
    return user.is_superuser or user.groups.filter(name='Calidad').exists()

class CalidadGroupRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return calidad_group_required(self.request.user)

# --- Views ---

class ControlListView(LoginRequiredMixin, CalidadGroupRequiredMixin, ListView):
    model = ControlCalidad
    template_name = 'postprensa/lista_controles.html'
    context_object_name = 'controles'
    ordering = ['-fecha']

@login_required
@user_passes_test(calidad_group_required)
def crear_control(request):
    ImagenFormSet = inlineformset_factory(ControlCalidad, ImagenControl, form=ImagenControlForm, extra=0, can_delete=False)
    
    if request.method == 'POST':
        form = ControlCalidadForm(request.POST)
        formset = ImagenFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                control = form.save(commit=False)
                control.creado_por = request.user
                control.save()
                form.save_m2m()  # Save ManyToMany (defectos)
                imagenes = formset.save(commit=False)
                for img in imagenes:
                    img.control = control
                    img.save()
                    
                # Procesar múltiple subida de fotos
                archivos_nombres = request.FILES.getlist('evidencias')
                for archivo_file in archivos_nombres:
                    ImagenControl.objects.create(control=control, imagen=archivo_file)
                    
            # Invocar notificación enviando en hilo paralelo
            threading.Thread(target=enviar_email_nuevo_control_bg, args=(control.id,)).start()
            
            return redirect('lista_controles_postprensa')
    else:
        form = ControlCalidadForm()
        formset = ImagenFormSet()
    
    # Build opciones_json for frontend
    opciones_dict = {}
    for op in OpcionDefecto.objects.filter(activo=True):
        if op.tipo_defecto_id not in opciones_dict:
            opciones_dict[op.tipo_defecto_id] = []
        opciones_dict[op.tipo_defecto_id].append({'id': op.id, 'nombre': op.nombre})
    
    return render(request, 'postprensa/form_control.html', {
        'form': form, 
        'formset': formset,
        'titulo': 'Nuevo Control de Calidad',
        'opciones_json': json.dumps(opciones_dict)
    })

@login_required
@user_passes_test(calidad_group_required)
def editar_control(request, pk):
    control = get_object_or_404(ControlCalidad, pk=pk)
    
    # Permitir edición si es staff O si es el creador
    if not request.user.is_staff and control.creado_por != request.user:
        return redirect('lista_controles_postprensa')
    
    ImagenFormSet = inlineformset_factory(
        ControlCalidad, ImagenControl, form=ImagenControlForm,
        extra=0, can_delete=True
    )
    
    if request.method == 'POST':
        form = ControlCalidadForm(request.POST, instance=control)
        formset = ImagenFormSet(request.POST, request.FILES, instance=control)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
                
                # Procesar múltiple subida de fotos extra en edición
                archivos_nombres = request.FILES.getlist('evidencias')
                for archivo_file in archivos_nombres:
                    ImagenControl.objects.create(control=control, imagen=archivo_file)
                    
            return redirect('lista_controles_postprensa')
    else:
        form = ControlCalidadForm(instance=control)
        formset = ImagenFormSet(instance=control)
    
    # Build opciones_json for frontend
    opciones_dict = {}
    for op in OpcionDefecto.objects.filter(activo=True):
        if op.tipo_defecto_id not in opciones_dict:
            opciones_dict[op.tipo_defecto_id] = []
        opciones_dict[op.tipo_defecto_id].append({'id': op.id, 'nombre': op.nombre})

    return render(request, 'postprensa/form_control.html', {
        'form': form,
        'formset': formset,
        'titulo': f'Editar Control OT #{control.orden}',
        'editando': True,
        'control': control,
        'opciones_json': json.dumps(opciones_dict)
    })

@login_required
@user_passes_test(calidad_group_required)
def eliminar_control(request, pk):
    # Solo staff puede eliminar
    if not request.user.is_staff:
        return redirect('lista_controles_postprensa')
    
    control = get_object_or_404(ControlCalidad, pk=pk)
    
    if request.method == 'POST':
        control.delete()
        return redirect('lista_controles_postprensa')
    
    return render(request, 'postprensa/confirmar_eliminar.html', {
        'control': control,
    })


# --- AJAX views for managing Maquinista (staff only) ---

@require_POST
@login_required
def agregar_maquinista(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'error': 'El nombre es requerido'}, status=400)
    if Maquinista.objects.filter(nombre__iexact=nombre).exists():
        return JsonResponse({'error': 'Ya existe un maquinista con ese nombre'}, status=400)
    maquinista = Maquinista.objects.create(nombre=nombre)
    return JsonResponse({'id': maquinista.id, 'nombre': maquinista.nombre})

@require_POST
@login_required
def editar_maquinista(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        maquinista = Maquinista.objects.get(pk=pk)
    except Maquinista.DoesNotExist:
        return JsonResponse({'error': 'Maquinista no encontrado'}, status=404)
    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'error': 'El nombre es requerido'}, status=400)
    if Maquinista.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
        return JsonResponse({'error': 'Ya existe un maquinista con ese nombre'}, status=400)
    maquinista.nombre = nombre
    maquinista.save()
    return JsonResponse({'id': maquinista.id, 'nombre': maquinista.nombre})

@require_POST
@login_required
def eliminar_maquinista(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        maquinista = Maquinista.objects.get(pk=pk)
    except Maquinista.DoesNotExist:
        return JsonResponse({'error': 'Maquinista no encontrado'}, status=404)
    if ControlCalidad.objects.filter(maquinista=maquinista).exists():
        return JsonResponse({'error': 'No se puede eliminar: tiene controles asociados.'}, status=400)
    maquinista.delete()
    return JsonResponse({'ok': True})


# --- AJAX views for managing Operario (staff only) ---

@require_POST
@login_required
def agregar_operario(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'error': 'El nombre es requerido'}, status=400)
    if OperarioInspeccion.objects.filter(nombre__iexact=nombre).exists():
        return JsonResponse({'error': 'Ya existe un operario con ese nombre'}, status=400)
    operario = OperarioInspeccion.objects.create(nombre=nombre)
    return JsonResponse({'id': operario.id, 'nombre': operario.nombre})

@require_POST
@login_required
def editar_operario(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        operario = OperarioInspeccion.objects.get(pk=pk)
    except OperarioInspeccion.DoesNotExist:
        return JsonResponse({'error': 'Operario no encontrado'}, status=404)
    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'error': 'El nombre es requerido'}, status=400)
    if OperarioInspeccion.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
        return JsonResponse({'error': 'Ya existe un operario con ese nombre'}, status=400)
    operario.nombre = nombre
    operario.save()
    return JsonResponse({'id': operario.id, 'nombre': operario.nombre})

@require_POST
@login_required
def eliminar_operario(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        operario = OperarioInspeccion.objects.get(pk=pk)
    except OperarioInspeccion.DoesNotExist:
        return JsonResponse({'error': 'Operario no encontrado'}, status=404)
    if ControlCalidad.objects.filter(operario=operario).exists():
        return JsonResponse({'error': 'No se puede eliminar: tiene controles asociados.'}, status=400)
    operario.delete()
    return JsonResponse({'ok': True})


# --- AJAX views for managing TipoDefecto (staff only) ---

@require_POST
@login_required
def agregar_tipo_defecto(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'error': 'El nombre es requerido'}, status=400)
    if TipoDefecto.objects.filter(nombre__iexact=nombre).exists():
        return JsonResponse({'error': 'Ya existe un tipo de defecto con ese nombre'}, status=400)
    tipo = TipoDefecto.objects.create(nombre=nombre)
    return JsonResponse({'id': tipo.id, 'nombre': tipo.nombre})

@require_POST
@login_required
def editar_tipo_defecto(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        tipo = TipoDefecto.objects.get(pk=pk)
    except TipoDefecto.DoesNotExist:
        return JsonResponse({'error': 'Tipo de defecto no encontrado'}, status=404)
    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'error': 'El nombre es requerido'}, status=400)
    if TipoDefecto.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
        return JsonResponse({'error': 'Ya existe un tipo de defecto con ese nombre'}, status=400)
    tipo.nombre = nombre
    tipo.save()
    return JsonResponse({'id': tipo.id, 'nombre': tipo.nombre})

@require_POST
@login_required
def eliminar_tipo_defecto(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        tipo = TipoDefecto.objects.get(pk=pk)
    except TipoDefecto.DoesNotExist:
        return JsonResponse({'error': 'Tipo de defecto no encontrado'}, status=404)
    if tipo.controlcalidad_set.exists():
        return JsonResponse({'error': 'No se puede eliminar: tiene controles asociados.'}, status=400)
    tipo.delete()
    return JsonResponse({'ok': True})


# --- AJAX views for managing OpcionDefecto (staff only) ---

@login_required
def obtener_opciones_defecto(request, tipo_id):
    """GET: returns options for a given TipoDefecto."""
    opciones = OpcionDefecto.objects.filter(tipo_defecto_id=tipo_id, activo=True).values('id', 'nombre')
    return JsonResponse({'opciones': list(opciones)})

@require_POST
@login_required
def agregar_opcion_defecto(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    tipo_id = request.POST.get('tipo_defecto_id')
    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'error': 'El nombre es requerido'}, status=400)
    try:
        tipo = TipoDefecto.objects.get(pk=tipo_id)
    except TipoDefecto.DoesNotExist:
        return JsonResponse({'error': 'Tipo de defecto no encontrado'}, status=404)
    if OpcionDefecto.objects.filter(tipo_defecto=tipo, nombre__iexact=nombre).exists():
        return JsonResponse({'error': 'Ya existe esa opción para este tipo de defecto'}, status=400)
    opcion = OpcionDefecto.objects.create(tipo_defecto=tipo, nombre=nombre)
    return JsonResponse({'id': opcion.id, 'nombre': opcion.nombre, 'tipo_defecto_id': tipo.id})

@require_POST
@login_required
def editar_opcion_defecto(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        opcion = OpcionDefecto.objects.get(pk=pk)
    except OpcionDefecto.DoesNotExist:
        return JsonResponse({'error': 'Opción no encontrada'}, status=404)
    nombre = request.POST.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'error': 'El nombre es requerido'}, status=400)
    if OpcionDefecto.objects.filter(tipo_defecto=opcion.tipo_defecto, nombre__iexact=nombre).exclude(pk=pk).exists():
        return JsonResponse({'error': 'Ya existe esa opción'}, status=400)
    opcion.nombre = nombre
    opcion.save()
    return JsonResponse({'id': opcion.id, 'nombre': opcion.nombre})

@require_POST
@login_required
def eliminar_opcion_defecto(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        opcion = OpcionDefecto.objects.get(pk=pk)
    except OpcionDefecto.DoesNotExist:
        return JsonResponse({'error': 'Opción no encontrada'}, status=404)
    if opcion.controlcalidad_set.exists():
        return JsonResponse({'error': 'No se puede eliminar: tiene controles asociados.'}, status=400)
    opcion.delete()
    return JsonResponse({'ok': True})


# --- Estadísticas ---

class EstadisticasPostprensaView(LoginRequiredMixin, CalidadGroupRequiredMixin, TemplateView):
    template_name = 'postprensa/estadisticas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        qs = ControlCalidad.objects.all()

        # Filters
        filter_mes = self.request.GET.get('mes', '')
        filter_anio = self.request.GET.get('anio', '')
        filter_maquinista = self.request.GET.get('maquinista', '')
        filter_tipo_defecto = self.request.GET.get('tipo_defecto', '')
        filter_opcion_defecto = self.request.GET.get('opcion_defecto', '')

        if filter_mes:
            qs = qs.filter(fecha__month=filter_mes)
        if filter_anio:
            qs = qs.filter(fecha__year=filter_anio)
        if filter_maquinista:
            qs = qs.filter(maquinista__nombre__icontains=filter_maquinista)
        if filter_tipo_defecto:
            qs = qs.filter(defectos__id=filter_tipo_defecto)
        if filter_opcion_defecto:
            qs = qs.filter(opciones_defecto__id=filter_opcion_defecto)

        # 1. Total Descartes por Mes (cronológico)
        descartes_mes = list(qs.annotate(month=TruncMonth('fecha')) \
            .values('month') \
            .annotate(total_descarte=Sum('cantidad_descartada')) \
            .order_by('month'))
            
        # 2. Defectos Más Comunes (dinámico)
        total = qs.count()
        if total > 0:
            defectos_comunes = TipoDefecto.objects.filter(activo=True).annotate(
                cantidad=Count('controlcalidad', filter=Q(controlcalidad__in=qs))
            ).order_by('-cantidad')
            defectos_sorted = {d.nombre: d.cantidad for d in defectos_comunes if d.cantidad > 0}
            
            # Sub-errores (Opciones)
            opciones_comunes = OpcionDefecto.objects.filter(activo=True).annotate(
                cantidad=Count('controlcalidad', filter=Q(controlcalidad__in=qs))
            ).order_by('-cantidad')
            
            opciones_raw_json = []
            opciones_sorted = {}
            for o in opciones_comunes:
                if o.cantidad > 0:
                    opciones_sorted[f"{o.tipo_defecto.nombre} - {o.nombre}"] = o.cantidad
                    opciones_raw_json.append({
                        'tipo_id': o.tipo_defecto.id,
                        'tipo_nombre': o.tipo_defecto.nombre,
                        'nombre': o.nombre,
                        'cantidad': o.cantidad
                    })
        else:
            defectos_sorted = {}
            opciones_sorted = {}
            opciones_raw_json = []

        # 3. Descartes por Maquinista con Desglose de Errores
        maquinistas_qs = qs.values('maquinista__nombre', 'maquinista__id') \
            .annotate(total=Sum('cantidad_descartada')) \
            .order_by('-total')
            
        descartes_maquinista = []
        for item in maquinistas_qs:
            maq_id = item['maquinista__id']
            maq_qs = qs.filter(maquinista__id=maq_id) if maq_id else qs.filter(maquinista__isnull=True)
            
            # Contar Subtipos (OpcionDefecto)
            opciones = OpcionDefecto.objects.filter(controlcalidad__in=maq_qs).annotate(
                cantidad=Count('controlcalidad')
            ).order_by('-cantidad')
            
            # Contar Tipos (TipoDefecto)
            tipos = TipoDefecto.objects.filter(controlcalidad__in=maq_qs).annotate(
                cantidad=Count('controlcalidad')
            ).order_by('-cantidad')
            
            desglose = []
            for op in opciones:
                if op.cantidad > 0:
                    desglose.append({'nombre': op.nombre, 'cantidad': op.cantidad})
                    
            if not desglose:
                for t in tipos:
                    if t.cantidad > 0:
                        desglose.append({'nombre': t.nombre, 'cantidad': t.cantidad})
            
            total_mq = item['total'] or 0
            descartes_maquinista.append({
                'maquinista': item['maquinista__nombre'] or "Sin Maquinista", 
                'total': total_mq,
                'porcentaje': min((total_mq / (sum(x['total'] or 0 for x in maquinistas_qs) or 1)) * 100, 100),
                'desglose': desglose
            })
            
        # 4. No llegaron a cantidad
        no_llego_cantidad = qs.filter(llego_cantidad=False).count()

        # JSON para Gráficos
        chart_meses_labels = [item['month'].strftime("%b %Y") if item['month'] else "Sin Fecha" for item in descartes_mes]
        chart_meses_data = [item['total_descarte'] or 0 for item in descartes_mes]
        
        chart_defectos_labels = list(defectos_sorted.keys())
        chart_defectos_data = list(defectos_sorted.values())
        
        chart_opciones_labels = list(opciones_sorted.keys())
        chart_opciones_data = list(opciones_sorted.values())
        
        chart_maquinistas_labels = [item['maquinista'] for item in descartes_maquinista]
        chart_maquinistas_data = [item['total'] for item in descartes_maquinista]

        # Listas para filtros
        maquinistas_list = Maquinista.objects.filter(activo=True).values_list('nombre', flat=True)
        tipos_defecto_list = TipoDefecto.objects.filter(activo=True)
        opciones_defecto_list = OpcionDefecto.objects.filter(activo=True).select_related('tipo_defecto').order_by('tipo_defecto__nombre', 'nombre')

        # Helper for month selection in template without using spaces/==
        meses_selected = {f"mes_{i}": "selected" if filter_mes == str(i) else "" for i in range(1, 13)}
        context.update(meses_selected)

        # Helper for types in template
        for t in tipos_defecto_list:
            t.is_selected = "selected" if filter_tipo_defecto == str(t.id) else ""
            
        for op in opciones_defecto_list:
            op.is_selected = "selected" if filter_opcion_defecto == str(op.id) else ""
            
        context['descartes_mes'] = descartes_mes
        context['defectos_comunes'] = defectos_sorted
        context['opciones_comunes'] = opciones_sorted
        context['descartes_maquinista'] = descartes_maquinista
        context['no_llego_cantidad'] = no_llego_cantidad
        context['total_controles'] = total
        
        context['filter_mes'] = filter_mes
        context['filter_anio'] = filter_anio
        context['filter_maquinista'] = filter_maquinista
        context['filter_tipo_defecto'] = filter_tipo_defecto
        context['filter_opcion_defecto'] = filter_opcion_defecto
        
        context['maquinistas_list'] = maquinistas_list
        context['tipos_defecto_list'] = tipos_defecto_list
        context['opciones_defecto_list'] = opciones_defecto_list
        
        # Variables JSON para Chart.js
        import json
        context['chart_meses_labels'] = json.dumps(chart_meses_labels)
        context['chart_meses_data'] = json.dumps(chart_meses_data)
        context['chart_defectos_labels'] = json.dumps(chart_defectos_labels)
        context['chart_defectos_data'] = json.dumps(chart_defectos_data)
        context['chart_opciones_labels'] = json.dumps(chart_opciones_labels)
        context['chart_opciones_data'] = json.dumps(chart_opciones_data)
        context['chart_maquinistas_labels'] = json.dumps(chart_maquinistas_labels)
        context['chart_maquinistas_data'] = json.dumps(chart_maquinistas_data)
        context['opciones_raw_json'] = json.dumps(opciones_raw_json)

        return context


# --- PDF Reports ---

@login_required
@user_passes_test(calidad_group_required)
def descargar_estadisticas_pdf(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # --- Header con Logo ---
    logo_path = settings.BASE_DIR / 'static' / 'img' / 'logo.png'
    title_text = "Reporte de Calidad - Postprensa"
    
    if logo_path.exists():
        img = Image(str(logo_path), width=120, height=40, kind='proportional')
        img.hAlign = 'LEFT'
        header_data = [[img, Paragraph(title_text, styles['Title'])]]
        t_header = Table(header_data, colWidths=[150, 300])
        t_header.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
        ]))
        elements.append(t_header)
    else:
        elements.append(Paragraph(title_text, styles['Title']))
    
    elements.append(Spacer(1, 20))
    
    # Resumen General
    total = ControlCalidad.objects.count()
    no_llego = ControlCalidad.objects.filter(llego_cantidad=False).count()
    elements.append(Paragraph("Resumen General", styles['Heading2']))
    elements.append(Paragraph(f"Total Controles Realizados: {total}", styles['Normal']))
    elements.append(Paragraph(f"Órdenes con Faltantes: {no_llego}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Defectos (dinámico)
    elements.append(Paragraph("Defectos Frecuentes", styles['Heading2']))
    data = [['Tipo de Defecto', 'Cantidad']]
    
    for tipo in TipoDefecto.objects.filter(activo=True):
        count = ControlCalidad.objects.filter(defectos=tipo).count()
        data.append([tipo.nombre, str(count)])
        
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_calidad.pdf"'
    return response

def generar_pdf_bytes_control(control):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # --- Header con Logo ---
    logo_path = settings.BASE_DIR / 'static' / 'img' / 'logo.png'
    title_text = f"Control de Calidad #{control.id}"
    
    if logo_path.exists():
        img = Image(str(logo_path), width=120, height=40, kind='proportional')
        img.hAlign = 'LEFT'
        header_data = [[img, Paragraph(title_text, styles['Title'])]]
        t_header = Table(header_data, colWidths=[150, 300])
        t_header.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'LEFT'),
        ]))
        elements.append(t_header)
    else:
        elements.append(Paragraph(title_text, styles['Title']))
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Orden de Trabajo: {control.orden}", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    # 2. General Info Table
    data_info = [
        ['Fecha:', control.fecha.strftime("%d/%m/%Y %H:%M")],
        ['Operario:', str(control.operario) if control.operario else '-'],
        ['Maquinista:', str(control.maquinista) if control.maquinista else '-'],
        ['Bobina:', control.bobina or '-'],
        ['Estado:', 'Aprobado' if control.llego_cantidad else 'Con Faltantes'],
    ]
    t_info = Table(data_info, colWidths=[100, 300])
    t_info.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 20))
    
    # 3. Defectos (dinámico)
    elements.append(Paragraph("Detalle de Defectos", styles['Heading3']))
    
    defectos_lista = control.defectos.all()
    str_defectos = ", ".join([d.nombre for d in defectos_lista]) if defectos_lista.exists() else "Sin defectos marcados"
    
    data_defects = [
        ['Tipos de Defecto:', str_defectos],
        ['Cantidad Descartada:', f"{control.cantidad_descartada} unidades"],
        ['Detalle:', control.detalle_defecto or '-'],
    ]
    t_defects = Table(data_defects, colWidths=[120, 380])
    t_defects.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), colors.darkred),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(t_defects)
    elements.append(Spacer(1, 20))
    
    # 4. Evidencia (Imagenes)
    if control.imagenes.exists():
        elements.append(Paragraph("Evidencia Visual", styles['Heading3']))
        for img_obj in control.imagenes.all():
            try:
                img = Image(img_obj.imagen.path, width=300, height=200, kind='proportional')
                elements.append(img)
                if img_obj.descripcion:
                    elements.append(Paragraph(f"Nota: {img_obj.descripcion}", styles['Italic']))
                elements.append(Spacer(1, 10))
            except Exception:
                elements.append(Paragraph("[Error cargando imagen]", styles['Normal']))

    # 5. Cierre
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Cierre del Control", styles['Heading3']))
    data_closure = [
        ['Autorizó Envío:', control.autorizo_envio or '-'],
        ['Observaciones:', control.observaciones or '-'],
    ]
    t_closure = Table(data_closure, colWidths=[100, 400])
    t_closure.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(t_closure)
    
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def enviar_email_nuevo_control_bg(control_id):
    try:
        control = ControlCalidad.objects.get(pk=control_id)
        destinatarios = list(NotificacionEmail.objects.filter(activo=True).values_list('email', flat=True))
        if not destinatarios:
            return
        
        pdf_bytes = generar_pdf_bytes_control(control)
        subject = f"Nuevo Control de Calidad Registrado: OT #{control.orden}"
        
        creator_name = control.creado_por.username if control.creado_por else 'Sistema'
        body = f"""Hola,
        
Se ha registrado un NUEVO control de calidad en el sistema.

Detalles:
- OT Nro: {control.orden}
- Fecha de Control: {control.fecha.strftime("%d/%m/%Y %H:%M")}
- Operario: {control.operario}
- Creado por: {creator_name}

Adjunto a este correo encontrará el reporte en formato PDF con el detalle de defectos, cantidades, maquinas y la evidencia en imágenes.

Saludos automáticos,
Sistema Gráfica Melfa"""

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios,
        )
        email.attach(f"Control_{control.orden}_{control.id}.pdf", pdf_bytes, 'application/pdf')
        email.send(fail_silently=False)
    except Exception as e:
        print(f"[MAIL_ERROR] No se pudo enviar notificación de control {control_id}: {e}")

@login_required
@user_passes_test(calidad_group_required)
def control_pdf(request, pk):
    control = get_object_or_404(ControlCalidad, pk=pk)
    
    pdf = generar_pdf_bytes_control(control)
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="control_{control.id}.pdf"'
    return response

# --- API CLIENTES ---
@require_POST
@login_required
def agregar_cliente(request):
    if not request.user.is_staff: return JsonResponse({'error': 'No autorizado'}, status=403)
    nombre = request.POST.get('nombre', '').strip()
    if not nombre: return JsonResponse({'error': 'El nombre es requerido'}, status=400)
    
    if Cliente.objects.filter(nombre__iexact=nombre).exists():
        return JsonResponse({'error': 'Ya existe un cliente con ese nombre'}, status=400)
        
    try:
        cliente = Cliente.objects.create(nombre=nombre)
        return JsonResponse({'id': cliente.id, 'nombre': cliente.nombre})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
@login_required
def editar_cliente(request, pk):
    if not request.user.is_staff: return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        cliente = Cliente.objects.get(pk=pk)
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'Cliente no encontrado'}, status=404)
        
    nombre = request.POST.get('nombre', '').strip()
    if not nombre: return JsonResponse({'error': 'Nombre requerido'}, status=400)
    
    if Cliente.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
        return JsonResponse({'error': 'Ya existe otro cliente con ese nombre'}, status=400)
    
    cliente.nombre = nombre
    cliente.save()
    return JsonResponse({'id': cliente.id, 'nombre': cliente.nombre})

@require_POST
@login_required
def eliminar_cliente(request, pk):
    if not request.user.is_staff: return JsonResponse({'error': 'No autorizado'}, status=403)
    try:
        cliente = Cliente.objects.get(pk=pk)
        if cliente.ordencompra_set.exists():
             return JsonResponse({'error': 'No se puede eliminar: tiene Órdenes de Compra asociadas'}, status=400)
        
        # Check ControlCalidad usage
        if hasattr(cliente, 'controlcalidad_set') and cliente.controlcalidad_set.exists():
             return JsonResponse({'error': 'No se puede eliminar: tiene Controles de Calidad asociados'}, status=400)
             
        cliente.delete()
        return JsonResponse({'success': True})
    except Cliente.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
