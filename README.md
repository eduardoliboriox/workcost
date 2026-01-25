# Venttos – Factory Metrics

**Venttos – Factory Metrics** é um sistema web desenvolvido para **engenharia, produção e PCP**, com foco em **controle de absenteísmo**, **análise de headcount**, **métricas operacionais** e **padronização de dados industriais**.

O projeto foi pensado para uso real em fábrica, priorizando **simplicidade**, **consistência de dados**, **baixo erro operacional** e **arquitetura limpa**.

---

## 🎯 Finalidade

* Lançamento diário de **absenteísmo por setor, linha e turno**
* Cálculo automático de **HC real**
* Registro de **faltas por cargo**
* Dashboard com visão consolidada
* Padronização de setores e linhas (sem digitação manual)
* Base sólida para futuras análises de PCP e produtividade

---

## 🧠 Conceitos Importantes

* **Setor → Linha dependente** (select dinâmico)
* Evita erros de digitação e dados inconsistentes
* Regras de negócio isoladas em *services*
* Acesso ao banco isolado em *repositories*
* Rotas HTML separadas de rotas REST

Arquitetura inspirada em boas práticas de **DDD leve + Clean Architecture**.

---

## 📊 Funcionalidades Principais

### 📌 Lançamento de Absenteísmo

* Seleção de:

  * Data
  * Filial
  * Setor
  * Linha (dinâmica)
  * Turno
* Definição de **HC padrão**
* Cálculo automático de **HC real**
* Inclusão de faltas por cargo
* Envio dos dados via API REST

### 📊 Dashboard

* Visualização consolidada dos lançamentos
* Indicadores operacionais
* Base para métricas futuras

---

## 📱 Plataforma

* Interface responsiva
* Desktop e mobile
* Layout mobile inspirado em **app nativo**
* Sidebar no desktop com navegação destacada

---

## ☁️ Infraestrutura

* Deploy em **Railway**
* Banco de dados **PostgreSQL**
* Variáveis de ambiente via `.env`
* Pronto para CI/CD

---

## 🧱 Estrutura do Projeto

```text
project/
├─ app/
│   ├─ __init__.py            # create_app()
│   ├─ config.py              # Configurações / env
│   ├─ extensions.py          # DB (psycopg)
│   │
│   ├─ repositories/          # Acesso ao banco (SQL)
│   │   ├─ __init__.py
│   │   ├─ atestados_repository.py
│   │   ├─ cargos_repository.py
│   │   ├─ lancamentos_repository.py
│   │   └─ modelos_repository.py
│   │  
│   ├─ routes/
│   │   ├─ __init__.py
│   │   ├─ api.py             # Rotas REST (JSON)
│   │   └─ pages.py           # Rotas HTML
│   │
│   ├─ services/              # Regras de negócio
│   │   ├─ atestados_service.py
│   │   ├─ cargos_service.py
│   │   ├─ lancamentos_service.py
│   │   ├─ modelos_service.py
│   │   └─ pcp_service.py
│   │
│   ├─ templates/             # Jinja2
│   │   ├─ base.html
│   │   ├─ cargos.html
│   │   ├─ dashboard.html
│   │   ├─ inicio.html
│   │   ├─ lancamento.html
│   │   ├─ powerbi.html
│   │   └─ relatorios.html
│   │
│   └─ static/
│       ├─ css/
│       │   ├─ powerbi.css
│       │   └─ style.css
│       │
│       ├─ js/
│       │   ├─ main.js
│       │   ├─ pcp.js
│       │   └─ powerbi.js
│       │
│       ├─ images/
│       └─ fonts/inter.woff2
│
├─ migrations/                # Alembic (ainda não utilizado)
├─ tests/                     # pytest
├─ run.py                     # Entrypoint
├─ requirements.txt
├─ LICENSE
├─ Procfile                   # Railway
├─ README.md
├─ .env                       # NÃO versionar
├─ .gitignore
└─ pyproject.toml
```

---

## ⚙️ Tecnologias Utilizadas

* Python 3
* Flask
* Jinja2
* HTML5 / CSS3
* JavaScript (Vanilla)
* PostgreSQL
* Bootstrap 5
* Railway

---

## ▶️ Como Rodar o Projeto Localmente

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/seu-usuario/venttos-factory-metrics.git
cd venttos-factory-metrics
```

### 2️⃣ Criar e ativar o ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux / Mac
```

### 3️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz:

```env
FLASK_ENV=development
SECRET_KEY=supersecretkey
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### 5️⃣ Executar a aplicação

```bash
python run.py
```

Acesse:

```
http://127.0.0.1:5000
```

---

## 📌 Observações

* Não possui autenticação (por enquanto)
* Foco em uso interno / industrial
* Estrutura pronta para escalar
* Código organizado para fácil manutenção

---

## 🚀 Deploy

* Deploy contínuo via **Railway**
* Uso de `Procfile`
* Banco PostgreSQL gerenciado

---

## 👨‍💻 Autor

Desenvolvido por **Eduardo Libório**

📧 [eduardosoleno@protonmail.com](mailto:eduardosoleno@protonmail.com)

---

## 📄 Licença

Projeto de uso privado / interno.
