from django.urls import path
from . import views

urlpatterns = [
    path('asistencias/cpm/<int:cpm_id>/', views.asistencia_por_cpm_y_fecha),
    # única definición de upsert para evitar duplicidad
    path('asistencias/cpm/<int:cpm_id>/upsert/', views.upsert_asistencia_cpm, name='upsert-asistencia-cpm'),
    path('asistencias/cpm/<int:cpm_id>/fechas/', views.fechas_con_asistencia),
    path('asistencias/cpm/<int:cpm_id>/resumen/', views.resumen_asistencia_cpm, name='resumen-asistencia-cpm'),
]
