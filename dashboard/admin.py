from django.contrib import admin
from .models import EstatisticaDiaria

@admin.register(EstatisticaDiaria)
class EstatisticaDiariaAdmin(admin.ModelAdmin):
    list_display = ('data', 'total_ampolas_abertas', 'total_ampolas_vencidas', 'total_vacinacoes', 'total_notificacoes_enviadas')
    readonly_fields = ('data', 'total_ampolas_abertas', 'total_ampolas_vencidas', 'total_vacinacoes', 'total_notificacoes_enviadas')
    
    def has_add_permission(self, request):
        # Impede a criação manual de estatísticas
        return False
