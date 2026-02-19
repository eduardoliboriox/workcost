

## ☁️ Infraestrutura

* Deploy em **Railway**
* Banco de dados **PostgreSQL**
* Variáveis de ambiente via `.env`
* Pronto para CI/CD

---

## 🧱 Estrutura do Projeto

```text
project/

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

## ▶️ Como Rodar o Projeto Localmente cttttttttttttttt

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
