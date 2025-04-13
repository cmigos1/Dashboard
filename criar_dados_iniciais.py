import os
import django
import datetime
from django.utils import timezone

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vacinas_dashboard.settings')
django.setup()

# Importar os modelos após a configuração do Django
from vacinas.models import TipoVacina, Ampola, Vacinacao
from grupos.models import Grupo, Pessoa, Notificacao
from dashboard.models import EstatisticaDiaria

def criar_tipos_vacina():
    print("Criando tipos de vacina...")
    tipos = [
        {
            'nome': 'CoronaVac',
            'descricao': 'Vacina contra COVID-19 produzida pelo Instituto Butantan',
            'tempo_validade_horas': 8
        },
        {
            'nome': 'Pfizer',
            'descricao': 'Vacina contra COVID-19 produzida pela Pfizer/BioNTech',
            'tempo_validade_horas': 6
        },
        {
            'nome': 'Influenza',
            'descricao': 'Vacina contra Influenza (gripe)',
            'tempo_validade_horas': 24
        },
        {
            'nome': 'Tríplice Viral',
            'descricao': 'Vacina contra Sarampo, Caxumba e Rubéola',
            'tempo_validade_horas': 8
        }
    ]
    
    for tipo in tipos:
        TipoVacina.objects.get_or_create(
            nome=tipo['nome'],
            defaults={
                'descricao': tipo['descricao'],
                'tempo_validade_horas': tipo['tempo_validade_horas']
            }
        )

def criar_grupos():
    print("Criando grupos...")
    grupos = [
        {
            'tipo': 'idoso',
            'nome': 'Idosos acima de 60 anos',
            'descricao': 'Pessoas com 60 anos ou mais'
        },
        {
            'tipo': 'risco',
            'nome': 'Pessoas com comorbidades',
            'descricao': 'Pessoas com doenças crônicas, imunossuprimidas'
        },
        {
            'tipo': 'crianca',
            'nome': 'Crianças até 12 anos',
            'descricao': 'Crianças com idade inferior a 12 anos'
        }
    ]
    
    for grupo in grupos:
        Grupo.objects.get_or_create(
            tipo=grupo['tipo'],
            nome=grupo['nome'],
            defaults={
                'descricao': grupo['descricao']
            }
        )

def criar_pessoas():
    print("Criando pessoas...")
    
    # Buscando grupos
    grupo_idoso = Grupo.objects.get(tipo='idoso')
    grupo_risco = Grupo.objects.get(tipo='risco')
    grupo_crianca = Grupo.objects.get(tipo='crianca')
    
    pessoas = [
        {
            'nome': 'Maria Silva',
            'data_nascimento': '1950-05-10',
            'cpf': '123.456.789-00',
            'telefone': '11999887766',
            'email': 'maria@example.com',
            'grupos': [grupo_idoso]
        },
        {
            'nome': 'João Oliveira',
            'data_nascimento': '1945-08-15',
            'cpf': '987.654.321-00',
            'telefone': '11988776655',
            'email': 'joao@example.com',
            'grupos': [grupo_idoso, grupo_risco]
        },
        {
            'nome': 'Ana Souza',
            'data_nascimento': '1985-03-20',
            'cpf': '456.789.123-00',
            'telefone': '11977665544',
            'email': 'ana@example.com',
            'grupos': [grupo_risco]
        },
        {
            'nome': 'Lucas Pereira',
            'data_nascimento': '2015-11-05',
            'cpf': '789.123.456-00',
            'telefone': '11966554433',
            'email': 'responsavel_lucas@example.com',
            'grupos': [grupo_crianca]
        },
        {
            'nome': 'Julia Santos',
            'data_nascimento': '2018-07-12',
            'cpf': '321.654.987-00',
            'telefone': '11955443322',
            'email': 'responsavel_julia@example.com',
            'grupos': [grupo_crianca]
        }
    ]
    
    for p in pessoas:
        pessoa, created = Pessoa.objects.get_or_create(
            cpf=p['cpf'],
            defaults={
                'nome': p['nome'],
                'data_nascimento': datetime.datetime.strptime(p['data_nascimento'], '%Y-%m-%d').date(),
                'telefone': p['telefone'],
                'email': p['email']
            }
        )
        
        if created:
            pessoa.grupos.set(p['grupos'])

def criar_ampolas():
    print("Criando ampolas...")
    # Buscar tipos de vacina
    tipos_vacina = TipoVacina.objects.all()
    
    # Data atual
    agora = timezone.now()
    
    # Criar ampolas com diferentes estados
    for tipo in tipos_vacina:
        # Ampola aberta recentemente
        Ampola.objects.create(
            tipo_vacina=tipo,
            data_abertura=agora - datetime.timedelta(hours=1),
            doses_iniciais=10,
            doses_restantes=8
        )
        
        # Ampola prestes a vencer
        ampola_vencendo = Ampola.objects.create(
            tipo_vacina=tipo,
            data_abertura=agora - datetime.timedelta(hours=tipo.tempo_validade_horas - 2),
            doses_iniciais=10,
            doses_restantes=5
        )
        
        # Ampola já vencida
        Ampola.objects.create(
            tipo_vacina=tipo,
            data_abertura=agora - datetime.timedelta(hours=tipo.tempo_validade_horas + 5),
            doses_iniciais=10,
            doses_restantes=3
        )

def criar_estatisticas():
    print("Criando estatísticas...")
    # Atualizar estatísticas para os últimos 7 dias
    hoje = timezone.now().date()
    
    for i in range(7):
        data = hoje - datetime.timedelta(days=i)
        estatistica, _ = EstatisticaDiaria.objects.get_or_create(data=data)
        
        # Valores simulados
        estatistica.total_ampolas_abertas = 5 - i if i <= 5 else 0
        estatistica.total_ampolas_vencidas = 2 - i if i <= 2 else 0
        estatistica.total_vacinacoes = 15 - (i * 2) if i <= 7 else 0
        estatistica.total_notificacoes_enviadas = 8 - i if i <= 8 else 0
        estatistica.save()

if __name__ == '__main__':
    criar_tipos_vacina()
    criar_grupos()
    criar_pessoas()
    criar_ampolas()
    criar_estatisticas()
    
    print("Dados iniciais criados com sucesso!") 