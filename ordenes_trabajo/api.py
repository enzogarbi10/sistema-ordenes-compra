from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cliente
from django.conf import settings
from rest_framework.permissions import BasePermission

class HasSyncSecretKey(BasePermission):
    def has_permission(self, request, view):
        # We check for a special header HTTP_X_SYNC_SECRET
        secret = request.META.get('HTTP_X_SYNC_SECRET')
        # Si no lo encuentra, busca en request.headers por si acaso
        if not secret:
            secret = request.headers.get('X-Sync-Secret')
        expected_secret = getattr(settings, 'SYNC_SECRET_KEY', 'default-insecure-sync-key-123')
        return secret == expected_secret

class SincronizarClientesAPI(APIView):
    permission_classes = [HasSyncSecretKey]

    def post(self, request):
        """
        Espera una lista de nombres de clientes.
        Formato JSON: 
        {
            "clientes": ["Cliente 1", "Cliente 2", "Cliente 3"]
        }
        """
        clientes_data = request.data.get('clientes', [])
        
        if not isinstance(clientes_data, list):
            return Response({"error": "Formato inválido. Se esperaba una lista en 'clientes'."}, status=status.HTTP_400_BAD_REQUEST)
        
        nuevos = 0
        actualizados = 0
        
        # Opcional: Para evitar borrar clientes que tengan ordenes asociadas,
        # lo más seguro es hacer un "update or create".
        for data in clientes_data:
            nombre = data.get('nombre', '')
            if not nombre:
                continue
                
            obj, created = Cliente.objects.get_or_create(nombre=nombre)
            
            # Update additional fields
            obj.codigo = data.get('codigo', obj.codigo)
            obj.direccion = data.get('direccion', obj.direccion)
            obj.localidad = data.get('localidad', obj.localidad)
            obj.cuit = data.get('cuit', obj.cuit)
            obj.telefono = data.get('telefono', obj.telefono)
            obj.contacto = data.get('contacto', obj.contacto)
            obj.estado = data.get('estado', obj.estado)
            obj.save()
            
            if created:
                nuevos += 1
            else:
                actualizados += 1
                
        return Response({
            "mensaje": "Sincronización exitosa",
            "nuevos_creados": nuevos,
            "ya_existentes": actualizados,
            "total_recibidos": len(clientes_data)
        }, status=status.HTTP_200_OK)
