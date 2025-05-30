# ImunoDose - Sistema de Gestão de Vacinas

Projeto para HackaMT - Edição Caceres 2024, 
Sistema para cadastro de vacinas, identificação de grupos de risco e integração com o WhatsApp para notificações.

## Funcionalidades

### 1. Cadastro de Ampolas Abertas
- Registro de quando uma ampola foi aberta
- Controle de vencimento com granularidade em horas
- Controle de doses restantes

### 2. Gestão de Grupos Prioritários
- Divisão em 3 grupos: Idosos, Grupos de Risco e Crianças
- Geração de links para envio de mensagens via WhatsApp
- Alerta automático para vacinas prestes a vencer

### 3. Monitoramento com Gráficos
- Acompanhamento de vacinas redistribuídas e vencidas
- Estatísticas diárias de vacinação
- Visualização de tendências ao longo do tempo

### 4. Log de Notificações
- Histórico detalhado de todas as notificações geradas
- Filtros por grupo e data
- Links diretos para envio de mensagens via WhatsApp

## Instalação

### Pré-requisitos
- Python 3.8+
- Pip (gerenciador de pacotes do Python)

### Passo a passo

1. Clone o repositório:
```
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

2. Crie um ambiente virtual:
```
python -m venv venv
```

3. Ative o ambiente virtual:
- No Windows:
```
venv\Scripts\activate
```
- No Linux/Mac:
```
source venv/bin/activate
```

4. Instale as dependências:
```
pip install django djangorestframework django-bootstrap4 matplotlib pandas requests
```

5. Execute as migrações:
```
python manage.py migrate
```

6. Crie um superusuário:
```
python manage.py createsuperuser
```

7. Carregue dados iniciais (opcional):
```
python criar_dados_iniciais.py
```

8. Inicie o servidor:
```
python manage.py runserver
```

9. Acesse o sistema em:
```
http://127.0.0.1:8000/
```

## Configuração do WhatsApp

Para configurar a integração do WhatsApp, adicione o domínio do seu servidor à lista de ALLOWED_HOSTS no arquivo settings.py:

```python
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'seu-dominio.com']
```

## Integração com WhatsApp

O sistema utiliza links diretos do WhatsApp (wa.me) para enviar notificações:

1. Ao selecionar um grupo para notificação, o sistema gera links wa.me para cada pessoa
2. Os links podem ser abertos em uma nova aba para enviar as mensagens individualmente
3. As mensagens já são preenchidas automaticamente com as informações da vacina
4. O sistema mantém um registro de todas as notificações geradas

Exemplo de link gerado:
```
https://wa.me/5511999999999?text=Ol%C3%A1%20Nome%2C%20temos%20doses%20dispon%C3%ADveis...
```

## Tecnologias Utilizadas

- **Backend**: Django, Django REST Framework
- **Frontend**: Bootstrap 5, Chart.js
- **Banco de Dados**: SQLite (padrão)
- **Integração**: Links diretos do WhatsApp (wa.me)

## Estrutura do Projeto

- **dashboard**: App principal com o painel de controle
- **vacinas**: App para gerenciamento de vacinas e ampolas
- **grupos**: App para gerenciamento de grupos prioritários e pessoas 
