# ECE 1779 Course Project Proposal: Cloud-Native Inventory Management System

**Team Members:** [Wenxi Chen] (1003795761), [Huiying Yu] (1012487667), [Jinghan Song] (1005992204), [Xuhui Zhang] (1007287482)

---

## 1. Motivation

Inventory management is a fundamental operational challenge for businesses ranging from small retail shops to mid-sized warehouses. Inaccurate stock tracking leads to stockouts, overstocking, and wasted staff time on manual counting — problems that cost retailers nearly $1.8 trillion globally each year.

While enterprise solutions like SAP and Oracle NetSuite exist, they are expensive and impractical for small-to-medium businesses (SMBs). Many SMBs still rely on spreadsheets, which are error-prone and offer no real-time visibility. Open-source alternatives like InvenTree require self-hosted servers and lack cloud-native features such as auto-scaling and automated alerting.

Our project addresses this gap by building a **lightweight, cloud-native inventory management system** that provides real-time stock visibility, automated low-stock email alerts, and multi-location support — all deployed on modern edge infrastructure for low-latency global access.

**Target users** include:

- **Warehouse managers** who need centralized stock visibility across multiple storage locations and want automated alerts when items run low.
- **Retail and warehouse staff** who perform daily stock-in and stock-out operations and need a fast, intuitive interface that updates in real time.
- **Operations teams** in SMBs who require dashboards to monitor inventory health without investing in enterprise-grade ERP software.

This project is worth pursuing because it directly applies core ECE 1779 concepts — containerization, orchestration, persistent storage, monitoring, and edge deployment — to a practical, real-world problem that benefits clearly defined users.

---

## 2. Objective and Key Features

### Objective

Design, implement, and deploy a stateful, cloud-native inventory management system demonstrating mastery of cloud computing principles from ECE 1779. The system will support full inventory lifecycle management with role-based access, real-time updates, automated alerting, and comprehensive monitoring — deployed on containerized, orchestrated edge infrastructure.

### Core Technical Requirements

**Containerization and Local Development:** Every service will be containerized with Docker using multi-stage builds. A `docker-compose.yml` file will orchestrate the full local stack: Python/FastAPI API server, PostgreSQL database, Redis message broker, and Prometheus/Grafana monitoring.

**State Management with PostgreSQL:** PostgreSQL 16 will serve as the primary relational database. We will use SQLAlchemy 2.0 as the ORM and Alembic for schema migrations. The schema includes six tables: `users` (authentication and roles), `items` (core inventory with SKU, quantity, category, location, and low-stock threshold), `categories`, `locations`, `inventory_logs` (immutable audit trail), and `alerts` (notification records).

**Persistent Storage:** PostgreSQL data will be stored on Fly.io Volumes (cloud) and Kubernetes PersistentVolumeClaims (orchestrated environment), ensuring state survives container restarts and redeployments.

**Deployment on Fly.io:** The application will be deployed to Fly.io with HTTPS enforced via built-in TLS termination. A `fly.toml` configuration file will define the deployment, health checks, and auto-start behavior.

**Kubernetes Orchestration (Option B):** We will use Kubernetes for orchestration — minikube locally and DigitalOcean Managed Kubernetes for production. The setup will include: Deployments with 3 replicas for the API (enabling load balancing and rolling updates), a StatefulSet for PostgreSQL with a PersistentVolumeClaim, LoadBalancer Services, Secrets for credentials, and liveness/readiness probes.

**Monitoring and Observability:** We will implement a three-layer monitoring approach. Fly.io's built-in metrics provide infrastructure-level visibility (CPU, memory, disk). Prometheus scrapes application-level metrics from a `/metrics` endpoint, including custom gauges for inventory levels, WebSocket connections, and HTTP latency. Grafana visualizes these through pre-configured dashboards. Alerting rules trigger on high error rates, elevated latency, and critical low-stock levels.

### Advanced Features (4 Planned)

As a four-member team, we plan to implement four advanced features, exceeding the minimum requirement of two:

**1. Real-Time Functionality (WebSockets):** When any user modifies inventory, the change is broadcast in real time to all connected clients via WebSockets. We will use FastAPI's native WebSocket support with Redis Pub/Sub as a message broker, enabling consistent event delivery across multiple Kubernetes replicas. Event types include `item_created`, `item_updated`, `item_deleted`, `stock_changed`, and `low_stock_alert`.

**2. Serverless Email Notifications:** A serverless function on DigitalOcean Functions handles low-stock alerts. When an item's quantity drops below its threshold, the API sends an HTTP POST to the function, which sends an email via SendGrid to Manager users. This decouples notification logic from the main API, demonstrating event-driven serverless architecture.

**3. Edge-Specific Optimizations:** The application will be deployed across multiple Fly.io regions (Toronto `yyz`, Virginia `iad`, London `lhr`) with automatic routing to the nearest healthy instance. Write operations at read-replica regions are forwarded to the primary via Fly.io's `fly-replay` header, maintaining consistency while optimizing global read performance.

**4. CI/CD Pipeline:** A GitHub Actions workflow will automate the build-test-deploy cycle. On every push to `main`, the pipeline runs pytest, builds Docker images, and deploys to Fly.io. Pull requests trigger the test suite automatically, preventing broken code from merging.

### Application Features

Beyond infrastructure, the application provides: JWT-based authentication with role-based access control (Manager and Staff roles), full CRUD for items/categories/locations, restock and withdrawal with quantity validation, search and filtering by name/SKU/category/location/quantity, an immutable audit trail, a summary dashboard, user management, and automated database backups via Kubernetes CronJob.

### Scope and Feasibility

As a four-member team, our target is 700+ meaningful lines of code per member (2,800+ total). Based on our estimation — approximately 1,800 lines for the backend, 400 for Kubernetes manifests, 200 for monitoring/CI/CD/serverless configs, and 1,500 for the frontend — we expect roughly 4,500+ total lines, comfortably exceeding the requirement. The scope is focused on a single, well-defined domain with clear CRUD semantics, making it achievable within the 5-week window.

---

## 3. Tentative Plan

### Responsibility Breakdown

**[Member 1] — Backend Core:** FastAPI application structure, authentication system (JWT + RBAC), all core CRUD endpoints (items, categories, locations, alerts, dashboard), and automated backend unit and integration tests.

**[Member 2] — Data & Real-Time Layer:** Database schema design, Alembic migrations, seed data scripts, WebSocket real-time update system with Redis Pub/Sub, search/filter/dashboard endpoints, and the audit log system.

**[Member 3] — Infrastructure & Deployment:** Docker multi-stage builds, Docker Compose configuration, all Kubernetes manifests (Deployments, StatefulSet, Services, PVCs, Secrets), Fly.io deployment, edge routing configuration, automated database backup CronJob, and CI/CD pipeline (GitHub Actions).

**[Member 4] — Frontend & Monitoring:** Next.js frontend (all pages, components, and WebSocket client hooks), serverless low-stock alert function (DO Functions + SendGrid), Prometheus metrics integration (custom gauges and `/metrics` endpoint), Grafana dashboard configuration, and alerting rules.

All four members will collaborate on architecture decisions, code reviews via GitHub pull requests, and integration testing.

### Week-by-Week Plan

**Week 1 (Feb 24 – Mar 2):** Finalize and submit proposal. Set up GitHub repository with branch protection and issue templates. [Member 1] initializes the FastAPI skeleton and project structure. [Member 2] designs and implements the database schema with Alembic migrations and writes seed data scripts. [Member 3] sets up Docker Compose with PostgreSQL and Redis. [Member 4] scaffolds the Next.js frontend project and login page.

**Week 2 (Mar 3 – Mar 9):** [Member 1] implements JWT authentication, RBAC middleware, and item CRUD endpoints with tests. [Member 2] implements category/location endpoints and begins the WebSocket connection manager with Redis Pub/Sub. [Member 3] writes multi-stage Dockerfiles and adds Prometheus/Grafana containers to Docker Compose. [Member 4] builds the dashboard layout and inventory list page, and begins integrating Prometheus metrics into the FastAPI `/metrics` endpoint.

**Week 3 (Mar 10 – Mar 16):** [Member 1] implements restock/withdraw endpoints, alert acknowledgment, and expands test coverage. [Member 2] completes WebSocket broadcasting across replicas, implements search/filter endpoints, and the audit log system. [Member 3] creates all Kubernetes manifests and validates them on minikube. [Member 4] builds item detail/create/edit pages, integrates WebSocket live updates in the frontend, and configures Grafana dashboards connected to Prometheus.

**Week 4 (Mar 17 – Mar 24):** [Member 1] finalizes remaining API endpoints (dashboard summary) and hardens auth edge cases. [Member 2] performs end-to-end testing of WebSocket events and search functionality under multi-replica conditions. [Member 3] deploys to Fly.io, configures edge routing across regions, sets up the backup CronJob, and configures the GitHub Actions CI/CD pipeline. [Member 4] builds and deploys the serverless low-stock alert function (DO Functions + SendGrid), finalizes alerting rules, and polishes the frontend. All members prepare the presentation. **Milestone: all core features working locally and/or deployed by Mar 24.**

**Week 5 (Mar 25 – Apr 4):** All members collaborate on final integration testing, bug fixes, deployment polish, video demo recording, final report (README.md), and AI interaction record (ai-session.md).

---

## 4. Initial Independent Reasoning (Before Using AI)

### Architecture Choices

We chose **Fly.io** because the course example for an Inventory Management System pairs it with Fly.io, and its edge routing capabilities support our planned low-latency global access feature. We selected **Kubernetes (Option B)** over Docker Swarm because Kubernetes is the industry standard, and practical experience with Deployments, StatefulSets, and PVCs aligns with our professional goals. For persistent storage, we chose Fly.io Volumes (cloud) and DigitalOcean Volumes via PVCs (Kubernetes), as recommended in the course guidelines.

We chose **Python with FastAPI** over Node.js because three of four team members have stronger Python experience, FastAPI provides native async support and built-in WebSocket handling, and its automatic OpenAPI documentation will simplify API testing during development.

### Anticipated Challenges

We expected **Kubernetes configuration** to be the most difficult aspect of the project. No team member has prior experience writing Kubernetes manifests from scratch, and the interplay between StatefulSets, PVCs, Secrets, and Services involves many configuration details where a single misconfigured field can cause cascading failures. We anticipated significant debugging time for pod crash loops and networking issues.

Our second concern was **WebSocket scaling across multiple replicas**. A WebSocket event published on one API replica would not automatically reach clients connected to other replicas. We identified early that some form of message broker (likely Redis) would be needed to bridge this gap, but we were uncertain about the implementation complexity.

A third concern specific to our team size was **coordination overhead**. With four members working in parallel on interconnected components (backend, frontend, infrastructure, advanced features), merge conflicts and integration issues were expected. We planned to mitigate this through clear module boundaries, feature branches, and pull request reviews.

### Early Development Approach

Our initial strategy was to build the application in layers: start with a working monolith (single FastAPI app with PostgreSQL in Docker Compose), validate all features locally, then progressively add orchestration (Kubernetes), monitoring (Prometheus/Grafana), and advanced features (WebSockets, serverless, edge routing, CI/CD). We divided responsibilities into four clear domains — backend API, real-time and advanced features, infrastructure/DevOps, and frontend/monitoring — to minimize blocking dependencies and allow maximum parallel progress across all four members.

---

## 5. AI Assistance Disclosure

### Parts Developed Without AI

The project idea selection, motivation framing, team responsibility division, and week-by-week timeline were developed entirely through team discussion without AI input. The choice of Fly.io, Kubernetes, and Python/FastAPI was based on our own reading of the course guidelines and our assessment of our team's collective skill set. The database schema was initially sketched on a whiteboard during our first team meeting before any AI consultation.

### How AI Was Used

We used AI (Claude) to help refine the technical details of our proposal, specifically: generating a comprehensive list of API endpoints to ensure we hadn't missed important CRUD operations, suggesting the specific Prometheus metric names and Grafana dashboard structure, and reviewing our Kubernetes manifest outline for completeness (confirming we needed StatefulSets for PostgreSQL rather than a plain Deployment).

### AI Suggestion and Team Discussion

AI suggested including **Redis Pub/Sub** as the message broker for distributing WebSocket events across multiple API replicas. Our team had originally considered implementing a simpler in-memory broadcast, which would work for a single replica but break under Kubernetes scaling. After reviewing the AI's suggestion, we discussed the tradeoff: Redis adds another service to our Docker Compose and Kubernetes setup (increasing infrastructure complexity and resource usage), but without it, our real-time feature would fundamentally fail in any multi-replica deployment — which is exactly the scenario Kubernetes orchestration creates. We concluded that the added complexity was justified because it directly addresses a real distributed systems problem, and Redis is lightweight enough (Alpine image, minimal memory) to not meaningfully impact our deployment cost or complexity budget. We adopted the suggestion.