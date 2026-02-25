from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from .models import OrdenCompra, ItemOrden, Cliente
from .forms import OrdenCompraForm, ItemOrdenFormSet, ClienteForm
from django.db import transaction
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from django.core.mail import EmailMessage
from django.conf import settings
import io
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test

# --- Cliente Views ---

# --- Permissions Mixins ---
class OrdenesGroupRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='Ordenes').exists()

def ordenes_group_required(user):
    return user.is_superuser or user.groups.filter(name='Ordenes').exists()

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class ClienteListView(LoginRequiredMixin, OrdenesGroupRequiredMixin, ListView):
    model = Cliente
    template_name = 'ordenes_trabajo/lista_clientes.html'
    context_object_name = 'clientes'
    ordering = ['nombre']

class ClienteCreateView(LoginRequiredMixin, SuperUserRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'ordenes_trabajo/form_cliente.html'
    success_url = reverse_lazy('lista_clientes')
    extra_context = {'titulo': 'Nuevo Cliente'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = RegistroUsuarioForm(self.request.POST)
        else:
            context['user_form'] = RegistroUsuarioForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        if 'user_form' in context:
            user_form = context['user_form']
            if user_form.is_valid():
                user = user_form.save()
                self.object = form.save(commit=False)
                self.object.user = user
                self.object.save()
                return redirect(self.success_url)
            else:
                return self.render_to_response(self.get_context_data(form=form))
        
        return super().form_valid(form)

class ClienteUpdateView(LoginRequiredMixin, SuperUserRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'ordenes_trabajo/form_cliente.html'
    success_url = reverse_lazy('lista_clientes')
    extra_context = {'titulo': 'Editar Cliente'}

class ClienteDeleteView(LoginRequiredMixin, SuperUserRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'ordenes_trabajo/confirmar_borrado_cliente.html'
    success_url = reverse_lazy('lista_clientes')

# --- Orden Views ---
class OrdenListView(LoginRequiredMixin, ListView):
    model = OrdenCompra
    template_name = 'ordenes_trabajo/lista_ordenes.html'
    context_object_name = 'ordenes'
    ordering = ['-numero']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter active orders
        queryset = queryset.filter(active=True)
        
        user = self.request.user
        if not (user.is_superuser or user.is_staff):
            queryset = queryset.filter(cliente__user=user)

        # Search Filters
        q = self.request.GET.get('q')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        cliente_id = self.request.GET.get('cliente_id')

        if q:
            queryset = queryset.filter(numero__icontains=q)
        if fecha_desde:
            queryset = queryset.filter(fecha_creacion__date__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_creacion__date__lte=fecha_hasta)
        if cliente_id and (user.is_superuser or user.is_staff): # Only admins can filter by any client
            queryset = queryset.filter(cliente_id=cliente_id)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_superuser or user.is_staff:
            context['clientes'] = Cliente.objects.all()
        return context

@login_required
def crear_orden(request):
    if request.method == 'POST':
        form = OrdenCompraForm(request.POST, user=request.user)
        formset = ItemOrdenFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                orden = form.save()
                items = formset.save(commit=False)
                for item in items:
                    item.orden = orden
                    item.save()
                for obj in formset.deleted_objects:
                    obj.delete()
                
                # Generar PDF y enviar email
                try:
                    pdf_content = _generate_pdf_bytes(orden)
                    print(f"PDF generado. Tamaño: {len(pdf_content)} bytes")
                    
                    email = EmailMessage(
                        subject=f'Nueva Orden de Compra N°{orden.numero}',
                        body=f'Adjunto encontrarás la orden de compra N°{orden.numero} para el cliente {orden.cliente.nombre}.',
                        from_email=settings.EMAIL_HOST_USER,
                        to=['ventas@agmelfa.com.ar'],
                    )
                    email.attach(f'orden_{orden.numero}.pdf', pdf_content, 'application/pdf')
                    email.send()
                    print("Email enviado correctamente desde la vista.")
                except Exception as e:
                    import traceback
                    print(f"Error al enviar email: {e}")
                    traceback.print_exc()

            return redirect('lista_ordenes')
    else:
        form = OrdenCompraForm(user=request.user)
        formset = ItemOrdenFormSet()
    
    return render(request, 'ordenes_trabajo/form_orden.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Nueva Orden de Compra'
    })

def _generate_pdf_bytes(orden):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos Personalizados
    style_title = styles['Heading1']
    style_title.alignment = 1 # Center
    style_title.fontSize = 20
    style_title.spaceAfter = 20

    style_subtitle = styles['Heading2']
    style_subtitle.fontSize = 14
    style_subtitle.textColor = colors.HexColor('#555555')
    style_subtitle.spaceAfter = 10

    style_normal = styles['Normal']
    style_normal.fontSize = 10
    style_normal.leading = 14

    style_label = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#333333')
    )
    
    style_value = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.black
    )

    # --- Header / Logo ---
    logo_path = settings.BASE_DIR / 'static' / 'img' / 'logo.png'
    header_data = []
    if logo_path.exists():
        img = Image(str(logo_path), width=150, height=50, kind='proportional')
        img.hAlign = 'LEFT'
        header_data.append([img, Paragraph(f"<b>ORDEN DE COMPRA N° {orden.numero}</b>", style_title)])
    else:
        header_data.append([Paragraph("AGMELFA", style_title), Paragraph(f"<b>ORDEN DE COMPRA N° {orden.numero}</b>", style_title)])
    
    header_table = Table(header_data, colWidths=[200, 300])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))

    # --- Info Cliente y Fecha ---
    from datetime import datetime
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    info_data = [
        [Paragraph("<b>Cliente:</b>", style_label), Paragraph(orden.cliente.nombre, style_value),
         Paragraph("<b>Generado el:</b>", style_label), Paragraph(ahora, style_value)]
    ]
    
    info_table = Table(info_data, colWidths=[60, 200, 100, 150])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,1), (-1,1), 1, colors.lightgrey),
        ('BOTTOMPADDING', (0,1), (-1,1), 10),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    # --- Items ---
    elements.append(Paragraph("Detalle de Items", style_subtitle))
    elements.append(Spacer(1, 10))

    for i, item in enumerate(orden.items.all(), 1):
        # Preparar datos del item
        terminaciones = []
        if item.serigrafia: terminaciones.append("Serigrafía")
        if item.stamping: terminaciones.append("Stamping")
        if item.relieve: terminaciones.append("Relieve")
        if item.bajo_relieve: terminaciones.append("Bajo Relieve")
        if item.gofrado: terminaciones.append("Gofrado")
        if item.barniz_sectorizado: terminaciones.append("Barniz Sectorizado")
        str_terminaciones = ", ".join(terminaciones) if terminaciones else "Ninguna"

        # Columna de Detalles
        detalles_content = [
            [Paragraph(f"<b>Item #{i}</b> - {item.marca}", styles['Heading3'])],
            [Spacer(1, 5)],
            [Paragraph("<b>Elemento:</b>", style_label), Paragraph(item.get_elemento_display(), style_value)],
            [Paragraph("<b>Variedad:</b>", style_label), Paragraph(item.variedad, style_value)],
            [Paragraph("<b>Cantidad:</b>", style_label), Paragraph(str(item.cantidad), style_value)],
            [Paragraph("<b>Medidas:</b>", style_label), Paragraph(f"{item.ancho} x {item.alto} cm", style_value)],
            [Paragraph("<b>Forma:</b>", style_label), Paragraph(item.get_forma_display(), style_value)],
            [Paragraph("<b>Papel:</b>", style_label), Paragraph(item.papel, style_value)],
            [Paragraph("<b>Grado Alc.:</b>", style_label), Paragraph(str(item.grado_alcoholico or '-'), style_value)],
            [Paragraph("<b>Cód. Cliente:</b>", style_label), Paragraph(str(item.codigo_cliente or '-'), style_value)],
            [Paragraph("<b>Año:</b>", style_label), Paragraph(str(item.anio or '-'), style_value)],
            [Paragraph("<b>Cont. Neto:</b>", style_label), Paragraph(str(item.contenido_neto or '-'), style_value)],
            [Paragraph("<b>Barniz:</b>", style_label), Paragraph(item.get_barniz_display() or '-', style_value)],
            [Paragraph("<b>Terminaciones:</b>", style_label), Paragraph(str_terminaciones, style_value)],
            [Paragraph("<b>Observaciones:</b>", style_label), Paragraph(item.observaciones or '-', style_value)],
        ]
        
        # Crear tabla interna para detalles para alinear etiquetas y valores
        detalles_table = Table(detalles_content, colWidths=[100, 200])
        detalles_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('SPAN', (0,0), (1,0)), # Span header
            ('SPAN', (0,1), (1,1)), # Span spacer
        ]))

        # Columna de Imagen
        imagen_content = []
        if item.archivo_muestra:
            try:
                img_path = item.archivo_muestra.path
                # Mantener aspect ratio aprox
                img = Image(img_path, width=180, height=180, kind='proportional') 
                imagen_content.append(img)
            except Exception:
                imagen_content.append(Paragraph("Error cargando imagen", style_value))
        else:
            imagen_content.append(Paragraph("Sin muestra adjunta", style_value))

        # Tabla contenedora del Item (Card)
        item_data = [[detalles_table, imagen_content]]
        item_table = Table(item_data, colWidths=[320, 200])
        item_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#DDDDDD')),
            ('ROUNDEDCORNERS', [10, 10, 10, 10]), # Si reportlab lo soporta, sino ignora
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FAFAFA')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
            ('LEFTPADDING', (0,0), (-1,-1), 15),
            ('RIGHTPADDING', (0,0), (-1,-1), 15),
            ('ALIGN', (1,0), (1,0), 'CENTER'), # Centrar imagen
        ]))
        
        elements.append(item_table)
        elements.append(Spacer(1, 15))

    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

@login_required
def editar_orden(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    
    # Seguridad: Un cliente solo puede editar sus propias órdenes
    user = request.user
    if not (user.is_superuser or user.is_staff):
        if orden.cliente.user != user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permiso para editar esta orden.")
            
    if request.method == 'POST':
        form = OrdenCompraForm(request.POST, instance=orden, user=request.user)
        formset = ItemOrdenFormSet(request.POST, request.FILES, instance=orden)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            return redirect('lista_ordenes')
    else:
        form = OrdenCompraForm(instance=orden, user=request.user)
        formset = ItemOrdenFormSet(instance=orden)
    
    return render(request, 'ordenes_trabajo/form_orden.html', {
        'form': form,
        'formset': formset,
        'titulo': f'Editar Orden N°{orden.numero}'
    })

class OrdenDeleteView(LoginRequiredMixin, DeleteView):
    model = OrdenCompra
    template_name = 'ordenes_trabajo/confirmar_borrado.html'
    success_url = reverse_lazy('lista_ordenes')

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not (user.is_superuser or user.is_staff):
            queryset = queryset.filter(cliente__user=user)
        return queryset

    def form_valid(self, form):
        self.object = self.get_object()
        self.object.active = False
        self.object.save()
        return redirect(self.success_url)

@login_required
def generar_pdf(request, pk):
    orden = get_object_or_404(OrdenCompra, pk=pk)
    
    # Seguridad: Un cliente solo puede generar el PDF de sus propias órdenes
    user = request.user
    if not (user.is_superuser or user.is_staff):
        if orden.cliente.user != user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permiso para ver esta orden.")
            
    pdf_content = _generate_pdf_bytes(orden)
    
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="orden_{orden.numero}.pdf"'
    
    return response

from .forms import OrdenCompraForm, ItemOrdenFormSet, ClienteForm, RegistroUsuarioForm, CustomUserCreationForm, AdminPasswordChangeForm, UserUpdateForm
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import TemplateView
from django.db.models.functions import TruncMonth
from django.db.models import Count

class EstadisticasView(LoginRequiredMixin, OrdenesGroupRequiredMixin, TemplateView):
    template_name = 'ordenes_trabajo/estadisticas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Base Queryset
        queryset = OrdenCompra.objects.filter(active=True)
        
        # Filter by Client (if not admin, force own client)
        if not (user.is_superuser or user.is_staff):
            queryset = queryset.filter(cliente__user=user)
        else:
            # Admin can filter by specific client
            cliente_id = self.request.GET.get('cliente_id')
            if cliente_id:
                queryset = queryset.filter(cliente_id=cliente_id)
            context['clientes'] = Cliente.objects.all()

        # Calculate Monthly Stats
        stats = queryset.annotate(month=TruncMonth('fecha_creacion')) \
                        .values('month') \
                        .annotate(total=Count('id')) \
                        .order_by('-month')
        
        context['stats'] = stats
        return context



# --- Usuario Views ---
from django.contrib.auth.models import User

class UsuarioListView(LoginRequiredMixin, SuperUserRequiredMixin, ListView):
    model = User
    template_name = 'ordenes_trabajo/lista_usuarios.html'
    context_object_name = 'usuarios'
    ordering = ['username']

class UsuarioCreateView(LoginRequiredMixin, SuperUserRequiredMixin, CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'ordenes_trabajo/form_usuario.html'
    success_url = reverse_lazy('lista_usuarios')
    extra_context = {'titulo': 'Nuevo Usuario'}

class UsuarioPasswordChangeView(LoginRequiredMixin, SuperUserRequiredMixin, FormView):
    form_class = AdminPasswordChangeForm
    template_name = 'ordenes_trabajo/cambiar_password_usuario.html'
    success_url = reverse_lazy('lista_usuarios')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.user_obj = get_object_or_404(User, pk=self.kwargs['pk'])
        kwargs['user'] = self.user_obj
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Cambiar Contraseña de {self.user_obj.username}'
        return context

class UsuarioUpdateView(LoginRequiredMixin, SuperUserRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'ordenes_trabajo/form_usuario.html'
    success_url = reverse_lazy('lista_usuarios')
    extra_context = {'titulo': 'Editar Usuario'}

class UsuarioDeleteView(LoginRequiredMixin, SuperUserRequiredMixin, DeleteView):
    model = User
    template_name = 'ordenes_trabajo/confirmar_borrado_usuario.html'
    success_url = reverse_lazy('lista_usuarios')
