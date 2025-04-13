from django.contrib import admin
from .models import Grupo, Pessoa, Notificacao

@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'descricao')
    list_filter = ('tipo',)
    search_fields = ('nome', 'descricao')

@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'idade', 'is_idoso', 'is_crianca')
    list_filter = ('grupos',)
    search_fields = ('nome', 'cpf', 'telefone')
    filter_horizontal = ('grupos',)

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'tipo_vacina', 'data_envio', 'enviada')
    list_filter = ('enviada', 'data_envio', 'tipo_vacina')
    search_fields = ('pessoa__nome',)
