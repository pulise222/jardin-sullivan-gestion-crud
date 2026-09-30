#actividades/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('curso/<int:curso_id>/', views.actividades_por_curso),
    path('curso/<int:curso_id>/crear/', views.crear_actividad_en_curso),

    path('<int:actividad_id>/detalle/', views.detalle_actividad),
    path('<int:actividad_id>/', views.actividad_update_delete),

    path('actividad/<int:actividad_id>/entregas/', views.entregas_por_actividad),
    path('entrega/<int:actividad_estudiante_id>/', views.actualizar_entrega),
    path('entrega/<int:actividad_estudiante_id>/archivo/', views.subir_entregable),

    path('curso/<int:curso_id>/matriz/', views.matriz_calificaciones_curso),
    path('estudiante/<int:estudiante_id>/', views.entregas_por_estudiante, name='entregas-por-estudiante'),

    # NUEVO: descarga forzada
    path('entrega/<int:actividad_estudiante_id>/download/', views.descargar_entregable, name='descargar-entregable'),
]
