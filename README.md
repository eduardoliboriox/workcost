```
# WorkCost (Venttos) — Solicitações, Provisões e KPIs

Aplicação **Fullstack Flask** (MVC) para gestão de **solicitações operacionais** (hora extra / banco de horas / compensação), com:
- **Fluxo de aprovação multinível** (gestor → gerente → controladoria → diretoria → RH)
- **Assinatura/confirmação por funcionário** (senha)
- **Cálculo de provisão** (refeição, transporte, adicional noturno)
- **Dashboards/KPIs** (absenteísmo, clientes ativos, custos, rankings)
- **PWA** (offline + manifest + service worker)
- **Autenticação local + OAuth** (Google / GitHub)

> 🇧🇷 Este README é a referência principal.  
> 🇺🇸 Para versão em inglês, veja `README.EN.md`.

---

## ☁️ Infraestrutura (Railway)

Este projeto roda em **Railway + PostgreSQL** e possui **dois ambientes** separados por branch:

### ✅ Produção
- **Service:** `workcost-venttos-prod`
- **Branch:** `main`
- **DB:** `banco_prod`
- **Domínio:** `workcost.com.br`

### ✅ Desenvolvimento
- **Service:** `workcost-venttos-develop`
- **Branch:** `develop`
- **DB:** `banco_test` *(clone do prod)*
- **Domínio:** *(sem domínio)*

### Deploy seguro (fluxo recomendado)
1. Trabalhar e validar na branch `develop`
2. Se estiver estável, promover para `main`
3. Produção nunca quebra durante uso

---

## 🧱 Arquitetura e Organização (MVC + Services/Repositories)

Estrutura pensada para separar responsabilidades:

- **Routes**
  - `app/routes/pages.py` → páginas HTML (Jinja)
  - `app/routes/api.py` → API REST (JSON)
- **Services** (`app/services/`)
  - Regras de negócio, agregações, cálculos, validações
- **Repositories** (`app/repositories/`)
  - Acesso ao PostgreSQL via SQL (psycopg)
- **Templates/Static**
  - Jinja2 + Bootstrap + JS Vanilla (UI responsiva)

---

## 🗂 Estrutura do Projeto (resumo)

```
├─ .github/
│   └─ workflow/
│         └─ ci.yml
│
├─ app/
│   ├─ __init__.py            # create_app()              
│   ├─ config.py              # Configurações / env
│   ├─ extensions.py          # DB (psycopg)
│   ├─ health.py        
│   │
│   ├─ auth/
│   │   ├─ __init__.py   (vazio)
│   │   ├─ decorators.py
│   │   ├─ models.py
│   │   ├─ profile_repository.py
│   │   ├─ repository.py
│   │   ├─ routes.py
│   │   └─ service.py
│   │
│   ├─ cli/
│   │   ├─ __init__.py
│   │   ├─ employees_code_generator.py
│   │   └─ employees_importer.py
│   │
│   ├─ repositories/          # Acesso ao banco (SQL)
│   │   ├─ __init__.py
│   │   ├─ employees_repository.py
│   │   ├─ lancamentos_repository.py
│   │   ├─ modelos_repository.py     
│   │   ├─ powerbi_service.py
│   │   └─ solicitacoes_repository.py
│   │  
│   ├─ routes/
│   │   ├─ __init__.py
│   │   ├─ api.py             # Rotas REST (JSON)
│   │   └─ pages.py           # Rotas HTML
│   │
│   ├─ services/              # Regras de negócio
│   │   ├─ __init__.py
│   │   ├─ email_service.py
│   │   ├─ employees_service.py
│   │   ├─ lancamentos_service.py
│   │   ├─ modelos_service.py
│   │   ├─ pcp_service.py    
│   │   ├─ powerbi_service.py
│   │   ├─ provisao_service.py
│   │   ├─ provisao_view_service.py
│   │   ├─ relatorios_service.py   
│   │   └─ solicitacoes_service.py
│   │
│   ├─ templates/             # Jinja2
│   │   ├─ auth/
│   │   │   ├─ mobile/
│   │   │   │    └─ login_choice.html
│   │   │   │    └─ login_form.htm
│   │   │   │    └─ register_form.htm
│   │   │   │ 
│   │   │   ├─ forgot_password.html
│   │   │   ├─ login.html   
│   │   │   ├─ myperfil.html   
│   │   │   ├─ register.html
│   │   │   ├─ reset_password.html
│   │   │   ├─ users_admin.html
│   │   │   └─ users_all.html 
│   │   │
│   │   ├─ layouts/
│   │   │   ├─ app.html  
│   │   │   ├─ app_print.html
│   │   │   └─ auth.html
│   │   │
│   │   ├─ legal/
│   │   │   ├─ cookies.html
│   │   │   └─ privacy.html
│   │   │ 
│   │   ├─ dashboard.html  
│   │   ├─ inicio.html
│   │   ├─ lancamento.html 
│   │   ├─ minhasextras.html 
│   │   ├─ offline.html
│   │   ├─ powerbi.html   
│   │   ├─ pedidos.html
│   │   ├─ relatorios.html  
│   │   ├─ solicitacoes-abertas.html
│   │   ├─ solicitacoes-fechadas.html
│   │   ├─ solicitacoes-frequencia.html
│   │   ├─ solicitacoes-provisao.html
│   │   └─ solicitacoes.html
│   │
│   ├─ static/
│   │   ├─ css/
│   │   │   ├─ auth.css  
│   │   │   ├─ legal.css
│   │   │   ├─ powerbi.css   
│   │   │   ├─ provisao.css
│   │   │   ├─ solicitacoes.css
│   │   │   └─ style.css  
│   │   │
│   │   ├─ js/
│   │   │   ├─ cookie-consent.js
│   │   │   ├─ dashboard-live.js   
│   │   │   ├─ document-fit.js
│   │   │   ├─ input-masks.js
│   │   │   ├─ main.js  
│   │   │   ├─ minhasextras.js
│   │   │   ├─ powerbi-live.js
│   │   │   ├─ powerbi.js     
│   │   │   ├─ pwa.js
│   │   │   ├─ register.js
│   │   │   ├─ relatorios.js
│   │   │   ├─ solicitacoes-abertas.js
│   │   │   ├─ solicitacoes-create.js  
│   │   │   ├─ solicitacoes-fechadas.js  
│   │   │   ├─ solicitacoes-frequencia.js
│   │   │   ├─ solicitacoes-mobile.js
│   │   │   ├─ solicitacoes-view.js   
│   │   │   └─ solicitacoes.js
│   │   │
│   │   ├─ images/
│   │   ├─ fonts/inter.woff2
│   │   │
│   │   ├─ manifest.webmanifest
│   │   └─ sw.js
│   │
│   └─ utils/
│        └─ text.py
│
├─ migrations/                # Alembic (ainda não utilizado)
├─ tests/                     # pytest
│
├─ .env                       # NÃO versionar
├─ .gitignore
├─ LICENSE
├─ Procfile                   # Railway
├─ README.EN.md
├─ README.md
├─ pyproject.toml
├─ requirements.txt
├─ run.py                     # Entrypoint
└─ runtime.txt                # Entrypoint
````

> Observação: parte do projeto foi derivada de outro repositório e ainda está em análise para decidir quais arquivos permanecem.

---

## ⚙️ Tecnologias

* **Python 3.12**
* **Flask**
* **Jinja2**
* **PostgreSQL**
* **psycopg**
* **Bootstrap 5**
* **JavaScript (Vanilla)**
* **PWA** (Service Worker + Manifest)
* **Pytest** (estrutura pronta)
* **GitHub Actions** (CI)

---

## 🔐 Variáveis de ambiente (obrigatórias)

Crie um `.env` na raiz (NÃO versionar):

```env
# App
ENVIRONMENT=development
SECRET_KEY=change-me
BASE_URL=http://127.0.0.1:5000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/workcost

# OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# SMTP (opcional)
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=true
SMTP_FROM=

# SendGrid (opcional)
SENDGRID_API_KEY=
SENDGRID_FROM=
```

✅ Em Railway, configure essas variáveis no painel do service (não use `.env` em produção).

---

## ▶️ Rodando Localmente

### 1) Clonar

```bash
git clone https://github.com/eduardoliboriox/workcost.git
cd workcost
```

### 2) Ambiente virtual

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac**

```bash
python -m venv venv
source venv/bin/activate
```

### 3) Dependências

```bash
pip install -r requirements.txt
```

### 4) Executar

```bash
python run.py
```

Acesse:

* `http://127.0.0.1:5000`

---

## 🧪 Healthcheck e CI

### Healthcheck local

O CI executa:

* `python -m app.health`
* `pytest` (se houver testes)

Arquivo:

* `.github/workflows/ci.yml`

---

## 🗃 Banco de Dados (Railway) — Operação via psql (Windows)

Você já usa `psql.exe` direto no Windows.

📌 **Importante (segurança):** não coloque senhas/URLs completas no README público.
Use o `DATABASE_URL` do Railway e rode assim:

```bash
"C:\Program Files\PostgreSQL\18\bin\psql.exe" "%DATABASE_URL%"
```

### Sugestão prática (2 atalhos no Windows)

**Produção**

```bash
set ENVIRONMENT=production
"C:\Program Files\PostgreSQL\18\bin\psql.exe" "%DATABASE_URL%"
```

**Desenvolvimento**

```bash
set ENVIRONMENT=develop
"C:\Program Files\PostgreSQL\18\bin\psql.exe" "%DATABASE_URL%"
```

> Em Railway: copie o `DATABASE_URL` do service correto (prod/develop) e configure no ambiente.

---

## 🔁 Fluxos principais do sistema

### Solicitações

* Criar solicitação (modo create)
* Visualizar solicitação (modo view)
* Assinar funcionário (senha)
* Aprovar por role (senha)
* Fechar solicitação e registrar objetivo/observação
* Provisão por solicitação (visão financeira)

### Provisão (custos)

Hoje o cálculo considera:

* Refeição por turno
* Transporte (rota/veículo próprio)
* Adicional noturno (baseado em horário)

Arquivos chave:

* `app/services/provisao_service.py`
* `app/services/provisao_view_service.py`

---

## 🧩 Endpoints principais (visão rápida)

### Pages (HTML)

* `/dashboard`
* `/powerbi`
* `/solicitacoes` (create)
* `/solicitacoes/<id>` (view)
* `/solicitacoes/<id>/provisao`
* `/solicitacoes/<id>/frequencia`
* `/pedidos`
* `/minhas-extras`

### API (JSON)

* `GET /api/dashboard/resumo`
* `GET /api/dashboard/solicitacoes-resumo`
* `GET /api/dashboard/gastos-provisao`
* `POST /api/solicitacoes`
* `POST /api/solicitacoes/<id>/confirmar-presenca`
* `POST /api/solicitacoes/<id>/salvar-view`
* `POST /api/solicitacoes/<id>/fechamento`
* `POST /api/auth/confirm-extra`

---

## 📱 PWA

Arquivos:

* `app/static/manifest.webmanifest`
* `app/static/sw.js`
* Rotas:

  * `/manifest.webmanifest`
  * `/offline`

---

## 🧭 Convenções do projeto

* **Services**: regras e agregações (nada de SQL aqui)
* **Repositories**: SQL puro + acesso ao DB
* **Routes**:

  * `pages.py` para HTML
  * `api.py` para JSON
* **CSS/JS**: isolados por página sempre que possível

---

## 👨‍💻 Autor

**Eduardo Libório**
📧 `eduardosoleno@protonmail.com`

---

## 📄 Licença

Projeto de uso privado/interno.

```
