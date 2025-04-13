from django.db import models
from django.utils import timezone
import datetime

class EstatisticaDiaria(models.Model):
    data = models.DateField(unique=True)
    total_ampolas_abertas = models.IntegerField(default=0)
    total_ampolas_vencidas = models.IntegerField(default=0)
    total_vacinacoes = models.IntegerField(default=0)
    total_notificacoes_enviadas = models.IntegerField(default=0)
    
    @classmethod
    def atualizar_ou_criar_hoje(cls):
        hoje = timezone.now().date()
        obj, criado = cls.objects.get_or_create(data=hoje)
        
        # Importações locais para evitar problemas de dependência circular
        from vacinas.models import Ampola, Vacinacao
        from grupos.models import Notificacao
        
        # Contagem de ampolas abertas hoje
        ampolas_hoje = Ampola.objects.filter(data_abertura__date=hoje).count()
        
        # Contagem de ampolas vencidas hoje
        ampolas_vencidas = Ampola.objects.filter(data_vencimento__date=hoje).count()
        
        # Contagem de vacinações hoje
        vacinacoes_hoje = Vacinacao.objects.filter(data__date=hoje).count()
        
        # Contagem de notificações enviadas hoje
        notificacoes_hoje = Notificacao.objects.filter(data_envio__date=hoje, enviada=True).count()
        
        # Atualiza os valores
        obj.total_ampolas_abertas = ampolas_hoje
        obj.total_ampolas_vencidas = ampolas_vencidas
        obj.total_vacinacoes = vacinacoes_hoje
        obj.total_notificacoes_enviadas = notificacoes_hoje
        obj.save()
        
        return obj
    
    def __str__(self):
        return f"Estatísticas de {self.data.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name = "Estatística Diária"
        verbose_name_plural = "Estatísticas Diárias"
