#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# Inventory Management System — Environment Setup & Check Script
# Run: chmod +x setup-check.sh && ./setup-check.sh
# ═══════════════════════════════════════════════════════════════

# Do NOT use set -e — check commands return non-zero when tools are missing

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
FIXED=0
WARNINGS=0

# ───────────────────────────────────────────
# Helper functions
# ───────────────────────────────────────────
print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""
}

print_check() {
    echo -e "  ${CYAN}▶ Checking $1...${NC}"
}

print_pass() {
    echo -e "  ${GREEN}✅ $1${NC}"
    PASS=$((PASS+1))
}

print_fail() {
    echo -e "  ${RED}❌ $1${NC}"
    FAIL=$((FAIL+1))
}

print_warn() {
    echo -e "  ${YELLOW}⚠️  $1${NC}"
    WARNINGS=$((WARNINGS+1))
}

print_fix() {
    echo -e "  ${GREEN}🔧 $1${NC}"
    FIXED=$((FIXED+1))
}

print_info() {
    echo -e "  ${CYAN}ℹ️  $1${NC}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="mac"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
}

# Check if Homebrew is available (macOS)
has_brew() {
    command -v brew &> /dev/null
}

# Ask user yes/no
ask_install() {
    echo ""
    read -p "    Would you like to install $1? (y/n): " choice
    case "$choice" in
        y|Y ) return 0;;
        * ) return 1;;
    esac
}

# Compare version strings: returns 0 if $1 >= $2
version_gte() {
    [ "$(printf '%s\n' "$2" "$1" | sort -V | head -n1)" = "$2" ]
}

# Extract version number from string
extract_version() {
    echo "$1" | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1
}

# ═══════════════════════════════════════════════════════════════
# START
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${BOLD}${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║   Inventory Management System — Environment Setup Check  ║${NC}"
echo -e "${BOLD}${BLUE}║   ECE 1779 Course Project                                ║${NC}"
echo -e "${BOLD}${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

detect_os
echo -e "  Detected OS: ${BOLD}$OS${NC} ($OSTYPE)"

# ───────────────────────────────────────────
# macOS: Check Homebrew first
# ───────────────────────────────────────────
if [[ "$OS" == "mac" ]]; then
    print_header "PACKAGE MANAGER"
    print_check "Homebrew"
    if has_brew; then
        BREW_VER=$(brew --version | head -1)
        print_pass "Homebrew installed ($BREW_VER)"
    else
        print_fail "Homebrew not found"
        if ask_install "Homebrew"; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            print_fix "Homebrew installed"
        else
            print_warn "Some auto-installs will be skipped without Homebrew"
        fi
    fi
fi

# ═══════════════════════════════════════════
# 1. GIT
# ═══════════════════════════════════════════
print_header "1/6  GIT"
print_check "Git"

if command -v git &> /dev/null; then
    GIT_VER=$(extract_version "$(git --version)")
    if version_gte "$GIT_VER" "2.0.0"; then
        print_pass "Git $GIT_VER"
    else
        print_warn "Git $GIT_VER is old (recommend 2.30+)"
    fi
else
    print_fail "Git not found"
    if [[ "$OS" == "mac" ]] && has_brew; then
        if ask_install "Git via Homebrew"; then
            brew install git
            print_fix "Git installed via Homebrew"
        fi
    elif [[ "$OS" == "linux" ]]; then
        if ask_install "Git via apt"; then
            sudo apt update && sudo apt install -y git
            print_fix "Git installed via apt"
        fi
    else
        print_info "Install Git from https://git-scm.com/downloads"
    fi
fi

# Check git config
print_check "Git user config"
GIT_NAME=$(git config --global user.name 2>/dev/null || echo "")
GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")

if [[ -n "$GIT_NAME" && -n "$GIT_EMAIL" ]]; then
    print_pass "Git user: $GIT_NAME <$GIT_EMAIL>"
else
    print_warn "Git user name/email not configured"
    echo ""
    if [[ -z "$GIT_NAME" ]]; then
        read -p "    Enter your full name for Git: " input_name
        git config --global user.name "$input_name"
        print_fix "Git user.name set to '$input_name'"
    fi
    if [[ -z "$GIT_EMAIL" ]]; then
        read -p "    Enter your email for Git: " input_email
        git config --global user.email "$input_email"
        print_fix "Git user.email set to '$input_email'"
    fi
fi

# Set pull strategy
print_check "Git pull strategy"
GIT_PULL=$(git config --global pull.rebase 2>/dev/null || echo "")
if [[ "$GIT_PULL" == "true" ]]; then
    print_pass "pull.rebase = true"
else
    git config --global pull.rebase true
    print_fix "Set pull.rebase = true (prevents merge commits on pull)"
fi

# ═══════════════════════════════════════════
# 2. DOCKER
# ═══════════════════════════════════════════
print_header "2/6  DOCKER"
print_check "Docker"

if command -v docker &> /dev/null; then
    DOCKER_VER=$(extract_version "$(docker --version)")
    if version_gte "$DOCKER_VER" "24.0.0"; then
        print_pass "Docker $DOCKER_VER"
    else
        print_warn "Docker $DOCKER_VER — recommend 24.0+ (update Docker Desktop)"
    fi
else
    print_fail "Docker not found"
    print_info "Install Docker Desktop from https://docs.docker.com/get-docker/"
    print_info "After installing, make sure Docker Desktop is RUNNING"
fi

# Check Docker daemon is running
print_check "Docker daemon"
if docker info &> /dev/null; then
    print_pass "Docker daemon is running"
else
    print_fail "Docker daemon is not running"
    print_info "Start Docker Desktop and try again"
fi

# Check Docker Compose
print_check "Docker Compose"
if docker compose version &> /dev/null; then
    COMPOSE_VER=$(extract_version "$(docker compose version)")
    if version_gte "$COMPOSE_VER" "2.20.0"; then
        print_pass "Docker Compose $COMPOSE_VER"
    else
        print_warn "Docker Compose $COMPOSE_VER — recommend 2.20+ (update Docker Desktop)"
    fi
else
    print_fail "Docker Compose not found"
    print_info "Docker Compose v2 comes with Docker Desktop — make sure it's installed and updated"
fi

# ═══════════════════════════════════════════
# 3. PYTHON
# ═══════════════════════════════════════════
print_header "3/6  PYTHON"
print_check "Python"

# Try python3 first, then python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if [[ -n "$PYTHON_CMD" ]]; then
    PYTHON_VER=$(extract_version "$($PYTHON_CMD --version 2>&1)")
    if version_gte "$PYTHON_VER" "3.12.0"; then
        print_pass "Python $PYTHON_VER ($PYTHON_CMD)"
    elif version_gte "$PYTHON_VER" "3.10.0"; then
        print_warn "Python $PYTHON_VER — works but 3.12+ recommended"
    else
        print_fail "Python $PYTHON_VER — need 3.12+"
        if [[ "$OS" == "mac" ]] && has_brew; then
            if ask_install "Python 3.12 via Homebrew"; then
                brew install python@3.12
                print_fix "Python 3.12 installed via Homebrew"
            fi
        elif [[ "$OS" == "linux" ]]; then
            print_info "Install: sudo apt install python3.12 python3.12-venv"
        fi
    fi
else
    print_fail "Python not found"
    if [[ "$OS" == "mac" ]] && has_brew; then
        if ask_install "Python 3.12 via Homebrew"; then
            brew install python@3.12
            print_fix "Python 3.12 installed"
        fi
    elif [[ "$OS" == "linux" ]]; then
        if ask_install "Python 3.12 via apt"; then
            sudo apt update && sudo apt install -y python3.12 python3.12-venv python3-pip
            print_fix "Python 3.12 installed"
        fi
    else
        print_info "Install from https://www.python.org/downloads/"
    fi
fi

# Check pip
print_check "pip"
if command -v pip3 &> /dev/null; then
    PIP_VER=$(extract_version "$(pip3 --version)")
    print_pass "pip $PIP_VER"
elif command -v pip &> /dev/null; then
    PIP_VER=$(extract_version "$(pip --version)")
    print_pass "pip $PIP_VER"
else
    print_warn "pip not found — install with: python3 -m ensurepip"
fi

# ═══════════════════════════════════════════
# 4. NODE.JS
# ═══════════════════════════════════════════
print_header "4/6  NODE.JS"
print_check "Node.js"

if command -v node &> /dev/null; then
    NODE_VER=$(extract_version "$(node --version)")
    if version_gte "$NODE_VER" "20.0.0"; then
        print_pass "Node.js $NODE_VER"
    elif version_gte "$NODE_VER" "18.0.0"; then
        print_warn "Node.js $NODE_VER — works but 20+ recommended"
    else
        print_fail "Node.js $NODE_VER — need 20+"
    fi
else
    print_fail "Node.js not found"
    if [[ "$OS" == "mac" ]] && has_brew; then
        if ask_install "Node.js 20 via Homebrew"; then
            brew install node@20
            print_fix "Node.js installed via Homebrew"
        fi
    elif [[ "$OS" == "linux" ]]; then
        if ask_install "Node.js 20 via NodeSource"; then
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt install -y nodejs
            print_fix "Node.js 20 installed"
        fi
    else
        print_info "Install from https://nodejs.org/"
    fi
fi

# Check npm
print_check "npm"
if command -v npm &> /dev/null; then
    NPM_VER=$(extract_version "$(npm --version)")
    print_pass "npm $NPM_VER"
else
    print_warn "npm not found — comes with Node.js"
fi

# ═══════════════════════════════════════════
# 5. MINIKUBE
# ═══════════════════════════════════════════
print_header "5/6  MINIKUBE & KUBECTL"
print_check "minikube"

if command -v minikube &> /dev/null; then
    MINI_VER=$(extract_version "$(minikube version --short 2>/dev/null || minikube version)")
    print_pass "minikube $MINI_VER"
else
    print_fail "minikube not found"
    if [[ "$OS" == "mac" ]] && has_brew; then
        if ask_install "minikube via Homebrew"; then
            brew install minikube
            print_fix "minikube installed via Homebrew"
        fi
    elif [[ "$OS" == "linux" ]]; then
        if ask_install "minikube"; then
            curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
            sudo install minikube-linux-amd64 /usr/local/bin/minikube
            rm minikube-linux-amd64
            print_fix "minikube installed"
        fi
    else
        print_info "Install from https://minikube.sigs.k8s.io/docs/start/"
    fi
fi

print_check "kubectl"
if command -v kubectl &> /dev/null; then
    KUBE_VER=$(extract_version "$(kubectl version --client --short 2>/dev/null || kubectl version --client)")
    print_pass "kubectl $KUBE_VER"
else
    print_fail "kubectl not found"
    if [[ "$OS" == "mac" ]] && has_brew; then
        if ask_install "kubectl via Homebrew"; then
            brew install kubectl
            print_fix "kubectl installed via Homebrew"
        fi
    elif [[ "$OS" == "linux" ]]; then
        if ask_install "kubectl via snap"; then
            sudo snap install kubectl --classic
            print_fix "kubectl installed via snap"
        fi
    else
        print_info "Install from https://kubernetes.io/docs/tasks/tools/"
    fi
fi

# ═══════════════════════════════════════════
# 6. FLY CLI
# ═══════════════════════════════════════════
print_header "6/6  FLY CLI"
print_check "flyctl"

if command -v fly &> /dev/null || command -v flyctl &> /dev/null; then
    FLY_CMD=$(command -v fly || command -v flyctl)
    FLY_VER=$($FLY_CMD version 2>/dev/null | head -1)
    print_pass "Fly CLI ($FLY_VER)"
else
    print_warn "Fly CLI not found (only Member 3 needs this now)"
    if ask_install "Fly CLI"; then
        curl -L https://fly.io/install.sh | sh
        print_fix "Fly CLI installed"
        print_info "Add to PATH: export FLYCTL_INSTALL=\"\$HOME/.fly\" && export PATH=\"\$FLYCTL_INSTALL/bin:\$PATH\""
    fi
fi

# ═══════════════════════════════════════════
# BONUS CHECKS
# ═══════════════════════════════════════════
print_header "BONUS CHECKS"

# Check available disk space
print_check "Disk space"
if [[ "$OS" == "mac" ]]; then
    FREE_GB=$(df -g / | tail -1 | awk '{print $4}')
else
    FREE_GB=$(df -BG / | tail -1 | awk '{print $4}' | sed 's/G//')
fi
if [[ "$FREE_GB" -ge 20 ]]; then
    print_pass "${FREE_GB}GB free (Docker images need ~5-10GB)"
elif [[ "$FREE_GB" -ge 10 ]]; then
    print_warn "${FREE_GB}GB free — might get tight with Docker images"
else
    print_fail "${FREE_GB}GB free — Docker needs at least 10GB free"
fi

# Check available memory
print_check "Available RAM"
if [[ "$OS" == "mac" ]]; then
    TOTAL_RAM=$(($(sysctl -n hw.memsize) / 1073741824))
else
    TOTAL_RAM=$(($(grep MemTotal /proc/meminfo | awk '{print $2}') / 1048576))
fi
if [[ "$TOTAL_RAM" -ge 8 ]]; then
    print_pass "${TOTAL_RAM}GB RAM (good for Docker + minikube)"
elif [[ "$TOTAL_RAM" -ge 4 ]]; then
    print_warn "${TOTAL_RAM}GB RAM — might be slow running all containers"
else
    print_fail "${TOTAL_RAM}GB RAM — may struggle with Docker + minikube"
fi

# Check if common ports are free
print_check "Port availability"
PORTS_BUSY=0
for PORT in 3000 3001 5432 6379 8000 9090; do
    if lsof -i :$PORT &> /dev/null 2>&1; then
        print_warn "Port $PORT is in use (needed by our stack)"
        PORTS_BUSY=$((PORTS_BUSY+1))
    fi
done
if [[ "$PORTS_BUSY" -eq 0 ]]; then
    print_pass "All required ports are free (3000, 3001, 5432, 6379, 8000, 9090)"
fi

# ═══════════════════════════════════════════
# REPO CHECK
# ═══════════════════════════════════════════
print_header "REPO CHECK"
print_check "Project repository"

if [[ -f "docker-compose.yml" ]]; then
    print_pass "docker-compose.yml found"
elif [[ -f "../docker-compose.yml" ]]; then
    print_warn "Run this script from the project root directory"
else
    print_info "docker-compose.yml not found — clone the repo first:"
    print_info "git clone https://github.com/johnchen77w/Inventory-Management-System.git"
fi

print_check ".env file"
if [[ -f ".env" ]]; then
    print_pass ".env file exists"
elif [[ -f ".env.example" ]]; then
    cp .env.example .env
    print_fix "Created .env from .env.example"
else
    print_warn ".env and .env.example not found — clone the repo first"
fi

# ═══════════════════════════════════════════
# DOCKER COMPOSE TEST
# ═══════════════════════════════════════════
if [[ -f "docker-compose.yml" ]] && docker info &> /dev/null 2>&1; then
    print_header "DOCKER COMPOSE SMOKE TEST"
    echo ""
    read -p "  Run docker compose up to test the full stack? (y/n): " run_test
    if [[ "$run_test" == "y" || "$run_test" == "Y" ]]; then
        echo ""
        print_info "Starting services (this may take a few minutes on first run)..."
        echo ""

        docker compose up --build -d

        echo ""
        print_info "Waiting 15 seconds for services to initialize..."
        sleep 15

        # Test API
        print_check "API health endpoint"
        if curl -s http://localhost:8000/health | grep -q "healthy"; then
            print_pass "API is healthy at http://localhost:8000/health"
        else
            print_fail "API not responding — check: docker compose logs api"
        fi

        # Test PostgreSQL
        print_check "PostgreSQL"
        if docker compose exec -T postgres pg_isready -U inventory &> /dev/null; then
            print_pass "PostgreSQL is ready"
        else
            print_fail "PostgreSQL not ready — check: docker compose logs postgres"
        fi

        # Test Redis
        print_check "Redis"
        if docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
            print_pass "Redis is responding"
        else
            print_fail "Redis not responding — check: docker compose logs redis"
        fi

        # Test Prometheus
        print_check "Prometheus"
        if curl -s http://localhost:9090/-/ready | grep -q "ready" 2>/dev/null; then
            print_pass "Prometheus is ready at http://localhost:9090"
        else
            print_warn "Prometheus may still be starting — check http://localhost:9090"
        fi

        # Test Grafana
        print_check "Grafana"
        if curl -s http://localhost:3001/api/health | grep -q "ok" 2>/dev/null; then
            print_pass "Grafana is ready at http://localhost:3001 (admin/admin)"
        else
            print_warn "Grafana may still be starting — check http://localhost:3001"
        fi

        echo ""
        read -p "  Stop the containers? (y/n): " stop_choice
        if [[ "$stop_choice" == "y" || "$stop_choice" == "Y" ]]; then
            docker compose down
            print_info "Containers stopped"
        else
            print_info "Containers still running — stop later with: docker compose down"
        fi
    fi
fi

# ═══════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════
print_header "SUMMARY"

echo -e "  ${GREEN}✅ Passed:  $PASS${NC}"
echo -e "  ${GREEN}🔧 Fixed:   $FIXED${NC}"
echo -e "  ${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo -e "  ${RED}❌ Failed:  $FAIL${NC}"
echo ""

if [[ "$FAIL" -eq 0 ]]; then
    echo -e "  ${GREEN}${BOLD}🎉 All good! Your environment is ready.${NC}"
    echo -e "  ${GREEN}   Run 'docker compose up --build' to start developing!${NC}"
elif [[ "$FAIL" -le 2 ]]; then
    echo -e "  ${YELLOW}${BOLD}⚠️  Almost there! Fix the failed items above and re-run this script.${NC}"
else
    echo -e "  ${RED}${BOLD}🚨 Several tools are missing. Install them and re-run this script.${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
