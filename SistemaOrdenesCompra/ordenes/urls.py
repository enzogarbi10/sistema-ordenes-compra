from django.urls import path
from . import views

urlpatterns = [
    # Ordenes
    path('', views.OrdenListView.as_view(), name='lista_ordenes'),
    path('nueva/', views.crear_orden, name='crear_orden'),
    path('editar/<int:pk>/', views.editar_orden, name='editar_orden'),
    path('borrar/<int:pk>/', views.OrdenDeleteView.as_view(), name='borrar_orden'),
    path('orden/<int:pk>/pdf/', views.generar_pdf, name='generar_pdf'),
    path('estadisticas/', views.EstadisticasView.as_view(), name='estadisticas'),
    
    # Clientes
    path('clientes/', views.ClienteListView.as_view(), name='lista_clientes'),
    path('clientes/nuevo/', views.ClienteCreateView.as_view(), name='crear_cliente'),
    path('clientes/editar/<int:pk>/', views.ClienteUpdateView.as_view(), name='editar_cliente'),
    path('clientes/borrar/<int:pk>/', views.ClienteDeleteView.as_view(), name='borrar_cliente'),

    # Usuarios
    path('usuarios/', views.UsuarioListView.as_view(), name='lista_usuarios'),
    path('usuarios/crear/', views.UsuarioCreateView.as_view(), name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', views.UsuarioUpdateView.as_view(), name='editar_usuario'),
    path('usuarios/borrar/<int:pk>/', views.UsuarioDeleteView.as_view(), name='borrar_usuario'),
    path('usuarios/<int:pk>/password/', views.UsuarioPasswordChangeView.as_view(), name='cambiar_password_usuario'),
]
