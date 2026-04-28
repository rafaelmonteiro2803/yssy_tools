# YSSY · Dynamics 365 CRM Dashboard

Dashboard web para visualização de oportunidades, contas e contatos do Microsoft Dynamics 365 da YSSY.

## Stack
- **Backend**: Python / Flask
- **Autenticação**: OAuth2 Client Credentials (Azure AD)
- **Deploy**: Render (via GitHub)

## Deploy no Render

### 1. Suba o repositório no GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/seu-usuario/dynamics-yssy.git
git push -u origin main
```

### 2. Configure no Render
- New → Web Service → conectar ao repo
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Runtime**: Python 3

### 3. Variáveis de ambiente no Render
```
TENANT_ID     = 4819c0ac-2467-422d-a1fd-618e47b30a45
CLIENT_ID     = 63d43218-3c42-4c04-8771-7259ae9cd58a
CLIENT_SECRET = <seu secret>
DYNAMICS_URL  = https://yssycrm.crm2.dynamics.com
API_VERSION   = v9.2
```

## Desenvolvimento local
```bash
pip install -r requirements.txt
cp .env.example .env   # editar com seu CLIENT_SECRET
python app.py
# http://localhost:5000
```

## Pré-requisitos no Azure AD
O app precisa das permissões de aplicação (não delegadas):
- `Dynamics CRM → user_impersonation` (ou `Dynamics 365 Business Central`)
- Um **Application User** criado no Dynamics com papel de segurança adequado
