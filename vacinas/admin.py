from django.contrib import admin
from .models import TipoVacina, Ampola, Vacinacao

@admin.register(TipoVacina)
class TipoVacinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tempo_validade_horas')
    search_fields = ('nome',)

@admin.register(Ampola)
class AmpolaAdmin(admin.ModelAdmin):
    list_display = ('tipo_vacina', 'data_abertura', 'data_vencimento', 'doses_iniciais', 'doses_restantes', 'vencida')
    list_filter = ('tipo_vacina', 'data_abertura')
    search_fields = ('tipo_vacina__nome',)
    readonly_fields = ('data_vencimento',)

@admin.register(Vacinacao)
class VacinacaoAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'ampola', 'data', 'dose')
    list_filter = ('data', 'ampola__tipo_vacina')
    search_fields = ('pessoa',)
