# Deployment Runbook — Step-by-Step

## Prerequisites Checklist

| Tool       | Status | Install if missing |
|------------|--------|--------------------|
| flyctl     | ✅ Installed | `curl -L https://fly.io/install.sh \| sh` |
| minikube   | ✅ Installed | `brew install minikube` |
| kubectl    | ✅ Installed | `brew install kubectl` |
| doctl      | ❌ Not installed | `brew install doctl` |
| gh (GitHub CLI) | ❌ Not installed | `brew install gh` |

---

## Part 1: Install Missing Tools

```bash
# Step 1.1: Install DigitalOcean CLI
brew install doctl

# Step 1.2: Install GitHub CLI
brew install gh

# Step 1.3: Authenticate DigitalOcean
doctl auth init
# → Paste your DigitalOcean API token (from https://cloud.digitalocean.com/account/api/tokens)

# Step 1.4: Authenticate GitHub CLI
gh auth login
# → Choose: GitHub.com → HTTPS → Login with browser
```

---

## Part 2: Deploy Backend API to Fly.io

All commands run from the project root:
```bash
cd ~/Desktop/M.Eng/ECE\ 1779H\ Intro\ to\ Cloud/Inventory-Management-System
```

### Step 2.1: Create the API app on Fly.io

```bash
fly apps create inventory-api --org personal
```

> If `inventory-api` is taken, pick a unique name like `ims-api-wenxi` and update `fly.toml`:
> ```
> app = "ims-api-wenxi"
> ```

### Step 2.2: Create Fly Managed Postgres

```bash
fly postgres create \
  --name inventory-db \
  --region yyz \
  --vm-size shared-cpu-1x \
  --initial-cluster-size 1 \
  --volume-size 1
```

> This creates a managed Postgres cluster. Note the connection details it prints:
> ```
> Username: postgres
> Password: <generated>
> Hostname: inventory-db.internal
> Port: 5432
> Database: postgres
> Connection string: postgres://postgres:<password>@inventory-db.internal:5432/postgres
> ```
> **Save the connection string!** You'll need it in Step 2.4.

### Step 2.3: Attach Postgres to your API app

```bash
fly postgres attach inventory-db --app inventory-api
```

> This automatically sets `DATABASE_URL` as a secret on the `inventory-api` app.
> The format will be: `postgres://inventory_api:<password>@inventory-db.internal:5432/inventory_api`
>
> ⚠️ **Important**: SQLAlchemy requires `postgresql://` not `postgres://`.
> If the URL starts with `postgres://`, fix it in Step 2.4.

### Step 2.4: Set all secrets

```bash
# Generate a strong JWT secret
JWT_SECRET=$(openssl rand -hex 32)
echo "Your JWT_SECRET: $JWT_SECRET"

# Set all secrets (replace values in <brackets>)
fly secrets set \
  JWT_SECRET="$JWT_SECRET" \
  DEFAULT_ADMIN_EMAIL="admin@example.com" \
  DEFAULT_ADMIN_PASSWORD="ChangeMe123!" \
  DEFAULT_ADMIN_NAME="System Admin" \
  SENDGRID_API_KEY="" \
  ALERT_FROM_EMAIL="alerts@inventory-app.com" \
  LOW_STOCK_FUNCTION_URL="" \
  REDIS_URL="" \
  --app inventory-api
```

> **Fix DATABASE_URL if needed** (only if it starts with `postgres://`):
> ```bash
> # Check current value
> fly secrets list --app inventory-api
>
> # If DATABASE_URL starts with postgres://, fix it:
> fly secrets set DATABASE_URL="postgresql://inventory_api:<password>@inventory-db.internal:5432/inventory_api" --app inventory-api
> ```

### Step 2.5: Deploy the API

```bash
fly deploy --config fly.toml
```

> This builds the Docker image remotely and deploys it.
> Wait for: `1 machine has been successfully been updated`
>
> Verify:
> ```bash
> fly status --app inventory-api
> fly logs --app inventory-api     # Check for errors
> ```

### Step 2.6: Test the API is running

```bash
# Health check
curl https://inventory-api.fly.dev/health
# Expected: {"status":"healthy"}

# API docs
open https://inventory-api.fly.dev/docs

# Test login (default admin)
curl -X POST https://inventory-api.fly.dev/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"ChangeMe123!"}'
# Expected: {"access_token":"eyJ...","refresh_token":"eyJ...","token_type":"bearer"}
```

### Step 2.7: Deploy the Frontend

```bash
# Create frontend app
fly apps create inventory-app --org personal

# Deploy (uses fly.frontend.toml which bakes in API URL)
fly deploy --config fly.frontend.toml
```

> Verify:
> ```bash
> open https://inventory-app.fly.dev
> ```

### Step 2.8: (Optional) Add Redis for future WebSocket support

```bash
# Create Upstash Redis on Fly.io
fly redis create --name inventory-redis --region yyz

# Note the REDIS_URL it prints, then:
fly secrets set REDIS_URL="redis://default:<password>@fly-inventory-redis.upstash.io:6379" --app inventory-api
```

### Step 2.9: (Optional) Scale to multiple regions

```bash
fly scale count 3 --region yyz,iad,lhr --config fly.toml
```

---

## Part 3: Test with Kubernetes (minikube)

### Step 3.1: Start minikube

```bash
minikube start --cpus=4 --memory=4096
```

> Wait for: `Done! kubectl is now configured to use "minikube" cluster`

### Step 3.2: Point Docker to minikube's daemon

```bash
eval $(minikube docker-env)
```

> ⚠️ This is critical! It makes `docker build` build images inside minikube so K8s can find them.

### Step 3.3: Build images inside minikube

```bash
# Build backend API image
docker build -t inventory-api:latest ./backend

# Build frontend image (with minikube API URL — we'll get it after API service is created)
docker build -t inventory-frontend:latest --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 ./frontend
```

### Step 3.4: Apply Kubernetes manifests (in order!)

```bash
# 1. Create the namespace
kubectl apply -f k8s/namespace.yml

# 2. Create secrets (contains DB passwords, JWT secret, etc.)
kubectl apply -f k8s/secrets.yml

# 3. Deploy PostgreSQL (StatefulSet with 5Gi PVC)
kubectl apply -f k8s/postgres-statefulset.yml

# 4. Wait for Postgres to be ready (this takes ~30 seconds)
kubectl wait --for=condition=Ready pod -l app=postgres -n inventory --timeout=120s

# 5. Deploy Redis
kubectl apply -f k8s/redis-deployment.yml

# 6. Deploy the API (3 replicas)
kubectl apply -f k8s/api-deployment.yml

# 7. Deploy WebSocket service (2 replicas)
kubectl apply -f k8s/ws-deployment.yml

# 8. Deploy Frontend (2 replicas)
kubectl apply -f k8s/frontend-deployment.yml

# 9. Deploy monitoring
kubectl apply -f k8s/monitoring/prometheus-deployment.yml
kubectl apply -f k8s/monitoring/grafana-deployment.yml

# 10. Deploy backup CronJob
kubectl apply -f k8s/backup-cronjob.yml
```

### Step 3.5: Verify everything is running

```bash
# Check all pods
kubectl get pods -n inventory
# Expected: All pods should show STATUS=Running (wait 1-2 min for all to start)

# Check all services
kubectl get svc -n inventory
# Expected: inventory-api and inventory-frontend have TYPE=LoadBalancer

# Check persistent volume claims
kubectl get pvc -n inventory
# Expected: postgres-data-postgres-0 should be Bound
```

> If any pods are stuck in `CrashLoopBackOff`, debug with:
> ```bash
> kubectl logs <pod-name> -n inventory
> kubectl describe pod <pod-name> -n inventory
> ```

### Step 3.6: Access the services via minikube

```bash
# Option A: minikube tunnel (runs in background, gives you LoadBalancer IPs)
minikube tunnel &

# Then check the EXTERNAL-IP:
kubectl get svc -n inventory
# Use the EXTERNAL-IP of inventory-api (port 80 → maps to 8000)

# Option B: minikube service (opens in browser)
minikube service inventory-api -n inventory
minikube service inventory-frontend -n inventory
```

### Step 3.7: Test the API on K8s

```bash
# Get the API URL
API_URL=$(minikube service inventory-api -n inventory --url)
echo "API is at: $API_URL"

# Health check
curl $API_URL/health

# Test login
curl -X POST $API_URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

### Step 3.8: Test scaling

```bash
# Scale API to 5 replicas
kubectl scale deployment/inventory-api --replicas=5 -n inventory

# Watch pods come up
kubectl get pods -n inventory -w

# Scale back down
kubectl scale deployment/inventory-api --replicas=3 -n inventory
```

### Step 3.9: Clean up minikube when done

```bash
# Delete all resources
kubectl delete namespace inventory

# Stop minikube
minikube stop

# Reset Docker to local daemon
eval $(minikube docker-env -u)
```

---

## Part 4: Deploy Serverless Function (DigitalOcean Functions)

### Step 4.1: Install doctl (if not done in Part 1)

```bash
brew install doctl
doctl auth init
# → Paste your DO API token
```

### Step 4.2: Connect to the serverless namespace

```bash
# Install the serverless plugin (first time only)
doctl serverless install

# Connect to a namespace (create one if you don't have one)
doctl serverless namespaces create --label inventory-alerts --region tor1

# Connect to it
doctl serverless connect
```

### Step 4.3: Deploy the function

```bash
doctl serverless deploy serverless/
```

> Expected output:
> ```
> Deployed functions:
>   - alerts/low_stock
> ```

### Step 4.4: Get the function URL

```bash
doctl serverless functions get alerts/low_stock --url
```

> Copy the URL. It will look like:
> `https://faas-tor1-xxx.doserverless.co/api/v1/web/fn-xxx/alerts/low_stock`

### Step 4.5: Test the function

```bash
FUNCTION_URL=$(doctl serverless functions get alerts/low_stock --url)

curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "item_name": "Test Item",
    "sku": "TEST-001",
    "quantity": 3,
    "threshold": 10,
    "location": "Warehouse A",
    "recipient_emails": ["johnchen77w@gmail.com"]
  }'
```

> ⚠️ This will return an error about SendGrid API key not configured until you set it.

### Step 4.6: Set SendGrid API key in the function

```bash
# If you have a SendGrid API key:
doctl serverless deploy serverless/ \
  --env SENDGRID_API_KEY=SG.your_api_key_here \
  --env ALERT_FROM_EMAIL=alerts@inventory-app.com
```

> **Getting a SendGrid API key (free tier):**
> 1. Go to https://app.sendgrid.com/
> 2. Sign up for free (100 emails/day)
> 3. Go to Settings → API Keys → Create API Key
> 4. Name it "inventory-alerts", select "Restricted Access" → Mail Send: Full Access
> 5. Copy the key (starts with `SG.`)

### Step 4.7: Link the function URL to your Fly.io API

```bash
FUNCTION_URL=$(doctl serverless functions get alerts/low_stock --url)

fly secrets set LOW_STOCK_FUNCTION_URL="$FUNCTION_URL" --app inventory-api
```

> Now when a stock withdrawal triggers a low-stock condition, the API will POST to this function, which sends the email.

---

## Part 5: Set Up CI/CD (GitHub Actions)

### Step 5.1: Install GitHub CLI (if not done in Part 1)

```bash
brew install gh
gh auth login
# → GitHub.com → HTTPS → Login with browser
```

### Step 5.2: Generate a Fly.io deploy token

```bash
fly tokens create deploy -x 999999h --app inventory-api
```

> Copy the token. It starts with `FlyV1 ...`

### Step 5.3: Add the token as a GitHub secret

```bash
# Using GitHub CLI:
gh secret set FLY_API_TOKEN --repo johnchen77w/Inventory-Management-System

# → Paste the Fly.io token when prompted
```

> Or do it manually:
> 1. Go to https://github.com/johnchen77w/Inventory-Management-System/settings/secrets/actions
> 2. Click "New repository secret"
> 3. Name: `FLY_API_TOKEN`
> 4. Value: paste the token from Step 5.2
> 5. Click "Add secret"

### Step 5.4: Push your branch and create a PR to test CI

```bash
cd ~/Desktop/M.Eng/ECE\ 1779H\ Intro\ to\ Cloud/Inventory-Management-System

# Push the branch
git push origin claude/strange-sanderson

# Create a PR
gh pr create \
  --title "Add deployment infrastructure" \
  --body "Fly.io, K8s, CI/CD, serverless configs"
```

> The `test.yml` workflow will automatically run pytest on the PR.
> Check at: https://github.com/johnchen77w/Inventory-Management-System/actions

### Step 5.5: Merge to main to trigger deployment

```bash
# After tests pass and PR is approved:
gh pr merge --squash
```

> The `deploy.yml` workflow will:
> 1. Run tests
> 2. Deploy API to Fly.io (if tests pass)
> 3. Deploy Frontend to Fly.io (if tests pass)

---

## Verification Checklist

After completing all parts, verify everything works:

| # | Check | Command | Expected |
|---|-------|---------|----------|
| 1 | Fly.io API health | `curl https://inventory-api.fly.dev/health` | `{"status":"healthy"}` |
| 2 | Fly.io API docs | `open https://inventory-api.fly.dev/docs` | Swagger UI loads |
| 3 | Fly.io Frontend | `open https://inventory-app.fly.dev` | Page loads |
| 4 | Fly.io Login | `curl -X POST .../auth/login -d ...` | Returns JWT |
| 5 | K8s pods running | `kubectl get pods -n inventory` | All Running |
| 6 | K8s API accessible | `minikube service inventory-api -n inventory --url` | Returns URL |
| 7 | Serverless function | `curl -X POST $FUNCTION_URL -d ...` | 200 OK |
| 8 | CI test pass | Check GitHub Actions tab | ✅ green |
| 9 | CD deploy pass | Merge PR, check Actions | ✅ green |

---

## Troubleshooting

### Fly.io: "Error: could not find app"
```bash
fly apps list    # Check your app name
fly status --app <your-app-name>
```

### Fly.io: Database connection error in logs
```bash
fly secrets list --app inventory-api   # Check DATABASE_URL is set
fly postgres connect inventory-db      # Test direct DB connection
# Run: \l   to list databases
# Run: \dt  to list tables
```

### K8s: Pod in CrashLoopBackOff
```bash
kubectl logs <pod-name> -n inventory           # See error
kubectl describe pod <pod-name> -n inventory   # See events
kubectl get events -n inventory --sort-by='.lastTimestamp'
```

### K8s: Can't pull image
```bash
# Make sure you're using minikube's Docker
eval $(minikube docker-env)
docker images | grep inventory   # Should show your images
```

### Serverless: "SENDGRID_API_KEY not configured"
You need a SendGrid account and API key. See Step 4.6.

### CI/CD: "Error: No access token available"
You forgot to add `FLY_API_TOKEN` as a GitHub secret. See Step 5.3.
