import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import Cliente


def _check_secret(request):
    """Verifica el header X-Sync-Secret para autorizar la petición."""
    secret = request.META.get('HTTP_X_SYNC_SECRET') or request.headers.get('X-Sync-Secret')
    expected = getattr(settings, 'SYNC_SECRET_KEY', 'default-insecure-sync-key-123')
    return secret == expected


@csrf_exempt
@require_http_methods(["POST"])
def sincronizar_clientes(request):
    """
    Sincroniza clientes enviados como JSON.
    Formato: {"clientes": [{"nombre": "...", "codigo": "...", ...}]}
    Requiere header: X-Sync-Secret: <clave>
    """
    if not _check_secret(request):
        return JsonResponse({"error": "No autorizado"}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    clientes_data = data.get('clientes', [])

    if not isinstance(clientes_data, list):
        return JsonResponse({"error": "Formato inválido. Se esperaba una lista en 'clientes'."}, status=400)

    nuevos = 0
    actualizados = 0

    for item in clientes_data:
        nombre = item.get('nombre', '')
        if not nombre:
            continue

        obj, created = Cliente.objects.get_or_create(nombre=nombre)
        obj.codigo = item.get('codigo', obj.codigo)
        obj.direccion = item.get('direccion', obj.direccion)
        obj.localidad = item.get('localidad', obj.localidad)
        obj.cuit = item.get('cuit', obj.cuit)
        obj.telefono = item.get('telefono', obj.telefono)
        obj.contacto = item.get('contacto', obj.contacto)
        obj.estado = item.get('estado', obj.estado)
        obj.save()

        if created:
            nuevos += 1
        else:
            actualizados += 1

    return JsonResponse({
        "mensaje": "Sincronización exitosa",
        "nuevos_creados": nuevos,
        "ya_existentes": actualizados,
        "total_recibidos": len(clientes_data)
    }, status=200)
