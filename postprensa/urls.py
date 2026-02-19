from django.urls import path
from . import views

urlpatterns = [
    path('', views.ControlListView.as_view(), name='lista_controles_postprensa'),
    path('crear/', views.crear_control, name='crear_control_postprensa'),
    path('control/<int:pk>/editar/', views.editar_control, name='editar_control_postprensa'),
    path('control/<int:pk>/eliminar/', views.eliminar_control, name='eliminar_control_postprensa'),
    path('estadisticas/', views.EstadisticasPostprensaView.as_view(), name='estadisticas_postprensa'),
    path('estadisticas/pdf/', views.descargar_estadisticas_pdf, name='descargar_estadisticas_pdf'),
    path('control/<int:pk>/pdf/', views.control_pdf, name='control_pdf'),
    # AJAX - Maquinistas
    path('api/agregar-maquinista/', views.agregar_maquinista, name='agregar_maquinista'),
    path('api/editar-maquinista/<int:pk>/', views.editar_maquinista, name='editar_maquinista'),
    path('api/eliminar-maquinista/<int:pk>/', views.eliminar_maquinista, name='eliminar_maquinista'),
    # AJAX - Operarios
    path('api/agregar-operario/', views.agregar_operario, name='agregar_operario'),
    path('api/editar-operario/<int:pk>/', views.editar_operario, name='editar_operario'),
    path('api/eliminar-operario/<int:pk>/', views.eliminar_operario, name='eliminar_operario'),
    # AJAX - Tipos de Defecto
    path('api/agregar-tipo-defecto/', views.agregar_tipo_defecto, name='agregar_tipo_defecto'),
    path('api/editar-tipo-defecto/<int:pk>/', views.editar_tipo_defecto, name='editar_tipo_defecto'),
    path('api/eliminar-tipo-defecto/<int:pk>/', views.eliminar_tipo_defecto, name='eliminar_tipo_defecto'),
    # AJAX - Opciones de Defecto
    path('api/opciones-defecto/<int:tipo_id>/', views.obtener_opciones_defecto, name='obtener_opciones_defecto'),
    path('api/agregar-opcion-defecto/', views.agregar_opcion_defecto, name='agregar_opcion_defecto'),
    path('api/editar-opcion-defecto/<int:pk>/', views.editar_opcion_defecto, name='editar_opcion_defecto'),
    path('api/eliminar-opcion-defecto/<int:pk>/', views.eliminar_opcion_defecto, name='eliminar_opcion_defecto'),
    # AJAX - Clientes
    path('api/agregar-cliente/', views.agregar_cliente, name='agregar_cliente'),
    path('api/editar-cliente/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('api/eliminar-cliente/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),
]
