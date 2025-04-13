from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastrar-ampola/', views.cadastrar_ampola, name='cadastrar_ampola'),
    path('enviar-notificacao/', views.enviar_notificacao, name='enviar_notificacao'),
    path('log-notificacoes/', views.log_notificacoes, name='log_notificacoes'),
    path('utilizar-dose/', views.utilizar_dose, name='utilizar_dose'),
    path('relatorio/', views.relatorio, name='relatorio'),
] 