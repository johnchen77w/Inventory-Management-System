# Inventory Management System — Complete System Design

## ECE 1779: Introduction to Cloud Computing (Winter 2026)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Overview](#2-architecture-overview)
3. [Technology Stack](#3-technology-stack)
4. [Core Technical Requirements — Compliance Matrix](#4-core-technical-requirements--compliance-matrix)
5. [Advanced Features (2 Required, 3 Planned)](#5-advanced-features)
6. [Database Schema](#6-database-schema)
7. [API Design](#7-api-design)
8. [Real-Time WebSocket Design](#8-real-time-websocket-design)
9. [Authentication & Role-Based Access Control](#9-authentication--role-based-access-control)
10. [Containerization & Docker Compose](#10-containerization--docker-compose)
11. [Kubernetes Orchestration](#11-kubernetes-orchestration)
12. [Deployment on Fly.io](#12-deployment-on-flyio)
13. [Monitoring & Observability](#13-monitoring--observability)
14. [Serverless Low-Stock Email Notifications](#14-serverless-low-stock-email-notifications)
15. [Edge Routing & Global Distribution](#15-edge-routing--global-distribution)
16. [CI/CD Pipeline](#16-cicd-pipeline)
17. [Backup & Recovery](#17-backup--recovery)
18. [Frontend (Optional UI)](#18-frontend-optional-ui)
19. [Directory Structure](#19-directory-structure)
20. [Development Workflow](#20-development-workflow)
21. [Lines of Code Estimation](#21-lines-of-code-estimation)
22. [Risk Mitigation](#22-risk-mitigation)

---

## 1. Project Overview

**Project:** Cloud-Native Inventory Management System  
**Deployment Provider:** Fly.io (edge/PaaS focus)  
**Orchestration:** Kubernetes (minikube locally → DigitalOcean Kubernetes for cloud)  
**Database:** PostgreSQL with Fly.io Persistent Volumes  

The system allows organizations to track and manage inventory in real time, with role-based access for Managers and Staff. It features live stock updates via WebSockets, automated low-stock alerts via serverless email notifications, and edge-optimized routing for global low-latency access.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                 │
│   Browser (Next.js Frontend)  /  REST API consumers             │
└──────────────┬──────────────────────────┬───────────────────────┘
               │ HTTPS                    │ WSS (WebSocket)
               ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Fly.io Edge Network                           │
│              (Region-based routing / TLS termination)            │
└──────────────┬──────────────────────────┬───────────────────────┘
               │                          │
               ▼                          ▼
┌──────────────────────────────────────────────────────────────┐
│          Kubernetes Cluster (DigitalOcean Managed K8s)        │
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────┐        │
│  │   API Service         │    │   WebSocket Service   │        │
│  │   (Python/FastAPI)    │    │   (Python/FastAPI)    │        │
│  │   Replicas: 2-4       │    │   Replicas: 2         │        │
│  └──────────┬───────────┘    └──────────┬───────────┘        │
│             │                           │                     │
│             ▼                           ▼                     │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              PostgreSQL (StatefulSet)                 │     │
│  │              + PersistentVolume (Fly Volume)          │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────┐        │
│  │  Prometheus + Grafana │    │  Backup CronJob       │        │
│  │  (Monitoring Stack)   │    │  (pg_dump → S3/DO     │        │
│  │                       │    │   Spaces)              │        │
│  └──────────────────────┘    └──────────────────────┘        │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              Serverless Functions                              │
│  ┌──────────────────────────────────────────────┐            │
│  │  Low-Stock Alert Function (DigitalOcean       │            │
│  │  Functions or Fly.io Machine)                 │            │
│  │  Trigger: API event / cron                    │            │
│  │  Action: Send email via SendGrid              │            │
│  └──────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Backend** | Python 3.12 + FastAPI | High performance async framework, native WebSocket support |
| **Database** | PostgreSQL 16 | Course requirement; excellent for relational inventory data |
| **ORM** | SQLAlchemy 2.0 + Alembic | Type-safe queries, schema migrations |
| **Auth** | JWT (PyJWT) + bcrypt | Stateless auth suitable for distributed deployment |
| **Real-time** | FastAPI WebSockets | Built-in support, no extra dependencies |
| **Containerization** | Docker + Docker Compose | Course requirement |
| **Orchestration** | Kubernetes (minikube local / DO managed) | Course requirement — Option B |
| **Deployment** | Fly.io | Course requirement — edge/PaaS focus |
| **Monitoring** | Fly.io metrics + Prometheus + Grafana | Course requirement |
| **Serverless** | DigitalOcean Functions (or Fly Machine) | Advanced feature — event-driven email alerts |
| **Email** | SendGrid API | Reliable transactional email for low-stock alerts |
| **Frontend** | Next.js 14 (React) | Optional; makes demo clearer |
| **CI/CD** | GitHub Actions | Advanced feature — automated build/deploy |

---

## 4. Core Technical Requirements — Compliance Matrix

| Requirement | Implementation | Status |
|------------|---------------|--------|
| **Docker containerization** | Dockerfile for API, WS service, frontend; multi-stage builds | ✅ Planned |
| **Docker Compose** | `docker-compose.yml` with api, ws, postgres, prometheus, grafana services | ✅ Planned |
| **PostgreSQL** | PostgreSQL 16 container; SQLAlchemy ORM; Alembic migrations | ✅ Planned |
| **Persistent Storage** | Fly.io Volumes mounted to PostgreSQL data directory | ✅ Planned |
| **Deployment to Fly.io** | `fly.toml` config; `fly deploy` for API + WS services | ✅ Planned |
| **Kubernetes orchestration** | minikube local; DigitalOcean K8s for prod; Deployments, Services, PVCs | ✅ Planned |
| **Monitoring & Observability** | Fly.io built-in metrics + Prometheus scraping + Grafana dashboards + alerts | ✅ Planned |
| **≥2 Advanced Features** | 3 planned: (1) Real-time WebSockets, (2) Serverless email notifications, (3) Edge routing | ✅ Planned |

---

## 5. Advanced Features

We will implement **3 advanced features** (minimum 2 required):

### 5.1 Real-Time Functionality (WebSockets)

Live stock updates pushed to all connected clients when inventory changes occur.

- When any user creates, updates, or deletes an inventory item, the API publishes an event.
- All connected WebSocket clients receive the update instantly.
- Events: `item_created`, `item_updated`, `item_deleted`, `stock_low_alert`.
- Implementation: FastAPI WebSocket endpoint with in-memory pub/sub (or Redis pub/sub for multi-replica).

### 5.2 Serverless Email Notifications for Low-Stock Alerts

When an item's quantity drops below its configured threshold, an event triggers a serverless function that sends an email to the Manager.

- Trigger mechanism: The API calls the serverless function endpoint when stock drops below threshold.
- Serverless platform: DigitalOcean Functions (HTTP trigger) or a lightweight Fly Machine.
- Email provider: SendGrid API (free tier: 100 emails/day).
- Email contains: item name, current quantity, threshold, location, and a direct link to the item.

### 5.3 Edge Routing for Low-Latency Access

Fly.io's global edge network routes requests to the nearest region.

- Deploy API replicas to multiple Fly.io regions (e.g., `yyz` Toronto, `iad` Virginia, `lhr` London).
- Fly.io automatically routes users to the nearest healthy instance.
- PostgreSQL primary in one region with read replicas if needed.
- Configuration via `fly.toml` with `[regions]` and `primary_region` settings.

---

## 6. Database Schema

```sql
-- Users table (authentication + RBAC)
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    role            VARCHAR(20) NOT NULL CHECK (role IN ('manager', 'staff')),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories for organizing inventory
CREATE TABLE categories (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) UNIQUE NOT NULL,
    description     TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Locations (warehouses, shelves, etc.)
CREATE TABLE locations (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) UNIQUE NOT NULL,
    description     TEXT,
    address         TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inventory items (core entity)
CREATE TABLE items (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    sku             VARCHAR(100) UNIQUE NOT NULL,
    description     TEXT,
    category_id     INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    location_id     INTEGER REFERENCES locations(id) ON DELETE SET NULL,
    quantity        INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    unit            VARCHAR(50) DEFAULT 'pcs',
    price           DECIMAL(10,2),
    low_stock_threshold INTEGER DEFAULT 10,
    created_by      INTEGER REFERENCES users(id),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log for inventory changes (tracks who changed what)
CREATE TABLE inventory_logs (
    id              SERIAL PRIMARY KEY,
    item_id         INTEGER REFERENCES items(id) ON DELETE CASCADE,
    user_id         INTEGER REFERENCES users(id),
    action          VARCHAR(20) NOT NULL CHECK (action IN ('create', 'update', 'delete', 'restock', 'withdraw')),
    quantity_before INTEGER,
    quantity_after  INTEGER,
    notes           TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Low-stock alert records (tracks sent notifications)
CREATE TABLE alerts (
    id              SERIAL PRIMARY KEY,
    item_id         INTEGER REFERENCES items(id) ON DELETE CASCADE,
    alert_type      VARCHAR(50) NOT NULL DEFAULT 'low_stock',
    message         TEXT,
    sent_to         VARCHAR(255),
    sent_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    acknowledged    BOOLEAN DEFAULT FALSE,
    acknowledged_by INTEGER REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_items_category ON items(category_id);
CREATE INDEX idx_items_location ON items(location_id);
CREATE INDEX idx_items_sku ON items(sku);
CREATE INDEX idx_items_quantity ON items(quantity);
CREATE INDEX idx_inventory_logs_item ON inventory_logs(item_id);
CREATE INDEX idx_inventory_logs_created ON inventory_logs(created_at);
CREATE INDEX idx_alerts_item ON alerts(item_id);
```

---

## 7. API Design

Base URL: `https://inventory-api.fly.dev/api/v1`

### Authentication Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register new user | None (first user) or Manager |
| POST | `/auth/login` | Login, returns JWT | None |
| POST | `/auth/refresh` | Refresh JWT token | JWT |
| GET | `/auth/me` | Get current user profile | JWT |

### Item Endpoints (CRUD)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/items` | List items (with filtering, search, pagination) | Staff+ |
| GET | `/items/{id}` | Get single item detail | Staff+ |
| POST | `/items` | Create new item | Manager |
| PUT | `/items/{id}` | Update item (full) | Manager |
| PATCH | `/items/{id}` | Partial update (e.g., quantity only) | Staff+ |
| DELETE | `/items/{id}` | Delete item | Manager |
| POST | `/items/{id}/restock` | Add stock quantity | Staff+ |
| POST | `/items/{id}/withdraw` | Remove stock quantity | Staff+ |

**Query parameters for `GET /items`:**
- `search` — search by name or SKU
- `category_id` — filter by category
- `location_id` — filter by location
- `min_quantity` / `max_quantity` — filter by quantity range
- `below_threshold` — boolean, show only low-stock items
- `sort_by` — field name (name, quantity, updated_at, price)
- `order` — asc / desc
- `page` / `per_page` — pagination

### Category Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/categories` | List categories | Staff+ |
| POST | `/categories` | Create category | Manager |
| PUT | `/categories/{id}` | Update category | Manager |
| DELETE | `/categories/{id}` | Delete category | Manager |

### Location Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/locations` | List locations | Staff+ |
| POST | `/locations` | Create location | Manager |
| PUT | `/locations/{id}` | Update location | Manager |
| DELETE | `/locations/{id}` | Delete location | Manager |

### Logs & Alerts Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/logs` | List inventory change logs | Manager |
| GET | `/logs/item/{id}` | Logs for specific item | Staff+ |
| GET | `/alerts` | List alerts | Manager |
| PATCH | `/alerts/{id}/acknowledge` | Acknowledge an alert | Manager |

### Dashboard / Metrics Endpoint

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/dashboard/summary` | Total items, low-stock count, recent activity | Staff+ |
| GET | `/dashboard/category-breakdown` | Items per category | Staff+ |
| GET | `/health` | Health check (for K8s probes) | None |
| GET | `/metrics` | Prometheus metrics | None (internal) |

---

## 8. Real-Time WebSocket Design

### Connection

```
WSS://inventory-api.fly.dev/ws?token=<JWT>
```

### Message Protocol (JSON)

**Server → Client (Event Push):**
```json
{
  "event": "item_updated",
  "data": {
    "id": 42,
    "name": "Widget A",
    "quantity": 5,
    "previous_quantity": 50,
    "updated_by": "john@example.com",
    "timestamp": "2026-03-15T10:30:00Z"
  }
}
```

**Event Types:**
- `item_created` — new item added
- `item_updated` — item details changed
- `item_deleted` — item removed
- `stock_changed` — quantity specifically changed (restock/withdraw)
- `low_stock_alert` — item dropped below threshold
- `alert_acknowledged` — manager acknowledged alert

### Implementation

```python
# Simplified WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def broadcast(self, event: str, data: dict):
        message = {"event": event, "data": data}
        for ws in self.active_connections.values():
            await ws.send_json(message)
```

For multi-replica deployments, use **Redis Pub/Sub** as a message broker so all replicas receive and broadcast events.

---

## 9. Authentication & Role-Based Access Control

### Roles

| Role | Permissions |
|------|------------|
| **Manager** | Full CRUD on all resources; manage users; view logs & alerts; acknowledge alerts |
| **Staff** | View items; restock/withdraw items; view own logs |

### JWT Token Structure

```json
{
  "sub": 1,
  "email": "admin@example.com",
  "role": "manager",
  "exp": 1711234567,
  "iat": 1711148167
}
```

### Auth Flow

1. User registers (first user auto-becomes Manager; subsequent users need Manager approval).
2. User logs in → receives access token (1 hour) + refresh token (7 days).
3. All API requests include `Authorization: Bearer <token>`.
4. FastAPI dependency checks token validity and role permissions.

### Password Security

- Passwords hashed with **bcrypt** (12 rounds).
- Minimum 8 characters enforced server-side.

---

## 10. Containerization & Docker Compose

### Dockerfiles

**API Service (multi-stage build):**
```dockerfile
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
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend (Next.js):**
```dockerfile
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
```

### docker-compose.yml

```yaml
version: "3.9"

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://inventory:secret@postgres:5432/inventory_db
      - JWT_SECRET=${JWT_SECRET}
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    restart: unless-stopped

  websocket:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: uvicorn app.ws:app --host 0.0.0.0 --port 8001
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://inventory:secret@postgres:5432/inventory_db
      - JWT_SECRET=${JWT_SECRET}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
      - NEXT_PUBLIC_WS_URL=ws://websocket:8001
    depends_on:
      - api

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=inventory
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=inventory_db
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U inventory"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  pgdata:
  grafana_data:
```

---

## 11. Kubernetes Orchestration

### Local Development: minikube

```bash
minikube start --cpus=4 --memory=4096
eval $(minikube docker-env)
# Build images locally
docker build -t inventory-api:latest ./backend
docker build -t inventory-frontend:latest ./frontend
```

### Kubernetes Manifests

**k8s/namespace.yml**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: inventory
```

**k8s/postgres-statefulset.yml** (with PersistentVolume)
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: inventory
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 5Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: inventory
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: username
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: password
            - name: POSTGRES_DB
              value: inventory_db
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: inventory
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
  clusterIP: None
```

**k8s/api-deployment.yml** (with replicas + load balancing)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inventory-api
  namespace: inventory
spec:
  replicas: 3
  selector:
    matchLabels:
      app: inventory-api
  template:
    metadata:
      labels:
        app: inventory-api
    spec:
      containers:
        - name: api
          image: inventory-api:latest
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: app-secret
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: inventory-api
  namespace: inventory
spec:
  type: LoadBalancer
  selector:
    app: inventory-api
  ports:
    - port: 80
      targetPort: 8000
```

**k8s/secrets.yml** (template — real values via `kubectl create secret`)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: inventory
type: Opaque
data:
  username: aW52ZW50b3J5     # base64 of "inventory"
  password: c2VjcmV0         # base64 of "secret"
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
  namespace: inventory
type: Opaque
stringData:
  DATABASE_URL: postgresql://inventory:secret@postgres:5432/inventory_db
  JWT_SECRET: your-super-secret-jwt-key
  SENDGRID_API_KEY: your-sendgrid-key
```

### Production: DigitalOcean Managed Kubernetes

- Create cluster via DO console (cheapest: 2 nodes, $24/month basic).
- Push images to DO Container Registry or Docker Hub.
- Apply same manifests with production secrets.
- Use DO Volumes as the PersistentVolume storage class.

---

## 12. Deployment on Fly.io

### fly.toml (API Service)

```toml
app = "inventory-api"
primary_region = "yyz"          # Toronto

[build]
  dockerfile = "backend/Dockerfile"

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512

[checks]
  [checks.health]
    type = "http"
    port = 8000
    path = "/health"
    interval = "30s"
    timeout = "5s"
```

### Fly.io Volume for PostgreSQL Persistence

```bash
fly volumes create pg_data --region yyz --size 1
```

Mount in `fly.toml`:
```toml
[mounts]
  source = "pg_data"
  destination = "/var/lib/postgresql/data"
```

### Multi-Region Deployment

```bash
fly regions add yyz iad lhr
fly scale count 3
```

---

## 13. Monitoring & Observability

### Layer 1: Fly.io Built-in Metrics

- CPU, memory, disk usage per machine via Fly dashboard.
- Logs via `fly logs` and Fly.io log dashboard.
- Set up alerts: CPU > 80%, memory > 85%, disk > 90%.

### Layer 2: Application Metrics (Prometheus)

Expose `/metrics` endpoint from FastAPI using `prometheus-fastapi-instrumentator`:

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

**Custom metrics:**
- `inventory_items_total` — gauge of total items
- `inventory_low_stock_items` — gauge of items below threshold
- `inventory_api_requests_total` — counter by endpoint + status
- `inventory_ws_connections_active` — gauge of active WebSocket connections
- `inventory_stock_changes_total` — counter of restock/withdraw operations

### Layer 3: Grafana Dashboards

Pre-configured dashboards:
1. **System Health** — CPU, memory, request latency, error rates
2. **Inventory Overview** — total items, low-stock items, stock changes over time
3. **API Performance** — requests/sec, p50/p95/p99 latency, error rates by endpoint
4. **WebSocket Connections** — active connections, messages/sec

### Alerting Rules (Prometheus)

```yaml
groups:
  - name: inventory-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 2
        for: 5m
        labels:
          severity: warning
      - alert: LowStockItemsHigh
        expr: inventory_low_stock_items > 10
        for: 1m
        labels:
          severity: warning
```

---

## 14. Serverless Low-Stock Email Notifications

### Architecture

```
API (stock update) → HTTP POST → Serverless Function → SendGrid API → Email to Manager
```

### DigitalOcean Function

```python
# packages/alerts/low_stock/__main__.py
import requests
import os

def main(args):
    item_name = args.get("item_name", "Unknown")
    quantity = args.get("quantity", 0)
    threshold = args.get("threshold", 10)
    manager_email = args.get("manager_email")

    sendgrid_key = os.environ.get("SENDGRID_API_KEY")
    response = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {sendgrid_key}",
            "Content-Type": "application/json"
        },
        json={
            "personalizations": [{"to": [{"email": manager_email}]}],
            "from": {"email": "alerts@inventory-app.com"},
            "subject": f"⚠️ Low Stock Alert: {item_name}",
            "content": [{
                "type": "text/html",
                "value": f"<h2>Low Stock Alert</h2>"
                         f"<p><strong>{item_name}</strong> has dropped to "
                         f"<strong>{quantity}</strong> units "
                         f"(threshold: {threshold}).</p>"
                         f"<p>Please restock as soon as possible.</p>"
            }]
        }
    )
    return {"statusCode": response.status_code}
```

### Trigger from API

```python
# In the item update/withdraw endpoint
if item.quantity < item.low_stock_threshold:
    # Fire-and-forget to serverless function
    asyncio.create_task(trigger_low_stock_alert(item))
```

---

## 15. Edge Routing & Global Distribution

### Fly.io Configuration

- **Primary region:** `yyz` (Toronto) — where the PostgreSQL write primary lives.
- **Read replicas:** `iad` (Virginia), `lhr` (London) — using Fly Postgres read replicas.
- **API instances:** deployed across all 3 regions.
- **Fly Replay header:** write requests that hit a read-replica region are automatically replayed to the primary region.

```toml
# fly.toml
primary_region = "yyz"

[env]
  PRIMARY_REGION = "yyz"
```

In the application:
```python
@app.middleware("http")
async def route_writes_to_primary(request, call_next):
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        current_region = os.environ.get("FLY_REGION")
        primary = os.environ.get("PRIMARY_REGION")
        if current_region != primary:
            # Fly.io will replay this to the primary region
            return Response(status_code=409,
                          headers={"fly-replay": f"region={primary}"})
    return await call_next(request)
```

---

## 16. CI/CD Pipeline

### .github/workflows/deploy.yml

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: |
          cd backend
          pip install -r requirements.txt -r requirements-dev.txt
          pytest --cov=app tests/
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db

  build-and-push:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: registry.fly.io
          username: x
          password: ${{ secrets.FLY_API_TOKEN }}
      - run: |
          docker build -t registry.fly.io/inventory-api:${{ github.sha }} ./backend
          docker push registry.fly.io/inventory-api:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --image registry.fly.io/inventory-api:${{ github.sha }}
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

---

## 17. Backup & Recovery

### Automated Database Backups

**Kubernetes CronJob** that runs `pg_dump` daily and uploads to DigitalOcean Spaces (S3-compatible):

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: inventory
spec:
  schedule: "0 2 * * *"    # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: postgres:16-alpine
              command:
                - /bin/sh
                - -c
                - |
                  pg_dump $DATABASE_URL | gzip > /tmp/backup-$(date +%Y%m%d).sql.gz
                  # Upload to DO Spaces using s3cmd or aws cli
              envFrom:
                - secretRef:
                    name: app-secret
          restartPolicy: OnFailure
```

Retention: keep 7 daily + 4 weekly backups.

---

## 18. Frontend (Optional UI)

A simple Next.js dashboard to make the demo compelling. Key pages:

| Page | Description |
|------|-------------|
| `/login` | Login form |
| `/dashboard` | Summary cards (total items, low-stock, recent activity) + charts |
| `/inventory` | Searchable, filterable, sortable table of all items |
| `/inventory/[id]` | Item detail page with history log |
| `/inventory/new` | Create new item form (Manager only) |
| `/categories` | Manage categories |
| `/locations` | Manage locations |
| `/alerts` | View and acknowledge low-stock alerts (Manager only) |
| `/users` | User management (Manager only) |

Real-time badge: a live indicator showing WebSocket connection status and flashing when stock changes occur.

---

## 19. Directory Structure

```
inventory-management-system/
├── README.md                          # Final report
├── ai-session.md                      # AI interaction record
├── docker-compose.yml                 # Local multi-container setup
├── .github/
│   └── workflows/
│       └── deploy.yml                 # CI/CD pipeline
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/                  # Database migrations
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Settings / env vars
│   │   ├── database.py                # SQLAlchemy engine + session
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── item.py
│   │   │   ├── category.py
│   │   │   ├── location.py
│   │   │   ├── log.py
│   │   │   └── alert.py
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── item.py
│   │   │   ├── category.py
│   │   │   ├── location.py
│   │   │   ├── log.py
│   │   │   └── alert.py
│   │   ├── routers/                   # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── items.py
│   │   │   ├── categories.py
│   │   │   ├── locations.py
│   │   │   ├── logs.py
│   │   │   ├── alerts.py
│   │   │   └── dashboard.py
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── item_service.py
│   │   │   ├── alert_service.py
│   │   │   └── notification_service.py
│   │   ├── middleware/
│   │   │   ├── auth.py                # JWT dependency
│   │   │   └── region_routing.py      # Fly.io write routing
│   │   ├── ws/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py             # WebSocket connection manager
│   │   │   └── events.py              # Event types
│   │   └── utils/
│   │       ├── security.py            # bcrypt + JWT helpers
│   │       └── metrics.py             # Prometheus custom metrics
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_items.py
│       ├── test_categories.py
│       ├── test_websocket.py
│       └── test_alerts.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx               # Dashboard
│   │   │   ├── login/page.tsx
│   │   │   ├── inventory/
│   │   │   │   ├── page.tsx           # Item list
│   │   │   │   ├── [id]/page.tsx      # Item detail
│   │   │   │   └── new/page.tsx       # Create item
│   │   │   ├── categories/page.tsx
│   │   │   ├── locations/page.tsx
│   │   │   ├── alerts/page.tsx
│   │   │   └── users/page.tsx
│   │   ├── components/
│   │   │   ├── Navbar.tsx
│   │   │   ├── ItemTable.tsx
│   │   │   ├── StockChart.tsx
│   │   │   ├── AlertBanner.tsx
│   │   │   └── WebSocketStatus.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useWebSocket.ts
│   │   └── lib/
│   │       └── api.ts                 # API client
│   └── public/
├── k8s/
│   ├── namespace.yml
│   ├── secrets.yml
│   ├── postgres-statefulset.yml
│   ├── api-deployment.yml
│   ├── ws-deployment.yml
│   ├── frontend-deployment.yml
│   ├── redis-deployment.yml
│   └── monitoring/
│       ├── prometheus-deployment.yml
│       └── grafana-deployment.yml
├── monitoring/
│   ├── prometheus.yml                 # Prometheus config
│   ├── alert-rules.yml                # Alerting rules
│   └── grafana/
│       └── provisioning/
│           ├── datasources/
│           │   └── prometheus.yml
│           └── dashboards/
│               ├── system-health.json
│               └── inventory-overview.json
├── serverless/
│   ├── project.yml                    # DO Functions config
│   └── packages/
│       └── alerts/
│           └── low_stock/
│               ├── __main__.py
│               └── requirements.txt
└── scripts/
    ├── seed-data.py                   # Seed database with sample data
    ├── backup.sh                      # Manual backup script
    └── setup-local.sh                 # One-command local setup
```

---

## 20. Development Workflow

### Week-by-Week Plan (assuming ~5 weeks, team of 2)

| Week | Tasks | Deliverable |
|------|-------|-------------|
| **Week 1** (Feb 24 – Mar 2) | Project proposal; set up repo, Docker, DB schema, Alembic migrations | Proposal submitted; basic Docker Compose running |
| **Week 2** (Mar 3 – 9) | Auth system (JWT + RBAC); item CRUD endpoints; unit tests | Working REST API with auth |
| **Week 3** (Mar 10 – 16) | WebSocket real-time updates; search/filter; categories/locations; frontend skeleton | Real-time demo-ready; basic UI |
| **Week 4** (Mar 17 – 24) | Kubernetes manifests (minikube); monitoring (Prometheus + Grafana); serverless alerts; **presentation prep** | Presentation-ready; all core features working locally |
| **Week 5** (Mar 25 – Apr 4) | Deploy to Fly.io + DO K8s; edge routing; CI/CD pipeline; backup; polish; video demo; final report | Final deliverable submitted |

---

## 21. Lines of Code Estimation

For a 2-member team, the target is **1000+ lines per member** (2000+ total).

| Component | Estimated LOC |
|-----------|--------------|
| Backend Python (FastAPI, models, routers, services, auth, WS) | ~1,800 |
| SQL migrations | ~150 |
| Dockerfiles (2) | ~60 |
| docker-compose.yml | ~80 |
| Kubernetes YAML manifests | ~400 |
| Prometheus / Grafana config | ~150 |
| GitHub Actions CI/CD | ~80 |
| Serverless function | ~60 |
| Frontend (Next.js/React) | ~1,200 |
| Tests | ~400 |
| Scripts (seed, backup, setup) | ~100 |
| **Total** | **~4,480** |

This comfortably exceeds the 2,000-line minimum for a 2-person team.

---

## 22. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Fly.io deployment issues | Start local with Docker Compose + minikube; deploy to cloud in Week 5 with buffer |
| Kubernetes complexity | Use minikube for local dev; use DO managed K8s to avoid cluster management overhead |
| WebSocket scaling across replicas | Use Redis pub/sub as message broker between instances |
| Database data loss | Automated daily backups + persistent volumes |
| SendGrid email delivery | Test with SendGrid sandbox mode first; fallback to console logging |
| Scope creep | Prioritize core requirements first; advanced features second; UI polish last |
| Team coordination | Use GitHub Issues + PRs; daily async standup via GitHub Discussions |

---

## Summary of Requirement Coverage

| # | Requirement | How It's Met |
|---|------------|--------------|
| 1 | Docker containerization | Multi-stage Dockerfiles for API, WS, Frontend |
| 2 | Docker Compose | 7-service compose file (api, ws, frontend, postgres, redis, prometheus, grafana) |
| 3 | PostgreSQL | Primary database with SQLAlchemy ORM + Alembic migrations |
| 4 | Persistent storage | Fly.io Volumes for PostgreSQL; DO Volumes for K8s PVCs |
| 5 | Fly.io deployment | fly.toml config; multi-region deployment |
| 6 | Kubernetes orchestration | minikube local → DO managed K8s; Deployments, Services, PVCs, StatefulSets |
| 7 | Monitoring | Fly.io metrics + Prometheus + Grafana + alerting rules |
| 8 | Advanced: Real-time (WebSockets) | Live stock updates to all connected clients |
| 9 | Advanced: Serverless notifications | DO Functions / Fly Machine triggers SendGrid emails for low-stock |
| 10 | Advanced: Edge routing | Multi-region Fly.io deployment with automatic region-based routing |
| 11 | Search & filter | Full-text search by name/SKU; filter by category, location, quantity |
| 12 | Role-based access | Manager + Staff roles with JWT auth |
| 13 | Video demo | 1-5 min video showing all features |
| 14 | Final report (README.md) | Comprehensive documentation covering all required sections |
| 15 | AI interaction record | ai-session.md with 1-3 meaningful interactions |
