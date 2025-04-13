from django.db import models
from django.utils import timezone
import datetime

class TipoVacina(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    tempo_validade_horas = models.IntegerField(help_text="Tempo de validade em horas após a abertura da ampola")
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Tipo de Vacina"
        verbose_name_plural = "Tipos de Vacinas"

class Ampola(models.Model):
    tipo_vacina = models.ForeignKey(TipoVacina, on_delete=models.CASCADE, related_name="ampolas")
    data_abertura = models.DateTimeField(default=timezone.now)
    data_vencimento = models.DateTimeField()
    doses_iniciais = models.IntegerField(default=10)
    doses_restantes = models.IntegerField(default=10)
    
    def save(self, *args, **kwargs):
        # Se for um novo registro, calcula a data de vencimento
        if not self.id:
            self.data_vencimento = self.data_abertura + datetime.timedelta(hours=self.tipo_vacina.tempo_validade_horas)
        super().save(*args, **kwargs)
    
    @property
    def vencida(self):
        return timezone.now() > self.data_vencimento
    
    @property
    def porcentagem_doses_usadas(self):
        if self.doses_iniciais == 0:
            return 0
        return ((self.doses_iniciais - self.doses_restantes) / self.doses_iniciais) * 100
    
    def __str__(self):
        return f"{self.tipo_vacina.nome} - {self.data_abertura.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        verbose_name = "Ampola"
        verbose_name_plural = "Ampolas"

class Vacinacao(models.Model):
    ampola = models.ForeignKey(Ampola, on_delete=models.CASCADE, related_name="vacinacoes")
    pessoa = models.CharField(max_length=100)
    data = models.DateTimeField(default=timezone.now)
    dose = models.IntegerField(default=1)
    
    def save(self, *args, **kwargs):
        # Ao registrar uma vacinação, diminui a quantidade de doses restantes
        self.ampola.doses_restantes -= 1
        self.ampola.save()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Vacinação de {self.pessoa} - {self.data.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        verbose_name = "Vacinação"
        verbose_name_plural = "Vacinações"
