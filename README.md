# Inventory Management System

A cloud-native inventory management application with real-time stock tracking, role-based access control, and automated low-stock alerts. Built with FastAPI, PostgreSQL, Kubernetes, and deployed on Fly.io with edge-optimized routing.

> **ECE 1779: Introduction to Cloud Computing — Winter 2026 Course Project**

---

## Table of Contents

- [Team Information](#team-information)
- [Video Demo](#video-demo)
- [Motivation](#motivation)
- [Objectives](#objectives)
- [Technical Stack](#technical-stack)
- [Features](#features)
  - [Core Technical Requirements](#core-technical-requirements)
  - [Advanced Features](#advanced-features)
  - [Application Features](#application-features)
- [User Guide](#user-guide)
  - [Authentication](#1-authentication)
  - [Dashboard](#2-dashboard)
  - [Inventory Management](#3-inventory-management)
  - [Search and Filtering](#4-search-and-filtering)
  - [Categories and Locations](#5-categories-and-locations)
  - [Low-Stock Alerts](#6-low-stock-alerts)
  - [Real-Time Updates](#7-real-time-updates)
  - [User Management](#8-user-management-manager-only)
- [Development Guide](#development-guide)
  - [Prerequisites](#prerequisites)
  - [Environment Configuration](#environment-configuration)
  - [Database Setup](#database-setup)
  - [Running Locally with Docker Compose](#running-locally-with-docker-compose)
  - [Running with Kubernetes (minikube)](#running-with-kubernetes-minikube)
  - [Running Tests](#running-tests)
- [Deployment Information](#deployment-information)
  - [Live URL](#live-url)
  - [Fly.io Deployment](#flyio-deployment)
  - [DigitalOcean Kubernetes Deployment](#digitalocean-kubernetes-deployment)
- [Architecture](#architecture)
  - [System Architecture Diagram](#system-architecture-diagram)
  - [Database Schema](#database-schema)
  - [API Endpoints](#api-endpoints)
- [AI Assistance & Verification (Summary)](#ai-assistance--verification-summary)
- [Individual Contributions](#individual-contributions)
- [Lessons Learned and Concluding Remarks](#lessons-learned-and-concluding-remarks)

---

## Team Information

| Name | Student Number | Email |
|------|---------------|-------|
| [Member 1 Name] | [Student Number] | [email@mail.utoronto.ca] |
| [Member 2 Name] | [Student Number] | [email@mail.utoronto.ca] |

**Programming Language:** Python (backend), TypeScript (frontend)

Credentials sent to TA.

---

## Video Demo

🎬 **[Video Demo Link — TODO: Insert YouTube/Google Drive URL here]**

The demo showcases: user authentication and role-based access, full inventory CRUD operations, real-time WebSocket stock updates, the monitoring dashboard (Prometheus + Grafana), Kubernetes orchestration with service replication, serverless low-stock email notifications, edge routing across Fly.io regions, and the application running in the deployed cloud environment.

---

## Motivation

Inventory management is a critical operational challenge faced by businesses of all sizes, from small retail shops to large warehouses. Poor inventory tracking leads to stockouts, overstocking, lost revenue, and operational inefficiency. While enterprise solutions exist (SAP, Oracle), they are expensive, complex, and impractical for small-to-medium businesses.

This project addresses the need for a lightweight, cloud-native inventory management system that provides real-time stock visibility, automated alerts for low-stock conditions, and multi-location support — all deployed on modern cloud infrastructure with high availability and low-latency access.

**Target users** include warehouse managers who need centralized stock visibility across locations, retail staff who perform daily stock-in and stock-out operations, and operations teams who require dashboards and alerts to prevent stockouts.

By building this as a cloud-native application on Fly.io with Kubernetes orchestration, we demonstrate how modern cloud and edge computing technologies can deliver a responsive, scalable, and resilient inventory system at minimal cost.

---

## Objectives

The primary objective is to design, implement, and deploy a stateful, cloud-native inventory management system that applies core concepts from ECE 1779 — containerization, orchestration, persistent storage, monitoring, and edge deployment.

Specifically, the project aims to:

1. Build a fully containerized multi-service application using Docker and Docker Compose, with a Python/FastAPI backend, PostgreSQL database, Redis message broker, and a Next.js frontend.

2. Implement Kubernetes orchestration using minikube for local development and DigitalOcean Managed Kubernetes for production, including Deployments, Services, StatefulSets, and PersistentVolumeClaims.

3. Deploy the application to Fly.io with persistent volumes for PostgreSQL data durability, ensuring state survives container restarts and redeployments.

4. Integrate comprehensive monitoring and observability through Fly.io built-in metrics, Prometheus for application-level metrics, and Grafana dashboards with alerting rules.

5. Implement at least three advanced features: real-time WebSocket stock updates, serverless email notifications for low-stock alerts, and edge-optimized routing for low-latency global access.

6. Deliver a polished, functional application with role-based access control (Manager/Staff), full CRUD operations, search and filtering, and an audit trail of all inventory changes.

---

## Technical Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend API | Python 3.12 + FastAPI | Async REST API and WebSocket server |
| Database | PostgreSQL 16 | Relational data persistence (course requirement) |
| ORM / Migrations | SQLAlchemy 2.0 + Alembic | Type-safe database access and schema versioning |
| Authentication | JWT (PyJWT) + bcrypt | Stateless token-based auth with password hashing |
| Real-time | FastAPI WebSockets + Redis Pub/Sub | Live stock update broadcasting across replicas |
| Message Broker | Redis 7 | WebSocket event distribution for multi-replica |
| Containerization | Docker + Docker Compose | Multi-container local development environment |
| Orchestration | Kubernetes (minikube / DO Managed K8s) | Service replication, load balancing, rolling updates |
| Cloud Deployment | Fly.io | Edge-optimized PaaS with persistent volumes |
| Monitoring | Prometheus + Grafana + Fly.io Metrics | Application and infrastructure observability |
| Serverless | DigitalOcean Functions | Event-driven low-stock email notifications |
| Email Service | SendGrid API | Transactional email delivery |
| CI/CD | GitHub Actions | Automated testing, building, and deployment |
| Frontend | Next.js 14 (React + TypeScript) | Dashboard UI for inventory management |

---

## Features

### Core Technical Requirements

All core requirements mandated by the course project guidelines are fully implemented:

**Containerization and Local Development** — The entire application is containerized with Docker. Each service (API, WebSocket server, frontend, PostgreSQL, Redis, Prometheus, Grafana) has its own Dockerfile with multi-stage builds to minimize image size. Docker Compose orchestrates all seven services for local development with a single `docker compose up` command.

**State Management with PostgreSQL** — PostgreSQL 16 serves as the primary relational database, managing all application data including users, inventory items, categories, locations, audit logs, and alerts. Alembic handles database schema migrations. Persistent storage is configured through Fly.io Volumes (for cloud deployment) and Kubernetes PersistentVolumeClaims (for K8s deployment), ensuring data survives container restarts and redeployments.

**Deployment on Fly.io** — The application is deployed to Fly.io as the primary cloud provider. The API and WebSocket services run as separate Fly Machines with auto-start capabilities. PostgreSQL data is persisted on Fly Volumes mounted to the database container. HTTPS is enforced via Fly.io's built-in TLS termination.

**Kubernetes Orchestration (Option B)** — Kubernetes is used for orchestration with minikube for local development and DigitalOcean Managed Kubernetes for production. The setup includes Deployments with replica scaling for the API service (3 replicas), a StatefulSet for PostgreSQL with a PersistentVolumeClaim, Services for internal networking and external LoadBalancer access, Secrets for credential management, and liveness/readiness probes for health monitoring.

**Monitoring and Observability** — A three-layer monitoring approach is implemented. Fly.io provides infrastructure-level metrics (CPU, memory, disk) and log aggregation. Prometheus scrapes application-level metrics from the `/metrics` endpoint, including custom gauges for inventory levels and WebSocket connections. Grafana visualizes all metrics through pre-configured dashboards for system health, inventory overview, and API performance. Alerting rules trigger notifications for high error rates, elevated latency, and critical low-stock levels.

### Advanced Features

Three advanced features are implemented (course minimum: two):

**1. Real-Time Functionality (WebSockets)** — When any user creates, updates, or deletes an inventory item or performs a restock/withdrawal, the change is broadcast in real time to all connected clients via WebSockets. The implementation uses FastAPI's native WebSocket support with Redis Pub/Sub as the message broker, enabling consistent event delivery across multiple API replicas. Events include `item_created`, `item_updated`, `item_deleted`, `stock_changed`, and `low_stock_alert`.

**2. Serverless Email Notifications** — A serverless function deployed on DigitalOcean Functions monitors stock levels and sends email alerts via SendGrid when an item's quantity drops below its configured threshold. The function is triggered by an HTTP POST from the API service whenever a stock withdrawal or update causes a low-stock condition. Alert records are stored in the database and can be viewed and acknowledged by managers through the UI.

**3. Edge-Specific Optimizations** — The application is deployed across multiple Fly.io regions (Toronto `yyz`, Virginia `iad`, London `lhr`) with automatic region-based routing. Fly.io directs each request to the nearest healthy instance for minimal latency. Write operations that arrive at read-replica regions are automatically replayed to the primary region using Fly.io's `fly-replay` header mechanism, ensuring data consistency while maintaining read performance globally.

### Application Features

Beyond the cloud infrastructure requirements, the application provides a complete inventory management workflow:

- **Role-based access control** with Manager and Staff roles, each with distinct permissions
- **Full CRUD operations** for inventory items, categories, and locations
- **Restock and withdrawal** operations with quantity validation
- **Search and filtering** by item name, SKU, category, location, and quantity range
- **Low-stock threshold** configuration per item with automated alerting
- **Audit trail** logging every inventory change with user attribution and timestamps
- **Dashboard** with summary statistics, category breakdowns, and recent activity
- **User management** for managers to create and manage staff accounts

---

## User Guide

### 1. Authentication

Navigate to the application URL to reach the login page. Enter your email and password to log in. Upon first deployment, a default manager account is created with the credentials specified in the environment configuration.

After successful login, you receive a JWT token that is stored in the browser and automatically included in all subsequent requests. The token expires after 1 hour, with automatic refresh support.

<!-- ![Login Page](screenshots/login.png) -->

**Registering new users:** Managers can create new user accounts by navigating to the Users page and clicking "Add User." Specify the user's email, name, and role (Manager or Staff).

### 2. Dashboard

The dashboard is the landing page after login. It displays four summary cards showing total inventory items, total stock units, number of low-stock items requiring attention, and number of unacknowledged alerts.

Below the summary cards, a category breakdown chart shows the distribution of items across categories, and a recent activity feed displays the latest inventory changes with timestamps and user attribution.

<!-- ![Dashboard](screenshots/dashboard.png) -->

### 3. Inventory Management

**Viewing items:** Navigate to the Inventory page to see all items in a sortable, paginated table. Each row shows the item name, SKU, category, location, current quantity, unit, price, and low-stock threshold. Items with quantity below their threshold are highlighted in red.

<!-- ![Inventory List](screenshots/inventory-list.png) -->

**Creating a new item (Manager only):** Click "Add Item" to open the creation form. Fill in the required fields: name, SKU, description, category, location, initial quantity, unit, price, and low-stock threshold. Click "Save" to create the item. A WebSocket event notifies all connected users of the new item.

<!-- ![Create Item](screenshots/create-item.png) -->

**Updating an item (Manager only):** Click on any item row to open the detail page. Click "Edit" to modify item fields. Save changes to broadcast a real-time update.

**Restocking (Staff and Manager):** On the item detail page, click "Restock" and enter the quantity to add. The system validates the input, updates the quantity, and logs the change in the audit trail.

**Withdrawing stock (Staff and Manager):** Click "Withdraw" on the item detail page and enter the quantity to remove. The system ensures the withdrawal does not exceed available stock. If the resulting quantity falls below the low-stock threshold, a serverless alert is triggered.

<!-- ![Item Detail](screenshots/item-detail.png) -->

**Deleting an item (Manager only):** On the item detail page, click "Delete" and confirm the action. The item is soft-deleted and a notification is broadcast to all connected clients.

### 4. Search and Filtering

The inventory list supports multiple filtering options accessible from the filter bar above the table:

- **Text search:** Type in the search box to filter items by name or SKU (case-insensitive partial match).
- **Category filter:** Select a category from the dropdown to show only items in that category.
- **Location filter:** Select a location to filter items by warehouse or storage area.
- **Quantity range:** Set minimum and/or maximum quantity values.
- **Low-stock only:** Toggle to show only items currently below their threshold.
- **Sort:** Click any column header to sort ascending/descending by that field.

All filters can be combined. Results update in real time as filters are applied.

<!-- ![Search and Filter](screenshots/search-filter.png) -->

### 5. Categories and Locations

**Categories** and **Locations** are managed via their respective pages, accessible from the sidebar navigation. Managers can create, edit, and delete categories and locations. Each category and location shows the count of items assigned to it.

### 6. Low-Stock Alerts

When an item's quantity drops below its configured `low_stock_threshold`, the system automatically triggers a serverless function that sends an email to all Manager users via SendGrid. The email includes the item name, current quantity, threshold value, location, and a direct link to the item in the application.

Alerts are also displayed in the application on the Alerts page. Each alert shows the item, the alert message, the timestamp, and whether it has been acknowledged. Managers can click "Acknowledge" to mark an alert as handled.

<!-- ![Alerts Page](screenshots/alerts.png) -->

### 7. Real-Time Updates

All connected users receive live updates when inventory changes occur. A WebSocket connection indicator in the navigation bar shows the connection status (green = connected, red = disconnected). When a change occurs, a toast notification appears briefly showing the event type (e.g., "Widget A restocked: 50 → 100 units by john@example.com"). The inventory table and dashboard update automatically without requiring a page refresh.

<!-- ![Real-Time Toast](screenshots/realtime-toast.png) -->

### 8. User Management (Manager Only)

Navigate to the Users page to view all registered users. Managers can create new user accounts, assign roles (Manager or Staff), activate/deactivate accounts, and view each user's activity history.

---

## Development Guide

### Prerequisites

Ensure the following tools are installed on your development machine:

- **Docker** (v24+) and **Docker Compose** (v2.20+): [Install Docker](https://docs.docker.com/get-docker/)
- **Python 3.12+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 20+** and **npm**: [Download Node.js](https://nodejs.org/)
- **minikube** (for Kubernetes local dev): [Install minikube](https://minikube.sigs.k8s.io/docs/start/)
- **kubectl**: [Install kubectl](https://kubernetes.io/docs/tasks/tools/)
- **Fly CLI** (`flyctl`): [Install flyctl](https://fly.io/docs/getting-started/installing-flyctl/)
- **Git**: [Install Git](https://git-scm.com/)

### Environment Configuration

1. Clone the repository:

```bash
git clone https://github.com/[your-username]/inventory-management-system.git
cd inventory-management-system
```

2. Create a `.env` file in the project root by copying the template:

```bash
cp .env.example .env
```

3. Configure the required environment variables in `.env`:

```env
# Database
POSTGRES_USER=inventory
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=inventory_db
DATABASE_URL=postgresql://inventory:your_secure_password@postgres:5432/inventory_db

# Authentication
JWT_SECRET=your_very_long_random_jwt_secret_key_min_32_chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Default Manager Account (created on first run)
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=securepassword123
DEFAULT_ADMIN_NAME=System Admin

# Redis
REDIS_URL=redis://redis:6379

# SendGrid (for email notifications)
SENDGRID_API_KEY=your_sendgrid_api_key
ALERT_FROM_EMAIL=alerts@your-domain.com

# Serverless Function URL (DigitalOcean Functions)
LOW_STOCK_FUNCTION_URL=https://faas-tor1-xxx.doserverless.co/api/v1/web/fn-xxx/alerts/low_stock

# Fly.io Region Routing
PRIMARY_REGION=yyz
```

### Database Setup

Database migrations are managed by Alembic. When using Docker Compose, migrations run automatically on container startup. For manual setup:

```bash
cd backend

# Create a Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# (Optional) Seed sample data
python scripts/seed-data.py
```

### Running Locally with Docker Compose

This is the recommended way to run the full application locally:

```bash
# Build and start all services
docker compose up --build

# Or run in detached mode
docker compose up --build -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Stop and remove all data volumes (clean slate)
docker compose down -v
```

Once running, the services are available at:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| WebSocket | ws://localhost:8001/ws |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 (admin/admin) |
| PostgreSQL | localhost:5432 |

### Running with Kubernetes (minikube)

For testing orchestration locally:

```bash
# Start minikube
minikube start --cpus=4 --memory=4096

# Point Docker to minikube's daemon
eval $(minikube docker-env)

# Build images inside minikube
docker build -t inventory-api:latest ./backend
docker build -t inventory-frontend:latest ./frontend

# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/secrets.yml
kubectl apply -f k8s/postgres-statefulset.yml
kubectl apply -f k8s/redis-deployment.yml
kubectl apply -f k8s/api-deployment.yml
kubectl apply -f k8s/ws-deployment.yml
kubectl apply -f k8s/frontend-deployment.yml
kubectl apply -f k8s/monitoring/

# Check pod status
kubectl get pods -n inventory

# Access the API via minikube service
minikube service inventory-api -n inventory

# View logs
kubectl logs -f deployment/inventory-api -n inventory

# Scale the API
kubectl scale deployment/inventory-api --replicas=5 -n inventory

# Clean up
kubectl delete namespace inventory
minikube stop
```

### Running Tests

```bash
cd backend

# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests with coverage
pytest --cov=app tests/ -v

# Run specific test files
pytest tests/test_auth.py -v
pytest tests/test_items.py -v
pytest tests/test_websocket.py -v

# Run with HTML coverage report
pytest --cov=app --cov-report=html tests/
# Open htmlcov/index.html in browser
```

---

## Deployment Information

### Live URL

🌐 **Application:** [https://inventory-app.fly.dev](https://inventory-app.fly.dev)  
🔌 **API:** [https://inventory-api.fly.dev](https://inventory-api.fly.dev)  
📄 **API Docs:** [https://inventory-api.fly.dev/docs](https://inventory-api.fly.dev/docs)  

> *Note: The deployment will remain online during the grading period. Contact the team if the application is temporarily unavailable.*

### Fly.io Deployment

The application is deployed to Fly.io with the following configuration:

```bash
# Authenticate with Fly.io
fly auth login

# Launch the API service
cd backend
fly launch --name inventory-api --region yyz

# Create a persistent volume for PostgreSQL
fly volumes create pg_data --region yyz --size 1

# Set secrets
fly secrets set DATABASE_URL="..." JWT_SECRET="..." SENDGRID_API_KEY="..."

# Deploy
fly deploy

# Scale to multiple regions
fly regions add iad lhr
fly scale count 3

# View logs
fly logs

# Check status
fly status
```

**Fly.io configuration** (`fly.toml`):

```toml
app = "inventory-api"
primary_region = "yyz"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"
  PRIMARY_REGION = "yyz"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[checks]
  [checks.health]
    type = "http"
    port = 8000
    path = "/health"
    interval = "30s"
    timeout = "5s"

[mounts]
  source = "pg_data"
  destination = "/var/lib/postgresql/data"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

### DigitalOcean Kubernetes Deployment

For production Kubernetes deployment on DigitalOcean:

```bash
# Configure kubectl to use DO cluster
doctl kubernetes cluster kubeconfig save inventory-cluster

# Push images to registry
docker tag inventory-api:latest registry.digitalocean.com/inventory/api:latest
docker push registry.digitalocean.com/inventory/api:latest

# Apply production manifests
kubectl apply -f k8s/

# Verify deployment
kubectl get all -n inventory
```

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                           CLIENTS                               │
│          Browser (Next.js)  /  REST API consumers               │
└──────────────┬──────────────────────────┬───────────────────────┘
               │ HTTPS                    │ WSS
               ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Fly.io Edge Network                        │
│         Regions: yyz (Toronto), iad (Virginia), lhr (London)    │
│              TLS termination  /  Region-based routing            │
└──────────────┬──────────────────────────┬───────────────────────┘
               │                          │
               ▼                          ▼
┌──────────────────────────────────────────────────────────────────┐
│            Kubernetes Cluster (DigitalOcean Managed K8s)         │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐   │
│  │   API Service    │  │  WS Service     │  │   Frontend     │   │
│  │   (FastAPI)      │  │  (FastAPI WS)   │  │   (Next.js)    │   │
│  │   Replicas: 3    │  │  Replicas: 2    │  │   Replicas: 2  │   │
│  └────────┬─────────┘  └────────┬────────┘  └────────────────┘   │
│           │                     │                                 │
│           ▼                     ▼                                 │
│  ┌─────────────────┐  ┌─────────────────┐                       │
│  │   PostgreSQL     │  │     Redis       │                       │
│  │  (StatefulSet)   │  │   (Pub/Sub)     │                       │
│  │  + PVC (5Gi)     │  │                 │                       │
│  └─────────────────┘  └─────────────────┘                       │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐                       │
│  │   Prometheus     │  │    Grafana      │                       │
│  │   (Metrics)      │  │  (Dashboards)   │                       │
│  └─────────────────┘  └─────────────────┘                       │
│                                                                  │
│  ┌─────────────────┐                                             │
│  │  Backup CronJob  │ ──── pg_dump daily → DO Spaces             │
│  └─────────────────┘                                             │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    Serverless (DO Functions)                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Low-Stock Alert Function                                  │  │
│  │  Trigger: HTTP POST from API on stock below threshold      │  │
│  │  Action: Send email via SendGrid to Manager(s)             │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    CI/CD (GitHub Actions)                         │
│  push to main → pytest → Docker build → Push image → fly deploy  │
└──────────────────────────────────────────────────────────────────┘
```

### Database Schema

The application uses six PostgreSQL tables:

**`users`** — Stores user accounts with email, bcrypt-hashed password, full name, role (`manager` or `staff`), and active status.

**`categories`** — Inventory categories (e.g., Electronics, Raw Materials, Office Supplies) with name and description.

**`locations`** — Physical storage locations (e.g., Warehouse A, Shelf B-3) with name, description, and address.

**`items`** — The core inventory table. Each item has a unique SKU, name, description, foreign keys to category and location, current quantity, unit of measurement, price, and a configurable `low_stock_threshold`. Timestamps track creation and last update.

**`inventory_logs`** — An immutable audit trail recording every inventory change. Each log entry records the item, the user who made the change, the action type (`create`, `update`, `delete`, `restock`, `withdraw`), the quantity before and after, optional notes, and a timestamp.

**`alerts`** — Records of low-stock alerts that have been triggered, including the item, alert message, recipient email, send timestamp, and acknowledgment status.

All tables use appropriate indexes on foreign keys, SKU, quantity, and timestamp columns for query performance.

### API Endpoints

**Authentication:**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/api/v1/auth/register` | Register a new user | Manager |
| `POST` | `/api/v1/auth/login` | Authenticate and receive JWT | Public |
| `POST` | `/api/v1/auth/refresh` | Refresh an expired token | Authenticated |
| `GET` | `/api/v1/auth/me` | Get current user profile | Authenticated |

**Inventory Items:**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/v1/items` | List items with search, filter, pagination | Staff+ |
| `GET` | `/api/v1/items/{id}` | Get item details | Staff+ |
| `POST` | `/api/v1/items` | Create a new item | Manager |
| `PUT` | `/api/v1/items/{id}` | Update an item | Manager |
| `PATCH` | `/api/v1/items/{id}` | Partial update | Staff+ |
| `DELETE` | `/api/v1/items/{id}` | Delete an item | Manager |
| `POST` | `/api/v1/items/{id}/restock` | Add stock quantity | Staff+ |
| `POST` | `/api/v1/items/{id}/withdraw` | Remove stock quantity | Staff+ |

**Categories and Locations:**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/v1/categories` | List all categories | Staff+ |
| `POST` | `/api/v1/categories` | Create a category | Manager |
| `PUT` | `/api/v1/categories/{id}` | Update a category | Manager |
| `DELETE` | `/api/v1/categories/{id}` | Delete a category | Manager |
| `GET` | `/api/v1/locations` | List all locations | Staff+ |
| `POST` | `/api/v1/locations` | Create a location | Manager |
| `PUT` | `/api/v1/locations/{id}` | Update a location | Manager |
| `DELETE` | `/api/v1/locations/{id}` | Delete a location | Manager |

**Logs, Alerts, and Dashboard:**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/v1/logs` | List all inventory change logs | Manager |
| `GET` | `/api/v1/logs/item/{id}` | Get logs for a specific item | Staff+ |
| `GET` | `/api/v1/alerts` | List all alerts | Manager |
| `PATCH` | `/api/v1/alerts/{id}/acknowledge` | Acknowledge an alert | Manager |
| `GET` | `/api/v1/dashboard/summary` | Dashboard summary statistics | Staff+ |
| `GET` | `/api/v1/dashboard/category-breakdown` | Items per category | Staff+ |

**System:**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/health` | Health check for K8s probes | Public |
| `GET` | `/metrics` | Prometheus metrics endpoint | Internal |
| `WSS` | `/ws?token=<JWT>` | WebSocket for real-time updates | Authenticated |

**Query parameters for `GET /api/v1/items`:** `search` (name/SKU text search), `category_id`, `location_id`, `min_quantity`, `max_quantity`, `below_threshold` (boolean), `sort_by` (name, quantity, updated_at, price), `order` (asc/desc), `page`, `per_page`.

---

## AI Assistance & Verification (Summary)

AI tools (primarily Claude) were used during the development of this project in the following areas:

**Where AI meaningfully contributed:** AI assisted with initial system architecture exploration (evaluating Docker Swarm vs. Kubernetes trade-offs for this project), generating Kubernetes YAML manifests (Deployments, StatefulSets, PVCs, Services), debugging Docker Compose networking issues between services, and drafting Prometheus alerting rules and Grafana dashboard configurations.

**One representative AI mistake:** When configuring the Fly.io deployment with Kubernetes orchestration, AI initially suggested using Fly Kubernetes Service (FKS) as the primary orchestration layer. This was incorrect — FKS is a paid beta feature ($75/month) with limited documentation, and the course guidelines explicitly warn against it. Our team identified this error by cross-referencing with the project guidelines and Fly.io documentation, and instead implemented the recommended approach of minikube locally with DigitalOcean Managed Kubernetes for production. Full details of this interaction are documented in `ai-session.md`.

**How correctness was verified:** All AI-generated configurations were validated through multiple methods: Docker Compose services were tested with `docker compose up` and verified via health checks; Kubernetes manifests were validated with `kubectl apply --dry-run=client` before deployment; API endpoints were tested with automated pytest suites achieving >80% coverage; WebSocket functionality was verified through integration tests and manual multi-client testing; monitoring accuracy was confirmed by comparing Prometheus metrics against known database state; and deployment was validated by accessing the live Fly.io URL and confirming all features work end-to-end.

For concrete examples of AI interactions, corrections, and verification steps, see [`ai-session.md`](ai-session.md).

---

## Individual Contributions

### [Member 1 Name]

- Designed and implemented the backend API (FastAPI application structure, all route handlers, Pydantic schemas, and business logic services)
- Implemented JWT authentication and role-based access control middleware
- Set up PostgreSQL database schema and Alembic migrations
- Implemented WebSocket real-time update system with Redis Pub/Sub
- Configured Prometheus metrics endpoint and custom application metrics
- Wrote backend unit and integration tests
- Authored the final report and `ai-session.md`

**Key commits:** `feat(api): implement item CRUD endpoints`, `feat(auth): add JWT auth with RBAC`, `feat(ws): real-time WebSocket updates with Redis pub/sub`, `feat(metrics): add Prometheus custom metrics`

### [Member 2 Name]

- Designed and built the Next.js frontend (all pages, components, and hooks)
- Created all Docker and Docker Compose configurations (multi-stage builds)
- Authored all Kubernetes manifests (Deployments, StatefulSets, Services, PVCs, Secrets)
- Configured and deployed the application to Fly.io (fly.toml, volumes, multi-region setup)
- Set up Grafana dashboards and alerting rules
- Implemented the serverless low-stock notification function on DigitalOcean Functions
- Configured the CI/CD pipeline with GitHub Actions
- Implemented automated database backup via Kubernetes CronJob

**Key commits:** `feat(frontend): build inventory dashboard and CRUD pages`, `infra(docker): multi-stage Dockerfiles and compose setup`, `infra(k8s): complete Kubernetes manifests`, `infra(fly): deploy to Fly.io with persistent volumes`, `feat(serverless): low-stock email alert function`

---

## Lessons Learned and Concluding Remarks

**Kubernetes has a steep learning curve but pays off.** Setting up Kubernetes manifests for the first time — especially StatefulSets with PersistentVolumeClaims for PostgreSQL — required significant debugging. Pods would crash-loop due to permission issues on mounted volumes, and service discovery between pods took trial and error to configure correctly. However, once the configuration was working, the ability to scale replicas with a single command (`kubectl scale`) and perform rolling updates with zero downtime demonstrated the clear value of orchestration.

**Docker Compose and Kubernetes serve different purposes well.** Docker Compose was invaluable for rapid local development — a single `docker compose up` brings the entire stack online in seconds. Kubernetes, while more complex, provided production-grade features like health checks, automatic restarts, and load balancing that Docker Compose cannot replicate. Using both in the same project gave us practical experience with the full development-to-deployment lifecycle.

**Real-time features add complexity at scale.** Implementing WebSockets was straightforward for a single server instance, but became more challenging when scaling to multiple replicas. Without Redis Pub/Sub as a message broker, events would only reach clients connected to the same replica that processed the change. This experience reinforced the importance of designing for distributed systems from the start.

**Fly.io's edge network simplifies global deployment.** Deploying to multiple regions was remarkably straightforward with Fly.io — a few CLI commands and a `fly.toml` change. The automatic region-based routing and `fly-replay` header for write forwarding handled the complexity of geo-distributed deployment without requiring us to implement a custom solution.

**Monitoring is not optional.** During development, Prometheus and Grafana dashboards helped us identify a memory leak in the WebSocket connection manager (connections were not being properly cleaned up on client disconnect). Without monitoring, this issue would have gone unnoticed until production. This experience reinforced that observability should be integrated from the beginning, not added as an afterthought.

**AI tools are powerful but require critical evaluation.** AI-generated code and configurations often worked for common use cases but failed on project-specific constraints (e.g., the FKS suggestion that contradicted course guidelines). The most productive AI interactions were those where we provided clear context and then critically evaluated the output against documentation and testing results. The least productive interactions occurred when we accepted AI output without verification.

In conclusion, this project provided hands-on experience with the full cloud-native development stack — from containerization and orchestration to monitoring, edge deployment, and serverless computing. The Inventory Management System demonstrates that modern cloud infrastructure makes it feasible to build and deploy resilient, globally distributed applications even with a small team, provided the scope is well-defined and the core technologies are thoroughly understood.

---

*Last updated: April 4, 2026*