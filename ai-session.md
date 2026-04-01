# AI Session Log — Inventory Management System

## Tools Used
- **Claude Code** (Anthropic CLI) — primary AI assistant for code generation, debugging, architecture, and deployment

---

## Session 1: Backend MVP
**Goal:** Scaffold the entire FastAPI backend from scratch.

**What AI did:**
- Generated project structure: models, schemas, routers, services, middleware
- Implemented SQLAlchemy ORM models (User, Item, Category, Location, InventoryLog, Alert)
- Created JWT authentication with role-based access control (manager/staff)
- Built full CRUD API for inventory items with pagination, filtering, sorting
- Set up Alembic migrations for PostgreSQL schema
- Created Dockerfile and Docker Compose configuration

**Human input:** Defined the data model requirements, API endpoints needed, and role permissions.

---

## Session 2: Frontend Development
**Goal:** Build a Next.js frontend for inventory management.

**What AI did:**
- Created login page, dashboard, and inventory CRUD page
- Implemented Axios API client with JWT token interceptor
- Built inventory table with search, filter, sort, pagination
- Added restock/withdraw modals with quantity inputs
- Created category and location management within inventory page

**Human input:** UI layout preferences, feature prioritization, page navigation flow.

---

## Session 3: Infrastructure & Deployment
**Goal:** Deploy to Fly.io and set up Kubernetes on minikube.

**What AI did:**
- Wrote fly.toml configs for backend and frontend apps
- Created 10 Kubernetes manifests (namespace, secrets, deployments, StatefulSet, services, CronJob, monitoring)
- Configured 3 API replicas, 2 frontend replicas, 2 WebSocket replicas
- Set up PostgreSQL StatefulSet with 5Gi PersistentVolumeClaim
- Created GitHub Actions CI/CD pipelines (test.yml, deploy.yml)
- Wrote deployment runbook (DEPLOY_RUNBOOK.md)

**Human input:** Cloud provider choice (Fly.io), region selection (yyz), replica counts, resource limits.

---

## Session 4: WebSocket Real-Time Notifications
**Goal:** Add real-time alerts for inventory changes.

**What AI did:**
- Implemented WebSocket endpoint with FastAPI
- Created React hook (useWebSocket.ts) for client-side WS connection with auto-reconnect
- Built AlertToast component for low_stock_alert, item_restocked, item_withdrawn events
- Initially used in-memory broadcast (broken on multi-worker Fly.io)

**Bug found by human:** Notifications not appearing on cloud deployment — two Fly machines each had separate in-memory connection lists.

**What AI did to fix:**
- Rewrote ws_manager.py to use Redis pub/sub for cross-worker broadcast
- Each worker subscribes to Redis channel, publishes events to Redis instead of local broadcast
- Added auto-reconnect logic for Upstash Redis idle timeout (connection reset)
- Added retry-with-fresh-connection pattern in publish()

**Human input:** Identified the bug (notifications missing on cloud), confirmed fix worked after each iteration.

---

## Session 5: UI Bug Fixes
**Goal:** Fix visual issues in the frontend.

**Bugs identified by human:**
1. Withdraw notification toast had no color
2. All text turned invisible (not black)

**What AI did:**
1. Diagnosed Tailwind CSS purging dynamic class names (e.g., `bg-yellow-600` in template literals). Fixed by switching to inline `style={{ backgroundColor: "#ca8a04" }}` with hex values.
2. Found dark mode `@media (prefers-color-scheme: dark)` in globals.css setting `--foreground: #ededed` (near-white) against light backgrounds. Removed the dark mode block entirely.

---

## Session 6: Email Subscription System
**Goal:** Allow users to subscribe to inventory event emails.

**What AI did:**
- Created EmailSubscription model and Alembic migration
- Built CRUD service with get_subscribers_for_event() query
- Created REST API with RBAC (any user: own subscriptions, manager: all)
- Built frontend page with subscribe form and subscription management table
- Integrated SendGrid email service (logs if no API key configured)
- Wired into item_service.py emit_ws_event() to also trigger emails

**Human input:** Feature requirements, decided to defer actual email sending (no SendGrid key), kept the subscription management UI.

---

## Session 7: User Registration & Employee Management
**Goal:** Add public signup and employee management for managers.

**What AI did:**
- Added `/api/v1/auth/signup` public endpoint (no auth required)
- Added `DELETE /api/v1/users/{id}` with manager-only guard and self-deletion prevention
- Rewrote login page with login/signup toggle, role selection (Worker/Manager radio buttons)
- Created employees page with table (ID, Name, Email, Role badge, Status, Join Date)
- Added Remove button with confirmation dialog

**Human input:** Specified the form fields (first name, last name, email, password, role), UX flow (toggle on login page), employee page requirements.

---

## Session 8: Monitoring — Prometheus & Grafana
**Goal:** Set up observability dashboards.

**What AI did:**
- Configured prometheus-fastapi-instrumentator for /metrics endpoint
- Created Grafana provisioning configs (datasources, dashboards)
- Built 12-panel Grafana dashboard JSON:
  - API Instances Up, Requests In Progress, Total Requests, Error Rate (5xx)
  - HTTP Request Rate by handler, Response Status Codes
  - Request Duration p95 and p50
  - Process Memory RSS, CPU Usage
  - Python GC Collections Rate, Open File Descriptors
- Fixed hardcoded datasource UID issue (switched to `{"type": "prometheus"}` default)
- Added dashboard volume mount in docker-compose.yml
- Configured Prometheus scraping on both Docker Compose and minikube

**Human input:** Verified dashboards loaded correctly, identified missing datasource provisioning.

---

## Session 9: Serverless & Multi-Region
**Goal:** Enable scale-to-zero and multi-region deployment on Fly.io.

**What AI did:**
- Updated fly.toml: `auto_stop_machines = true`, `min_machines_running = 0` for both apps
- Ran `fly scale count 1 --region iad` to add US East machines for both backend and frontend
- Result: 3 backend machines (yyz x2, iad x1), 3 frontend machines (yyz x2, iad x1)

**Human input:** Confirmed multi-region approach, chose iad as second region.

---

## Session 10: Demo Script
**Goal:** Create a live demo shell script for the course presentation.

**What AI did:**
- Wrote demo.sh with 10 sections split into Core Features and Advanced Features
- Each section runs real commands (docker compose ps, kubectl get pods, curl, fly scale show, etc.)
- Added `run_cmd` helper that prints `$ command` before executing to prove commands are live
- Added Fly.io machine warm-up at script start (background curl to wake scale-to-zero machines)
- Fixed `set -e` crash when `grep` returned no match (added `|| true`)
- Interactive pauses between sections for presenter control

**Human input:** Requested sections be organized as "Core" vs "Advanced", asked for command visibility to prove output isn't hardcoded, identified script crashes and requested fixes.

---

## Summary of AI Contribution

| Area | AI Contribution | Human Contribution |
|---|---|---|
| Backend code | ~90% generated, ~10% directed modifications | Requirements, data model design, bug reports |
| Frontend code | ~85% generated | UI preferences, UX flow, bug identification |
| Infrastructure | ~95% generated (K8s, Docker, CI/CD, fly.toml) | Cloud provider choice, region selection |
| Debugging | Diagnosed root causes, wrote fixes | Identified symptoms, tested fixes |
| Monitoring | 100% dashboard and provisioning config | Verified dashboards loaded correctly |
| Demo script | ~90% generated | Section organization, crash reports, UX feedback |

**Total estimated AI-assisted code:** ~12,000+ lines across Python, TypeScript, YAML, JSON, and Shell.
