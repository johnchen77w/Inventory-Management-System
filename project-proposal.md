# ECE 1779 Course Project Proposal: Cloud-Native Inventory Management System

**Team Members:** [Wenxi Chen] (1003795761), [Huiying Yu] (1012487667), [Jinghan Song] (1005992204), [Xuhui Zhang] (1007287482)

---

## 1. Motivation

Inventory management is a fundamental operational challenge for businesses ranging from small retail shops to mid-sized warehouses. Inaccurate stock tracking leads to costly problems: stockouts cause lost sales and customer dissatisfaction, overstocking ties up capital unnecessarily, and manual counting processes waste staff time. According to industry research, inventory distortion (shrinkage, stockouts, and overstock) costs retailers nearly $1.8 trillion globally each year.

While enterprise solutions like SAP and Oracle NetSuite exist, they are prohibitively expensive, complex to deploy, and impractical for small-to-medium businesses (SMBs) that lack dedicated IT infrastructure. Many SMBs still rely on spreadsheets or paper-based tracking, which are error-prone and offer no real-time visibility. Open-source alternatives like InvenTree exist but require self-hosted servers and lack cloud-native features such as auto-scaling, edge-optimized access, and automated alerting.

Our project addresses this gap by building a **lightweight, cloud-native inventory management system** that provides real-time stock visibility, automated low-stock email alerts, and multi-location support — all deployed on modern edge infrastructure for low-latency global access.

**Target users** include:

- **Warehouse managers** who need centralized stock visibility across multiple storage locations and want automated alerts when items run low.
- **Retail and warehouse staff** who perform daily stock-in and stock-out operations and need a fast, intuitive interface that updates in real time.
- **Operations teams** in SMBs who require dashboards to monitor inventory health without investing in enterprise-grade ERP software.

This project is worth pursuing because it directly applies core ECE 1779 concepts — containerization, orchestration, persistent storage, monitoring, and edge deployment — to a practical, real-world problem that benefits clearly defined users.

---

## 2. Objective and Key Features

### Objective

Design, implement, and deploy a stateful, cloud-native inventory management system that demonstrates mastery of cloud computing principles covered in ECE 1779. The system will support full inventory lifecycle management with role-based access, real-time updates, automated alerting, and comprehensive monitoring — all running on containerized, orchestrated infrastructure deployed to an edge cloud provider.

### Core Technical Requirements

**Containerization and Local Development:** Every service will be containerized with Docker using multi-stage builds to minimize image size. A `docker-compose.yml` file will orchestrate the full local stack: Python/FastAPI API server, PostgreSQL database, Redis message broker, and Prometheus/Grafana monitoring. A single `docker compose up` command will bring the entire application online for development and testing.

**State Management with PostgreSQL:** PostgreSQL 16 will serve as the primary relational database, storing users, inventory items, categories, locations, inventory change logs, and alert records. We will use SQLAlchemy 2.0 as the ORM and Alembic for schema migrations, ensuring the database schema is version-controlled and reproducible. The database schema includes six tables: `users` (authentication and roles), `items` (core inventory with SKU, quantity, category, location, and low-stock threshold), `categories`, `locations`, `inventory_logs` (immutable audit trail), and `alerts` (notification records).

**Persistent Storage:** PostgreSQL data will be stored on Fly.io Volumes in the cloud deployment and on Kubernetes PersistentVolumeClaims in the orchestrated environment, ensuring state survives container restarts and redeployments.

**Deployment on Fly.io:** The application will be deployed to Fly.io as the primary cloud provider. The API service will run as a Fly Machine with HTTPS enforced via Fly.io's built-in TLS termination. A `fly.toml` configuration file will define the deployment, health checks, and auto-start behavior.

**Kubernetes Orchestration (Option B):** We will use Kubernetes for orchestration. Locally, minikube will host the cluster for development and testing. For production, we will use DigitalOcean Managed Kubernetes. The Kubernetes setup will include: Deployments with 3 replicas for the API service (enabling load balancing and rolling updates), a StatefulSet for PostgreSQL with a PersistentVolumeClaim, Services (LoadBalancer type) for external access, Secrets for credential management, and liveness/readiness probes for automated health monitoring.

**Monitoring and Observability:** We will implement a three-layer monitoring approach. First, Fly.io's built-in metrics will provide infrastructure-level visibility (CPU, memory, disk). Second, Prometheus will scrape application-level metrics from a `/metrics` endpoint exposed by the FastAPI backend, including custom gauges for total inventory items, low-stock item count, active WebSocket connections, and HTTP request latency histograms. Third, Grafana will visualize these metrics through pre-configured dashboards for system health, inventory overview, and API performance. Alerting rules will trigger on high error rates (>10%), elevated p95 latency (>2s), and critical low-stock levels.

### Advanced Features (3 Planned)

We plan to implement three advanced features, exceeding the minimum requirement of two:

**1. Real-Time Functionality (WebSockets):** When any user creates, updates, or deletes an inventory item, the change will be broadcast in real time to all connected clients via WebSockets. We will use FastAPI's native WebSocket support combined with Redis Pub/Sub as a message broker, enabling consistent event delivery even when the API runs across multiple Kubernetes replicas. Event types include `item_created`, `item_updated`, `item_deleted`, `stock_changed`, and `low_stock_alert`.

**2. Serverless Email Notifications:** A serverless function deployed on DigitalOcean Functions will handle low-stock alerts. When an item's quantity drops below its configured threshold, the API sends an HTTP POST to the function, which formats and sends an email via the SendGrid API to all Manager users. This decouples the notification logic from the main API, demonstrating event-driven serverless architecture.

**3. Edge-Specific Optimizations:** The application will be deployed across multiple Fly.io regions (Toronto `yyz`, Virginia `iad`, London `lhr`). Fly.io's edge network will automatically route each request to the nearest healthy instance for minimal latency. Write operations arriving at read-replica regions will be forwarded to the primary region using Fly.io's `fly-replay` header mechanism, maintaining data consistency while optimizing read performance globally.

### Application Features

Beyond infrastructure, the application provides: JWT-based authentication with role-based access control (Manager and Staff roles), full CRUD operations for items/categories/locations, restock and withdrawal operations with quantity validation, search and filtering by name/SKU/category/location/quantity range, an immutable audit trail of all inventory changes, a dashboard with summary statistics, and user management for Managers.

### Scope and Feasibility

As a two-member team, our target is 1,000+ meaningful lines of code per member (2,000+ total). Based on our estimation — approximately 1,800 lines for the Python backend, 400 lines for Kubernetes manifests, 150 lines for monitoring configuration, and 1,200 lines for the optional Next.js frontend — we expect to produce roughly 4,000+ total lines, comfortably exceeding the requirement. The scope is focused on a single, well-defined domain (inventory management) with clear CRUD semantics, making it achievable within the 5-week development window while still demonstrating all required cloud technologies.

---

## 3. Tentative Plan

### Responsibility Breakdown

**[Member 1]** will focus on the **backend and data layer**: FastAPI application, database schema, authentication, WebSocket implementation, Prometheus metrics, and automated tests.

**[Member 2]** will focus on **infrastructure and frontend**: Docker/Docker Compose configuration, Kubernetes manifests, Fly.io deployment, Grafana dashboards, serverless function, CI/CD pipeline, and the Next.js frontend.

Both members will collaborate on architecture decisions, code reviews (via GitHub pull requests), and integration testing.

### Week-by-Week Plan

**Week 1 (Feb 24 – Mar 2):** Finalize and submit proposal. Set up GitHub repository with branch protection and issue templates. Initialize Docker Compose with PostgreSQL and a skeleton FastAPI app. Design and implement the database schema with Alembic migrations. Seed sample data.

**Week 2 (Mar 3 – Mar 9):** [Member 1] implements JWT authentication, role-based access control, and item CRUD endpoints with full test coverage. [Member 2] writes multi-stage Dockerfiles, refines Docker Compose for all services (API, Redis, Prometheus, Grafana), and begins the Next.js frontend skeleton.

**Week 3 (Mar 10 – Mar 16):** [Member 1] implements WebSocket real-time updates with Redis Pub/Sub, search/filter endpoints, and the audit log system. [Member 2] creates all Kubernetes manifests (minikube), configures Grafana dashboards, and builds the inventory UI pages.

**Week 4 (Mar 17 – Mar 24):** [Member 1] implements the serverless low-stock alert function (DO Functions + SendGrid) and remaining API endpoints (alerts, dashboard). [Member 2] deploys to Fly.io, configures edge routing across regions, and sets up the GitHub Actions CI/CD pipeline. Both members prepare the presentation. **Milestone: all core features working locally and/or deployed by Mar 24.**

**Week 5 (Mar 25 – Apr 4):** Polish deployment, fix bugs, configure automated backups, record the video demo, and write the final report (README.md) and AI interaction record (ai-session.md).

---

## 4. Initial Independent Reasoning (Before Using AI)

### Architecture Choices

We chose **Fly.io** as the deployment provider because the project's example idea for an Inventory Management System specifically pairs it with Fly.io, and because Fly.io's edge routing capabilities directly support our planned advanced feature of low-latency global access. We selected **Kubernetes (Option B)** over Docker Swarm because Kubernetes is the industry-dominant orchestration platform, and gaining practical experience with Deployments, StatefulSets, and PVCs aligns with our professional development goals. For persistent storage, we chose Fly.io Volumes for the cloud deployment and DigitalOcean Volumes (via PVCs) for the Kubernetes cluster, as both are explicitly recommended in the course guidelines.

We chose **Python with FastAPI** over Node.js because both team members have stronger Python experience, FastAPI provides native async support and built-in WebSocket handling, and its automatic OpenAPI documentation will simplify API testing during development.

### Anticipated Challenges

We expected **Kubernetes configuration** to be the most difficult aspect of the project. Neither team member has prior experience writing Kubernetes manifests from scratch, and the interplay between StatefulSets, PVCs, Secrets, and Services involves many configuration details where a single misconfigured field can cause cascading failures. We anticipated significant debugging time for pod crash loops and networking issues.

Our second concern was **WebSocket scaling across multiple replicas**. A WebSocket event published on one API replica would not automatically reach clients connected to other replicas. We identified early that some form of message broker (likely Redis) would be needed to bridge this gap, but we were uncertain about the implementation complexity.

### Early Development Approach

Our initial strategy was to build the application in layers: start with a working monolith (single FastAPI app with PostgreSQL in Docker Compose), validate all features locally, then progressively add orchestration (Kubernetes), monitoring (Prometheus/Grafana), and advanced features (WebSockets, serverless, edge routing). We divided responsibilities by skill set — one member stronger in backend/API development, the other in infrastructure/DevOps — to minimize blocking dependencies and allow parallel progress.

---

## 5. AI Assistance Disclosure

### Parts Developed Without AI

The project idea selection, motivation framing, team responsibility division, and week-by-week timeline were developed entirely through team discussion without AI input. The choice of Fly.io, Kubernetes, and Python/FastAPI was based on our own reading of the course guidelines and our assessment of our team's skill set. The database schema was initially sketched on a whiteboard before any AI consultation.

### How AI Was Used

We used AI (Claude) to help refine the technical details of our proposal, specifically: generating a comprehensive list of API endpoints to ensure we hadn't missed important CRUD operations, suggesting the specific Prometheus metric names and Grafana dashboard structure, and reviewing our Kubernetes manifest outline for completeness (confirming we needed StatefulSets for PostgreSQL rather than a plain Deployment).

### AI Suggestion and Team Discussion

AI suggested including **Redis Pub/Sub** as the message broker for distributing WebSocket events across multiple API replicas. Our team had originally considered implementing a simpler in-memory broadcast, which would work for a single replica but break under Kubernetes scaling. After reviewing the AI's suggestion, we discussed the tradeoff: Redis adds another service to our Docker Compose and Kubernetes setup (increasing infrastructure complexity and resource usage), but without it, our real-time feature would fundamentally fail in any multi-replica deployment — which is exactly the scenario Kubernetes orchestration creates. We concluded that the added complexity was justified because it directly addresses a real distributed systems problem, and Redis is lightweight enough (Alpine image, minimal memory) to not meaningfully impact our deployment cost or complexity budget. We adopted the suggestion.
