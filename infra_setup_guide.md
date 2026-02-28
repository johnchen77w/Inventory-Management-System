# Infrastructure Setup Guide — Step by Step

This guide walks through every setup step in order so all 4 team members can start developing immediately. **Member 3 (Infra) should execute these steps**, but everyone needs the prerequisites installed.

---

## Phase 1: Prerequisites (ALL Members)

Every team member needs these tools installed on their machine.

### Step 1.1 — Install Git

```bash
# Verify
git --version
# Should be 2.x+
```

- macOS: `brew install git`
- Ubuntu: `sudo apt install git`
- Windows: https://git-scm.com/download/win

### Step 1.2 — Install Docker Desktop

Download from https://docs.docker.com/get-docker/

```bash
# Verify
docker --version        # Should be 24+
docker compose version  # Should be v2.20+
```

> **Windows users:** Enable WSL 2 backend in Docker Desktop settings.

### Step 1.3 — Install Python 3.12+

```bash
# Verify
python3 --version   # Should be 3.12+
pip3 --version
```

- macOS: `brew install python@3.12`
- Ubuntu: `sudo apt install python3.12 python3.12-venv`
- Windows: https://www.python.org/downloads/

### Step 1.4 — Install Node.js 20+ (Member 4 essential, others optional)

```bash
# Verify
node --version   # Should be 20+
npm --version
```

- All platforms: https://nodejs.org/ (LTS)
- Or via nvm: `nvm install 20`

### Step 1.5 — Install minikube and kubectl (Member 3 essential, others recommended)

```bash
# minikube
# macOS:
brew install minikube

# Ubuntu:
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# kubectl
# macOS:
brew install kubectl

# Ubuntu:
sudo snap install kubectl --classic

# Verify
minikube version
kubectl version --client
```

### Step 1.6 — Install Fly CLI (Member 3 essential, others optional for now)

```bash
# macOS/Linux:
curl -L https://fly.io/install.sh | sh

# Verify
fly version
```

### Step 1.7 — Create Accounts (Member 3 handles, shares access with team)

| Service | URL | What You Need |
|---------|-----|---------------|
| **GitHub** | https://github.com | Everyone needs an account |
| **Fly.io** | https://fly.io | One team account (free tier) |
| **DigitalOcean** | https://cloud.digitalocean.com | One team account (GitHub Student Pack = $200 credit) |
| **SendGrid** | https://signup.sendgrid.com | One account (free: 100 emails/day) |

> **Important:** Apply for the [GitHub Student Developer Pack](https://education.github.com/pack) if you haven't — it gives $200 DigitalOcean credit and other perks.

---

## Phase 2: GitHub Repository Setup (Member 3)

### Step 2.1 — Create the Repository

1. Go to https://github.com/new
2. Repository name: `inventory-management-system`
3. Visibility: **Private** (add collaborators later; make public for final submission if desired)
4. Initialize with: README, `.gitignore` (Python), MIT License
5. Click **Create repository**

### Step 2.2 — Add All Team Members as Collaborators

Settings → Collaborators → Add people → Enter each member's GitHub username

Also add the instructor and TAs now (saves forgetting later):
- `cying17`
- `yuel5304`
- `YirenZzz`

### Step 2.3 — Set Up Branch Protection

Settings → Branches → Add rule:
- Branch name pattern: `main`
- ✅ Require a pull request before merging
- ✅ Require approvals: 1
- ✅ Require status checks to pass (enable after CI/CD is set up)
- Click **Create**

### Step 2.4 — Create Issue Labels

Go to Issues → Labels → Create:

| Label | Color | Description |
|-------|-------|-------------|
| `backend` | `#059669` | Backend API work |
| `frontend` | `#2563eb` | Frontend UI work |
| `infra` | `#d97706` | Docker, K8s, Fly.io |
| `monitoring` | `#7c3aed` | Prometheus, Grafana |
| `websocket` | `#ea580c` | Real-time features |
| `database` | `#dc2626` | Schema, migrations |
| `bug` | `#e11d48` | Bug fixes |
| `documentation` | `#64748b` | Docs, README |

### Step 2.5 — Everyone Clones the Repo

```bash
git clone https://github.com/<your-username>/inventory-management-system.git
cd inventory-management-system

# Set default pull strategy
git config pull.rebase true
```

---

## Phase 3: Project Directory Structure (Member 3)

### Step 3.1 — Create the Scaffold

```bash
cd inventory-management-system

# Backend
mkdir -p backend/app/{models,schemas,routers,services,middleware,ws,utils}
mkdir -p backend/tests
mkdir -p backend/alembic/versions

# Frontend
mkdir -p frontend/src/app/{login,inventory,categories,locations,alerts,users}
mkdir -p frontend/src/{components,hooks,lib}
mkdir -p frontend/public

# Kubernetes
mkdir -p k8s/monitoring

# Monitoring configs
mkdir -p monitoring/grafana/provisioning/{datasources,dashboards}

# Serverless
mkdir -p serverless/packages/alerts/low_stock

# Scripts
mkdir -p scripts

# GitHub Actions
mkdir -p .github/workflows
```

### Step 3.2 — Create Placeholder Files

```bash
# Backend init files
touch backend/app/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/routers/__init__.py
touch backend/app/services/__init__.py
touch backend/app/middleware/__init__.py
touch backend/app/ws/__init__.py
touch backend/app/utils/__init__.py
touch backend/tests/__init__.py
touch backend/tests/conftest.py

# Key files
touch backend/app/main.py
touch backend/app/config.py
touch backend/app/database.py
touch backend/requirements.txt
touch backend/requirements-dev.txt
touch backend/Dockerfile
touch backend/alembic.ini

# Frontend
touch frontend/package.json
touch frontend/next.config.js
touch frontend/Dockerfile

# Root files
touch docker-compose.yml
touch .env.example
touch ai-session.md
```

### Step 3.3 — Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
venv/
.venv/
*.egg

# Node
node_modules/
.next/
out/

# Environment
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
*.log

# Coverage
htmlcov/
.coverage
coverage.xml
EOF
```

### Step 3.4 — Create .env.example

```bash
cat > .env.example << 'EOF'
# Database
POSTGRES_USER=inventory
POSTGRES_PASSWORD=secret
POSTGRES_DB=inventory_db
DATABASE_URL=postgresql://inventory:secret@postgres:5432/inventory_db

# Auth
JWT_SECRET=change-me-to-a-long-random-string-at-least-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Default Admin (created on first startup)
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=admin123
DEFAULT_ADMIN_NAME=System Admin

# Redis
REDIS_URL=redis://redis:6379

# SendGrid (Member 4 will configure)
SENDGRID_API_KEY=
ALERT_FROM_EMAIL=alerts@inventory-app.com

# Serverless Function URL (Member 4 will configure)
LOW_STOCK_FUNCTION_URL=

# Fly.io
PRIMARY_REGION=yyz
EOF
```

### Step 3.5 — Commit and Push

```bash
cp .env.example .env   # Local copy (gitignored)
git add -A
git commit -m "chore: initialize project structure"
git push origin main
```

---

## Phase 4: Backend Foundation (Member 1 + Member 2)

### Step 4.1 — Python Dependencies (Member 1)

```bash
cat > backend/requirements.txt << 'EOF'
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
alembic==1.13.2
psycopg2-binary==2.9.9
pyjwt==2.9.0
bcrypt==4.2.0
python-dotenv==1.0.1
pydantic[email]==2.9.0
pydantic-settings==2.5.0
redis==5.1.0
httpx==0.27.0
prometheus-fastapi-instrumentator==7.0.0
EOF

cat > backend/requirements-dev.txt << 'EOF'
pytest==8.3.0
pytest-cov==5.0.0
pytest-asyncio==0.24.0
httpx==0.27.0
EOF
```

### Step 4.2 — FastAPI Skeleton (Member 1)

Create `backend/app/config.py`:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://inventory:secret@localhost:5432/inventory_db"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    redis_url: str = "redis://localhost:6379"
    default_admin_email: str = "admin@example.com"
    default_admin_password: str = "admin123"
    default_admin_name: str = "System Admin"
    primary_region: str = "yyz"

    class Config:
        env_file = ".env"

settings = Settings()
```

Create `backend/app/database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Create `backend/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Inventory Management System",
    description="Cloud-native inventory management with real-time updates",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Routers will be added here as they're built:
# from app.routers import auth, items, categories, locations, logs, alerts, dashboard
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(items.router, prefix="/api/v1/items", tags=["items"])
# ...
```

### Step 4.3 — Database Schema (Member 2)

Initialize Alembic:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic init alembic
```

Edit `backend/alembic.ini` — change the `sqlalchemy.url` line:
```ini
sqlalchemy.url = postgresql://inventory:secret@localhost:5432/inventory_db
```

Edit `backend/alembic/env.py` — add after imports:
```python
from app.database import Base
from app.models import user, item, category, location, log, alert  # import all models
target_metadata = Base.metadata
```

Then Member 2 creates all model files under `backend/app/models/` (user.py, item.py, category.py, location.py, log.py, alert.py) using the schema from the design doc.

Generate the first migration:
```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

### Step 4.4 — Commit Backend Foundation

```bash
git checkout -b feat/backend-skeleton
git add -A
git commit -m "feat(backend): FastAPI skeleton, config, DB setup, dependencies"
git push origin feat/backend-skeleton
# Create a Pull Request → get 1 approval → merge to main
```

---

## Phase 5: Docker Compose (Member 3)

### Step 5.1 — Backend Dockerfile

```bash
cat > backend/Dockerfile << 'DOCKERFILE'
# Stage 1: Build
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
DOCKERFILE
```

### Step 5.2 — Docker Compose

```bash
cat > docker-compose.yml << 'YAML'
version: "3.9"

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./backend:/app    # Hot reload for development
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    restart: unless-stopped

volumes:
  pgdata:
  grafana_data:
YAML
```

### Step 5.3 — Prometheus Config

```bash
cat > monitoring/prometheus.yml << 'YAML'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "inventory-api"
    static_configs:
      - targets: ["api:8000"]
    metrics_path: /metrics
YAML
```

### Step 5.4 — Grafana Datasource Auto-Provisioning

```bash
cat > monitoring/grafana/provisioning/datasources/prometheus.yml << 'YAML'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
YAML
```

### Step 5.5 — Test Everything Starts

```bash
# From project root
docker compose up --build

# In another terminal, verify:
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Check Prometheus: http://localhost:9090
# Check Grafana:    http://localhost:3001 (admin/admin)
# Check Postgres:   docker compose exec postgres psql -U inventory -d inventory_db -c "\dt"
```

### Step 5.6 — Commit

```bash
git checkout -b infra/docker-compose
git add -A
git commit -m "infra(docker): Docker Compose with API, PostgreSQL, Redis, Prometheus, Grafana"
git push origin infra/docker-compose
# PR → merge
```

---

## Phase 6: Frontend Scaffold (Member 4)

### Step 6.1 — Initialize Next.js

```bash
cd frontend
npx create-next-app@14 . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
```

### Step 6.2 — Install Dependencies

```bash
npm install axios
npm install --save-dev @types/node
```

### Step 6.3 — Create API Client

Create `frontend/src/lib/api.ts`:
```typescript
import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
});

// Add JWT interceptor
api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Step 6.4 — Frontend Dockerfile

```bash
cat > frontend/Dockerfile << 'DOCKERFILE'
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./
RUN npm ci --production
EXPOSE 3000
CMD ["npm", "start"]
DOCKERFILE
```

### Step 6.5 — Add Frontend to Docker Compose (Member 3 helps)

Add this service to `docker-compose.yml`:
```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_WS_URL=ws://localhost:8000
    depends_on:
      - api
    restart: unless-stopped
```

### Step 6.6 — Commit

```bash
git checkout -b feat/frontend-scaffold
git add -A
git commit -m "feat(frontend): Next.js scaffold with API client and Dockerfile"
git push origin feat/frontend-scaffold
# PR → merge
```

---

## Phase 7: Run Database Migration Inside Docker (Member 2)

### Step 7.1 — Add Migration Script

Create `backend/scripts/start.sh`:
```bash
#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
chmod +x backend/scripts/start.sh
```

### Step 7.2 — Update Backend Dockerfile CMD

Change the last line of `backend/Dockerfile`:
```dockerfile
CMD ["bash", "scripts/start.sh"]
```

Now migrations auto-run every time the container starts.

---

## Phase 8: Verify the Full Stack (ALL Members)

### Step 8.1 — Pull Latest and Start

```bash
git checkout main
git pull origin main
cp .env.example .env    # If you haven't already
docker compose up --build
```

### Step 8.2 — Verify Checklist

| Check | URL / Command | Expected |
|-------|--------------|----------|
| API health | `curl http://localhost:8000/health` | `{"status":"healthy"}` |
| API docs | http://localhost:8000/docs | Swagger UI loads |
| PostgreSQL | `docker compose exec postgres psql -U inventory -d inventory_db -c "\dt"` | Tables listed |
| Redis | `docker compose exec redis redis-cli ping` | `PONG` |
| Prometheus | http://localhost:9090/targets | `inventory-api` target shows UP |
| Grafana | http://localhost:3001 (admin/admin) | Dashboard loads, Prometheus datasource connected |
| Frontend | http://localhost:3000 | Next.js page loads |

### Step 8.3 — If Something Fails

```bash
# View logs for a specific service
docker compose logs api
docker compose logs postgres

# Rebuild from scratch
docker compose down -v
docker compose up --build

# Check if ports are already in use
lsof -i :8000
lsof -i :5432
lsof -i :3000
```

---

## Phase 9: Everyone Starts Their Work

Once Phase 8 passes for all members, everyone branches off `main` and starts:

| Member | First Branch | First Task |
|--------|-------------|------------|
| **Member 1** | `feat/auth` | JWT auth + register/login endpoints + RBAC middleware |
| **Member 2** | `feat/models` | SQLAlchemy models for all 6 tables + Alembic migration + seed script |
| **Member 3** | `infra/k8s-manifests` | Kubernetes namespace, secrets, postgres StatefulSet + PVC |
| **Member 4** | `feat/login-page` | Login page UI + auth hook + protected route wrapper |

### Git Workflow for Everyone

```bash
# Start new work
git checkout main
git pull origin main
git checkout -b feat/your-feature-name

# Work, commit frequently
git add -A
git commit -m "feat(scope): description of what you did"

# Push and create PR
git push origin feat/your-feature-name
# Go to GitHub → Create Pull Request → Request 1 review → Merge after approval

# After merge, clean up
git checkout main
git pull origin main
git branch -d feat/your-feature-name
```

### Commit Message Convention

```
feat(backend): add JWT authentication middleware
feat(frontend): build inventory list page
infra(docker): add Redis to Docker Compose
infra(k8s): create API deployment with 3 replicas
fix(api): handle duplicate SKU on item creation
test(auth): add login endpoint tests
docs: update README with setup instructions
```

---

## Quick Reference: Services & Ports

| Service | Local Port | Container Port | Purpose |
|---------|-----------|----------------|---------|
| API (FastAPI) | 8000 | 8000 | REST API + WebSocket |
| Frontend (Next.js) | 3000 | 3000 | Web UI |
| PostgreSQL | 5432 | 5432 | Database |
| Redis | 6379 | 6379 | WS Pub/Sub broker |
| Prometheus | 9090 | 9090 | Metrics collection |
| Grafana | 3001 | 3000 | Dashboards |

---

## Quick Reference: Key External Accounts

| Service | Setup By | Shared How |
|---------|---------|------------|
| GitHub repo | Member 3 | Collaborator invites |
| Fly.io | Member 3 | Share login or use `fly auth token` |
| DigitalOcean | Member 3 | Team access or shared project |
| SendGrid | Member 4 | API key in `.env` (never commit!) |

---

## What NOT to Commit

- `.env` (contains secrets) — use `.env.example` as the template
- `node_modules/`
- `__pycache__/`
- `.next/`
- `venv/`
- Any API keys, passwords, or tokens

If someone accidentally commits secrets:
```bash
# Remove from tracking (file stays local)
git rm --cached .env
git commit -m "fix: remove .env from tracking"

# Rotate the exposed credentials immediately
```