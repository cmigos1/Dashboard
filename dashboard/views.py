from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import datetime
import json
import requests
from django.conf import settings
from django.urls import reverse
import urllib.parse
from vacinas.models import TipoVacina, Ampola, Vacinacao
from grupos.models import Grupo, Pessoa, Notificacao
from .models import EstatisticaDiaria
from django.db import models

def index(request):
    # Dados para o bloco 1: Cadastro de ampolas abertas
    tipos_vacina = TipoVacina.objects.all()
    ampolas_recentes = Ampola.objects.all().order_by('-data_abertura')[:5]
    
    # Dados para o bloco 2: Contador de grupos
    grupos_idosos = Pessoa.objects.filter(grupos__tipo='idoso').count()
    grupos_risco = Pessoa.objects.filter(grupos__tipo='risco').count()
    grupos_criancas = Pessoa.objects.filter(grupos__tipo='crianca').count()
    grupos_gestantes = Pessoa.objects.filter(grupos__tipo='gestante').count()
    grupos_tea = Pessoa.objects.filter(grupos__tipo='tea').count()
    
    # Buscar ampolas prestes a vencer (nas próximas 24 horas)
    agora = timezone.now()
    proximas_24h = agora + datetime.timedelta(hours=24)
    ampolas_prestes_vencer = Ampola.objects.filter(
        data_vencimento__gt=agora,
        data_vencimento__lt=proximas_24h,
        doses_restantes__gt=0
    ).order_by('data_vencimento')
    
    # Dados para o bloco 3: Monitoramento de gráficos
    ultimos_7_dias = []
    hoje = timezone.now().date()
    
    for i in range(6, -1, -1):
        data = hoje - datetime.timedelta(days=i)
        estatistica, _ = EstatisticaDiaria.objects.get_or_create(data=data)
        ultimos_7_dias.append({
            'data': data.strftime('%d/%m'),
            'ampolas_abertas': estatistica.total_ampolas_abertas,
            'ampolas_vencidas': estatistica.total_ampolas_vencidas,
            'vacinacoes': estatistica.total_vacinacoes,
            'notificacoes': estatistica.total_notificacoes_enviadas
        })
    
    # Obter notificações recentes
    notificacoes_recentes = Notificacao.objects.all().order_by('-data_envio')[:10]
    
    context = {
        'tipos_vacina': tipos_vacina,
        'ampolas_recentes': ampolas_recentes,
        'grupos_idosos': grupos_idosos,
        'grupos_risco': grupos_risco,
        'grupos_criancas': grupos_criancas,
        'grupos_gestantes': grupos_gestantes,
        'grupos_tea': grupos_tea,
        'ampolas_prestes_vencer': ampolas_prestes_vencer,
        'ultimos_7_dias': json.dumps(ultimos_7_dias),
        'notificacoes_recentes': notificacoes_recentes
    }
    
    return render(request, 'dashboard/index.html', context)

def log_notificacoes(request):
    """View para exibir o log de notificações"""
    notificacoes = Notificacao.objects.all().order_by('-data_envio')
    
    # Filtrar por grupo se especificado
    grupo_tipo = request.GET.get('grupo')
    if grupo_tipo:
        notificacoes = notificacoes.filter(pessoa__grupos__tipo=grupo_tipo)
    
    # Filtrar por data
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if data_inicio:
        data_inicio = datetime.datetime.strptime(data_inicio, '%Y-%m-%d').date()
        notificacoes = notificacoes.filter(data_envio__date__gte=data_inicio)
    
    if data_fim:
        data_fim = datetime.datetime.strptime(data_fim, '%Y-%m-%d').date()
        notificacoes = notificacoes.filter(data_envio__date__lte=data_fim)
    
    context = {
        'notificacoes': notificacoes,
        'grupos': Grupo.objects.all()
    }
    
    return render(request, 'dashboard/log_notificacoes.html', context)

@login_required
def cadastrar_ampola(request):
    if request.method == 'POST':
        tipo_vacina_id = request.POST.get('tipo_vacina')
        doses_iniciais = int(request.POST.get('doses_iniciais', 10))
        tipo_duracao = request.POST.get('tipo_duracao', 'curta')
        
        tipo_vacina = TipoVacina.objects.get(id=tipo_vacina_id)
        
        # Data de abertura é sempre o momento atual
        data_abertura = timezone.now()
        
        # Criar nova ampola
        if tipo_duracao == 'longa' and request.POST.get('data_vencimento'):
            # Para longa duração: data de abertura é agora, data de vencimento é fornecida pelo usuário
            from datetime import datetime
            data_vencimento_obj = datetime.strptime(request.POST.get('data_vencimento'), '%Y-%m-%dT%H:%M')
            ampola = Ampola.objects.create(
                tipo_vacina=tipo_vacina,
                doses_iniciais=doses_iniciais,
                doses_restantes=doses_iniciais,
                data_abertura=data_abertura,
                data_vencimento=data_vencimento_obj
            )
        else:
            # Duração curta: usar a hora atual e calcular a validade com horas
            horas_validade = int(request.POST.get('horas_validade', 6))
            
            # Calcular data de vencimento baseada nas horas de validade
            data_vencimento = data_abertura + datetime.timedelta(hours=horas_validade)
            
            ampola = Ampola.objects.create(
                tipo_vacina=tipo_vacina,
                doses_iniciais=doses_iniciais,
                doses_restantes=doses_iniciais,
                data_abertura=data_abertura,
                data_vencimento=data_vencimento
            )
        
        return redirect('dashboard:index')
    
    return redirect('dashboard:index')

@login_required
def enviar_notificacao(request):
    if request.method == 'POST':
        grupo_tipo = request.POST.get('grupo_tipo')
        ampola_id = request.POST.get('ampola_id')
        
        # Buscar a ampola
        ampola = Ampola.objects.get(id=ampola_id)
        
        # Buscar todas as pessoas do grupo selecionado
        if grupo_tipo == 'todos':
            # Todos os grupos
            pessoas = Pessoa.objects.all().distinct()
        elif grupo_tipo == 'idoso':
            pessoas = Pessoa.objects.filter(grupos__tipo='idoso')
        elif grupo_tipo == 'risco':
            pessoas = Pessoa.objects.filter(grupos__tipo='risco')
        elif grupo_tipo == 'crianca':
            pessoas = Pessoa.objects.filter(grupos__tipo='crianca')
        elif grupo_tipo == 'gestante':
            pessoas = Pessoa.objects.filter(grupos__tipo='gestante')
        elif grupo_tipo == 'tea':
            pessoas = Pessoa.objects.filter(grupos__tipo='tea')
        else:
            return JsonResponse({'erro': 'Grupo inválido'}, status=400)

        # Criar notificações e preparar links WhatsApp
        links_whatsapp = []
        notificacoes_enviadas = 0
        
        for pessoa in pessoas:
            # Criar a mensagem
            mensagem = f"Olá {pessoa.nome}, temos doses disponíveis da vacina {ampola.tipo_vacina.nome}. Válida até {ampola.data_vencimento.strftime('%d/%m/%Y %H:%M')}."
            
            # Criar registro de notificação
            notificacao = Notificacao.objects.create(
                pessoa=pessoa,
                tipo_vacina=ampola.tipo_vacina,
                mensagem=mensagem,
                enviada=True  # Marcamos como enviada já que estamos apenas gerando links
            )
            
            # Gerar link do WhatsApp
            telefone_limpo = ''.join(filter(str.isdigit, pessoa.telefone))
            # Adicionar código do país se necessário (Brasil = 55)
            if len(telefone_limpo) == 11 or len(telefone_limpo) == 10:  # DDD + número
                telefone_limpo = '55' + telefone_limpo
                
            mensagem_codificada = urllib.parse.quote(mensagem)
            link_whatsapp = f"https://wa.me/{telefone_limpo}?text={mensagem_codificada}"
            
            links_whatsapp.append({
                'nome': pessoa.nome,
                'telefone': pessoa.telefone,
                'link': link_whatsapp
            })
            
            notificacoes_enviadas += 1
        
        return JsonResponse({
            'sucesso': True,
            'total_envios': notificacoes_enviadas,
            'links_whatsapp': links_whatsapp,
            'mensagem': f"Links gerados para {notificacoes_enviadas} pessoas"
        })
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

def gerar_link_whatsapp(telefone, mensagem):
    """
    Função para gerar link do WhatsApp (wa.me)
    """
    # Remover formatação do telefone (deixar apenas números)
    telefone_limpo = ''.join(filter(str.isdigit, telefone))
    
    # Adicionar código do país se necessário (Brasil = 55)
    if len(telefone_limpo) == 11 or len(telefone_limpo) == 10:  # DDD + número
        telefone_limpo = '55' + telefone_limpo
    
    # Codificar a mensagem para URL
    mensagem_codificada = urllib.parse.quote(mensagem)
    
    # Retornar o link
    return f"https://wa.me/{telefone_limpo}?text={mensagem_codificada}"

@login_required
def utilizar_dose(request):
    """
    View para registrar a utilização de uma dose
    """
    if request.method == 'POST':
        ampola_id = request.POST.get('ampola_id')
        
        try:
            # Buscar a ampola
            ampola = Ampola.objects.get(id=ampola_id)
            
            # Verificar se há doses disponíveis e se não está vencida
            agora = timezone.now()
            if ampola.doses_restantes <= 0:
                return JsonResponse({'sucesso': False, 'erro': 'Não há doses disponíveis nesta ampola'}, status=400)
            
            if ampola.data_vencimento < agora:
                return JsonResponse({'sucesso': False, 'erro': 'Esta ampola está vencida'}, status=400)
            
            # Decrementar a quantidade de doses
            ampola.doses_restantes -= 1
            ampola.save()
            
            # Registrar a vacinação (opcional, podemos expandir para incluir o paciente)
            Vacinacao.objects.create(
                ampola=ampola,
                pessoa="Utilização registrada pelo sistema",
                dose=1
            )
            
            return JsonResponse({
                'sucesso': True, 
                'ampola_id': ampola.id,
                'doses_restantes': ampola.doses_restantes,
                'mensagem': 'Dose utilizada com sucesso'
            })
            
        except Ampola.DoesNotExist:
            return JsonResponse({'sucesso': False, 'erro': 'Ampola não encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'sucesso': False, 'erro': str(e)}, status=500)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)

@login_required
def relatorio(request):
    """
    View para exibir relatórios e estatísticas do sistema
    """
    # Período padrão: últimos 30 dias
    data_fim = timezone.now().date()
    data_inicio = data_fim - datetime.timedelta(days=30)
    
    # Verificar se há filtros de data
    if request.GET.get('data_inicio'):
        data_inicio = datetime.datetime.strptime(request.GET.get('data_inicio'), '%Y-%m-%d').date()
    if request.GET.get('data_fim'):
        data_fim = datetime.datetime.strptime(request.GET.get('data_fim'), '%Y-%m-%d').date()
    
    # Estatísticas gerais
    total_ampolas = Ampola.objects.count()
    ampolas_ativas = Ampola.objects.filter(doses_restantes__gt=0, data_vencimento__gt=timezone.now()).count()
    ampolas_vencidas = Ampola.objects.filter(data_vencimento__lt=timezone.now()).count()
    
    # Estatísticas de doses
    total_doses_iniciais = Ampola.objects.aggregate(total=models.Sum('doses_iniciais'))['total'] or 0
    total_doses_restantes = Ampola.objects.aggregate(total=models.Sum('doses_restantes'))['total'] or 0
    doses_utilizadas = total_doses_iniciais - total_doses_restantes
    
    # Estatísticas de vacinação por período
    vacinacoes_periodo = Vacinacao.objects.filter(
        data__date__gte=data_inicio,
        data__date__lte=data_fim
    ).count()
    
    # Estatísticas de notificações
    notificacoes_enviadas = Notificacao.objects.filter(enviada=True).count()
    notificacoes_periodo = Notificacao.objects.filter(
        data_envio__date__gte=data_inicio,
        data_envio__date__lte=data_fim
    ).count()
    
    # Estatísticas por grupo
    grupos = Grupo.objects.all()
    estatisticas_grupos = []
    
    for grupo in grupos:
        pessoas_grupo = Pessoa.objects.filter(grupos=grupo).count()
        notificacoes_grupo = Notificacao.objects.filter(
            pessoa__grupos=grupo,
            data_envio__date__gte=data_inicio,
            data_envio__date__lte=data_fim
        ).count()
        
        estatisticas_grupos.append({
            'grupo': grupo,
            'pessoas': pessoas_grupo,
            'notificacoes': notificacoes_grupo
        })
    
    # Estatísticas por tipo de vacina
    tipos_vacina = TipoVacina.objects.all()
    estatisticas_vacinas = []
    
    for tipo in tipos_vacina:
        ampolas_tipo = Ampola.objects.filter(tipo_vacina=tipo).count()
        ampolas_ativas_tipo = Ampola.objects.filter(
            tipo_vacina=tipo, 
            doses_restantes__gt=0, 
            data_vencimento__gt=timezone.now()
        ).count()
        
        vacinacoes_tipo = Vacinacao.objects.filter(
            ampola__tipo_vacina=tipo,
            data__date__gte=data_inicio,
            data__date__lte=data_fim
        ).count()
        
        estatisticas_vacinas.append({
            'tipo': tipo,
            'ampolas': ampolas_tipo,
            'ampolas_ativas': ampolas_ativas_tipo,
            'vacinacoes': vacinacoes_tipo
        })
    
    # Dados para gráficos
    ultimos_7_dias = []
    hoje = timezone.now().date()
    
    for i in range(6, -1, -1):
        data = hoje - datetime.timedelta(days=i)
        estatistica, _ = EstatisticaDiaria.objects.get_or_create(data=data)
        
        ultimos_7_dias.append({
            'data': data.strftime('%d/%m'),
            'ampolas_abertas': estatistica.total_ampolas_abertas,
            'ampolas_vencidas': estatistica.total_ampolas_vencidas,
            'vacinacoes': estatistica.total_vacinacoes,
            'notificacoes': estatistica.total_notificacoes_enviadas
        })
    
    context = {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_ampolas': total_ampolas,
        'ampolas_ativas': ampolas_ativas,
        'ampolas_vencidas': ampolas_vencidas,
        'total_doses_iniciais': total_doses_iniciais,
        'total_doses_restantes': total_doses_restantes,
        'doses_utilizadas': doses_utilizadas,
        'vacinacoes_periodo': vacinacoes_periodo,
        'notificacoes_enviadas': notificacoes_enviadas,
        'notificacoes_periodo': notificacoes_periodo,
        'estatisticas_grupos': estatisticas_grupos,
        'estatisticas_vacinas': estatisticas_vacinas,
        'ultimos_7_dias': json.dumps(ultimos_7_dias)
    }
    
    return render(request, 'dashboard/relatorio.html', context)
