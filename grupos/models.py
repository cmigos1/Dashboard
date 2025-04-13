from django.db import models
from django.utils import timezone

class Grupo(models.Model):
    TIPO_CHOICES = (
        ('idoso', 'Idoso'),
        ('risco', 'Grupo de Risco'),
        ('crianca', 'Criança'),
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()}: {self.nome}"
    
    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"

class Pessoa(models.Model):
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    grupos = models.ManyToManyField(Grupo, related_name="pessoas")
    
    @property
    def idade(self):
        today = timezone.now().date()
        return today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))
    
    @property
    def is_idoso(self):
        return self.idade >= 60
    
    @property
    def is_crianca(self):
        return self.idade < 12
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas"

class Notificacao(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name="notificacoes")
    tipo_vacina = models.ForeignKey('vacinas.TipoVacina', on_delete=models.CASCADE)
    data_envio = models.DateTimeField(default=timezone.now)
    mensagem = models.TextField()
    enviada = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Notificação para {self.pessoa.nome} - {self.data_envio.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
