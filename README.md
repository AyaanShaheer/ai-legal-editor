# 🧠 AI Legal Document Editor

An intelligent legal document editing backend powered by **Azure OpenAI** that performs natural-language edits on DOCX files and returns **tracked changes**, full **version history**, and a complete **audit trail**.

Built with **FastAPI, Celery, PostgreSQL, Redis, and Azure services**.

> 🔗 Repository: [https://github.com/AyaanShaheer/ai-legal-editor](https://github.com/AyaanShaheer/ai-legal-editor)

---

## 🎯 What This System Does

This platform allows users to:

* Upload legal documents (`.docx`)
* Give natural language editing instructions
* Receive AI-generated edits as **Word tracked changes**
* Preview patches before applying
* Maintain complete document version history
* Apply / reject edits with audit logging
* Process edits asynchronously via background workers

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)              │
│  Routes: upload, edit, status, patch, apply, versions │
└──────┬──────────────────────────────────────────┬──────┘
       │                                          │
       ▼                                          ▼
┌──────────────┐                        ┌─────────────────┐
│  PostgreSQL  │                        │  Celery Worker  │
│   Database   │◄──────────────────────►│  (Async Jobs)   │
└──────────────┘                        └────────┬────────┘
                                                 │
       ┌─────────────────────────────────────────┤
       ▼                                         ▼
┌──────────────┐                        ┌─────────────────┐
│ Azure Blob   │                        │  Azure OpenAI   │
│  Storage     │                        │   GPT-4 API     │
└──────────────┘                        └─────────────────┘
```

---

## ✅ Implemented Features

### Core Engine

* DOCX parser with formatting preservation
* Patch engine using `diff-match-patch`
* Word **tracked changes** generator
* Version management & retrieval
* Background processing via Celery

### Storage & Persistence

* PostgreSQL for metadata
* Azure Blob Storage (local fallback in dev)
* Repository pattern (async + sync)
* SQLAlchemy models & auto table creation

### AI Integration

* Azure OpenAI GPT-4 powered editor
* Structured JSON patch output
* Patch validation before application
* Mock agent for cost-free testing

### API Endpoints

| Method | Endpoint                                       | Description             |
| ------ | ---------------------------------------------- | ----------------------- |
| POST   | `/api/v1/upload`                               | Upload DOCX             |
| POST   | `/api/v1/documents/{id}/edit`                  | Submit edit instruction |
| GET    | `/api/v1/jobs/{id}`                            | Job status              |
| GET    | `/api/v1/jobs/{id}/patch`                      | Preview patch           |
| POST   | `/api/v1/jobs/{id}/apply`                      | Apply changes           |
| GET    | `/api/v1/documents/{id}/versions`              | List versions           |
| GET    | `/api/v1/documents/{id}/versions/{v}/download` | Download version        |
| GET    | `/api/v1/documents`                            | List documents          |

---

## 🛠️ Tech Stack

**Backend**

* Python 3.10+
* FastAPI
* Celery + Redis
* SQLAlchemy
* PostgreSQL

**AI / Processing**

* Azure OpenAI (GPT-4)
* python-docx
* diff-match-patch

**Storage**

* Azure Blob Storage
* Local filesystem fallback

**DevOps**

* Docker & Docker Compose

---

## 🚀 Quick Start (Local Development)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/AyaanShaheer/ai-legal-editor.git
cd ai-legal-editor
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # macOS/Linux
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment

```bash
cp .env.example .env
```

Minimum required:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/legal_editor
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 5️⃣ Start Infrastructure

```bash
docker-compose up -d
```

### 6️⃣ Initialize Database

```bash
python scripts/init_db.py
```

### 7️⃣ Run Services

**Terminal 1**

```bash
uvicorn app.main:app --reload --port 8000
```

**Terminal 2**

```bash
celery -A worker.celery_app worker --loglevel=info --pool=solo
```

### 8️⃣ Verify End-to-End

```bash
python scripts/test_end_to_end.py
```

---

## 🧪 Manual API Test (cURL)

Upload:

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@tests/fixtures/sample_employment_agreement.docx"
```

Edit:

```bash
curl -X POST "http://localhost:8000/api/v1/documents/1/edit" \
  -H "Content-Type: application/json" \
  -d '{"instruction":"Change company name to TechCorp Industries"}'
```

---

## 🗂️ Project Structure (Simplified)

```
app/
 ├─ api/           → Routes & DI
 ├─ core/          → Config, DB, Celery, logging
 ├─ models/        → SQLAlchemy models
 ├─ repositories/  → Data access layer
 ├─ services/      → DOCX, patching, storage, LLM
 ├─ tasks/         → Celery jobs
 └─ main.py
scripts/           → Tests & DB init
tests/fixtures/    → Sample documents
docker-compose.yml
worker.py
```

---

## 🔧 Important Environment Variables

```
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_STORAGE_CONNECTION_STRING=
AZURE_STORAGE_CONTAINER_NAME=documents
MAX_FILE_SIZE_MB=10
```

If Azure keys are missing → system auto-switches to **mock agent**.

---

## 📚 API Docs

* Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔒 Security Status

> Current: Development-mode

Missing for production:

* Authentication (Azure AD / JWT)
* Rate limiting
* HTTPS
* CORS rules
* Input sanitization
* Alembic migrations
* Health checks

---

## 🧭 Roadmap

**Frontend**

* React / Next.js UI
* Patch visualization
* Version comparison

**Deployment**

* Azure Container Apps
* Azure PostgreSQL
* Key Vault
* GitHub Actions CI/CD

**Advanced**

* Clause extraction & risk scoring
* Batch processing
* PDF export with tracked changes

---

## 👤 Author

**Ayaan Shaheer**
Full-Stack Developer • AI/ML Engineer

---

## 📄 License

MIT

---

## 💬 Support

Open an issue with:

* Logs
* Steps to reproduce
* Environment info

---

## ✅ Project Status

**Backend:** Complete
**Frontend:** Pending
**Deployment:** Pending

*Last updated: Feb 2026*

---
