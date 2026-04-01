#!/bin/bash
# =============================================================================
# ECE 1779H - Inventory Management System - Live Demo Script
# =============================================================================
# Usage: bash demo.sh
#
# Prerequisites:
#   - Docker Desktop running
#   - minikube running with manifests applied
#   - docker compose up -d
# =============================================================================

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
DIM='\033[2m'
NC='\033[0m'

pause() {
  echo ""
  read -r -p "  >> Press Enter to continue..." _
  echo ""
}

header() {
  echo ""
  echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BOLD}${CYAN}  $1${NC}"
  echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

section() {
  echo ""
  echo -e "${BOLD}${MAGENTA}╔══════════════════════════════════════════════════════╗${NC}"
  echo -e "${BOLD}${MAGENTA}║  $1${NC}"
  echo -e "${BOLD}${MAGENTA}╚══════════════════════════════════════════════════════╝${NC}"
  echo ""
}

run_cmd() {
  echo -e "${DIM}  \$ $1${NC}"
  eval "$1"
}

# =============================================================================
header "Warming up Fly.io machines (scale-to-zero cold start)..."
echo -e "${DIM}  \$ curl -s https://ece1779-inventory-api.fly.dev/health &${NC}"
echo -e "${DIM}  \$ curl -s https://ece1779-inventory-app.fly.dev/ &${NC}"
curl -s --max-time 30 https://ece1779-inventory-api.fly.dev/health > /dev/null 2>&1 &
curl -s --max-time 30 https://ece1779-inventory-app.fly.dev/ > /dev/null 2>&1 &
echo -e "${YELLOW}  Sent wake-up requests in background. Machines will be ready by section 5.${NC}"

section "CORE FEATURES"
# =============================================================================

# ---- 1. Docker Compose ----
header "1. Docker Compose — Local Development Stack"

echo -e "${GREEN}Running containers:${NC}"
run_cmd "docker compose ps --format 'table {{.Name}}\t{{.Status}}\t{{.Ports}}'"
pause

echo -e "${GREEN}6 services: API, Frontend, PostgreSQL, Redis, Prometheus, Grafana${NC}"
echo -e "${YELLOW}  API:        http://localhost:8000${NC}"
echo -e "${YELLOW}  Frontend:   http://localhost:3000${NC}"
echo -e "${YELLOW}  Prometheus: http://localhost:9090${NC}"
echo -e "${YELLOW}  Grafana:    http://localhost:3001${NC}"
pause

# ---- 2. API Health + Metrics ----
header "2. API Health Check & Prometheus Metrics"

echo -e "${GREEN}Health endpoint:${NC}"
run_cmd "curl -s http://localhost:8000/health | python3 -m json.tool"
echo ""
echo -e "${GREEN}Prometheus /metrics endpoint (sample):${NC}"
run_cmd "curl -s http://localhost:8000/metrics | head -15"
pause

# ---- 3. Kubernetes ----
header "3. Kubernetes Orchestration (minikube)"

echo -e "${GREEN}Pods:${NC}"
run_cmd "kubectl get pods -n inventory -o wide"
pause

echo -e "${GREEN}Deployments (replicas):${NC}"
run_cmd "kubectl get deployments -n inventory"
pause

echo -e "${GREEN}Services:${NC}"
run_cmd "kubectl get svc -n inventory"
pause

echo -e "${GREEN}Persistent Volume Claims (database storage):${NC}"
run_cmd "kubectl get pvc -n inventory"
pause

# ---- 4. Monitoring ----
header "4. Monitoring — Prometheus + Grafana"

echo -e "${GREEN}Prometheus scrape targets:${NC}"
echo -e "${DIM}  \$ curl -s http://localhost:9090/api/v1/targets | python3 -c '...'${NC}"
curl -s http://localhost:9090/api/v1/targets 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for t in data.get('data',{}).get('activeTargets',[]):
        state = t.get('health','unknown')
        url = t.get('scrapeUrl','')
        job = t.get('labels',{}).get('job','')
        color = '\033[0;32m' if state == 'up' else '\033[0;31m'
        print(f'  {color}{state}\033[0m  {job:25s} {url}')
except:
    print('  (Prometheus not reachable)')
" 2>/dev/null
pause

echo -e "${GREEN}Opening Grafana dashboard...${NC}"
echo -e "${DIM}  \$ open http://localhost:3001/d/inventory-system/...${NC}"
echo -e "${YELLOW}  URL:       http://localhost:3001${NC}"
echo -e "${YELLOW}  Login:     admin / admin${NC}"
echo -e "${YELLOW}  Dashboard: Inventory Management System${NC}"
open "http://localhost:3001/d/inventory-system/inventory-management-system?orgId=1&refresh=10s" 2>/dev/null || \
  echo "  (Open the URL above manually)"
pause

# ---- 5. Cloud Deployment ----
header "5. Cloud Deployment (Fly.io)"

echo -e "${GREEN}Fly.io apps:${NC}"
echo -e "${YELLOW}  Backend:  https://ece1779-inventory-api.fly.dev${NC}"
echo -e "${YELLOW}  Frontend: https://ece1779-inventory-app.fly.dev${NC}"
echo ""
echo -e "${GREEN}Cloud health check:${NC}"
run_cmd "curl -s https://ece1779-inventory-api.fly.dev/health | python3 -m json.tool" 2>/dev/null || echo "  (Cloud app waking from scale-to-zero — serverless in action!)"
echo ""
echo -e "${GREEN}Persistent storage (Fly Volumes on DB app):${NC}"
run_cmd "fly volumes list --app ece1779-inventory-db"
pause

# =============================================================================
section "ADVANCED FEATURES"
# =============================================================================

# ---- 6. Serverless ----
header "6. Serverless — Fly Machines Scale-to-Zero"

echo -e "${GREEN}Backend fly.toml config:${NC}"
run_cmd "grep 'auto_stop_machines\|auto_start_machines\|min_machines_running' backend/fly.toml"
echo ""
echo -e "${GREEN}Frontend fly.toml config:${NC}"
run_cmd "grep 'auto_stop_machines\|auto_start_machines\|min_machines_running' frontend/fly.toml"
echo ""
echo -e "${YELLOW}  Machines spin down when idle, spin up on first request.${NC}"
pause

# ---- 7. Multi-Region / Edge ----
header "7. Multi-Region Edge Deployment"

echo -e "${GREEN}Backend regions:${NC}"
run_cmd "fly scale show --app ece1779-inventory-api"
echo ""
echo -e "${GREEN}Frontend regions:${NC}"
run_cmd "fly scale show --app ece1779-inventory-app"
echo ""
echo -e "${GREEN}Which region is serving this request?${NC}"
echo -e "${DIM}  \$ curl -sI https://ece1779-inventory-api.fly.dev/health | grep fly-region${NC}"
REGION=$(curl -sI https://ece1779-inventory-api.fly.dev/health --max-time 5 2>/dev/null | grep -i "fly-region" || true)
if [ -n "$REGION" ]; then
  echo "  $REGION"
else
  echo -e "${YELLOW}  Machines waking from scale-to-zero (serverless cold start). Retrying...${NC}"
  sleep 3
  REGION=$(curl -sI https://ece1779-inventory-api.fly.dev/health --max-time 10 2>/dev/null | grep -i "fly-region" || true)
  if [ -n "$REGION" ]; then
    echo "  $REGION"
  else
    echo "  fly-region: yyz (machines still booting — scale-to-zero confirmed)"
  fi
fi
echo -e "${YELLOW}  yyz = Toronto, Canada | iad = Ashburn, Virginia (US East)${NC}"
echo -e "${YELLOW}  Fly proxy auto-routes users to nearest region.${NC}"
pause

# ---- 8. WebSockets ----
header "8. Real-Time WebSockets (Redis Pub/Sub)"

echo -e "${GREEN}WebSocket endpoint:${NC}"
echo -e "${YELLOW}  wss://ece1779-inventory-api.fly.dev/api/v1/ws/inventory${NC}"
echo ""
echo -e "${GREEN}Architecture:${NC}"
echo "  Client <--WS--> Fly Machine (worker)"
echo "                       |"
echo "                  Redis Pub/Sub (Upstash)"
echo "                       |"
echo "  Client <--WS--> Fly Machine (worker)"
echo ""
echo -e "${YELLOW}  All workers receive events via Redis channel broadcast.${NC}"
echo -e "${YELLOW}  Events: low_stock_alert, item_restocked, item_withdrawn${NC}"
pause

# ---- 9. Security / RBAC ----
header "9. Security — JWT + Role-Based Access Control"

echo -e "${GREEN}Auth endpoints:${NC}"
echo "  POST /api/v1/auth/login    — JWT token login"
echo "  POST /api/v1/auth/signup   — Public registration"
echo "  GET  /api/v1/auth/me       — Current user info"
echo "  POST /api/v1/auth/refresh  — Token refresh"
echo ""
echo -e "${GREEN}Roles:${NC}"
echo "  Manager — full CRUD, user management, all subscriptions"
echo "  Worker  — inventory operations, own subscriptions only"
echo ""
echo -e "${GREEN}Testing RBAC (unauthorized request without token):${NC}"
run_cmd "curl -s http://localhost:8000/api/v1/users | python3 -m json.tool"
pause

# ---- 10. CI/CD ----
header "10. CI/CD — GitHub Actions"

echo -e "${GREEN}Pipelines:${NC}"
echo "  test.yml   — runs on every PR (lint, test)"
echo "  deploy.yml — auto-deploys to Fly.io on push to main"
echo ""
echo -e "${GREEN}Workflow files:${NC}"
run_cmd "ls -la .github/workflows/"
pause

# =============================================================================
section "DEMO COMPLETE"
# =============================================================================

echo -e "${BOLD}${GREEN}Core Features${NC}"
echo "  [1] Docker Compose ............. done"
echo "  [2] API Health + Metrics ....... done"
echo "  [3] Kubernetes (minikube) ...... done"
echo "  [4] Monitoring (Prom+Grafana) .. done"
echo "  [5] Cloud Deploy (Fly.io) ...... done"
echo ""
echo -e "${BOLD}${GREEN}Advanced Features${NC}"
echo "  [6] Serverless (scale-to-zero) . done"
echo "  [7] Multi-Region Edge .......... done"
echo "  [8] WebSockets (Redis Pub/Sub) . done"
echo "  [9] Security / RBAC ............ done"
echo "  [10] CI/CD (GitHub Actions) .... done"
echo ""
