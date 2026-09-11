# Ledgerly — Expense Tracker

A full-stack expense tracking app with budgets, recurring expenses, analytics, and multi-currency support.

**Stack:** React 19 + Vite (frontend) · Django 6 + DRF (backend) · PostgreSQL · JWT auth

---

## Local Development

### Prerequisites

- Python 3.13+
- Node.js 20+
- PostgreSQL running locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt

# Create backend/.env (copy and fill in values)
cp .env.example .env          # or create manually — see Environment Variables below

python manage.py migrate
python manage.py runserver    # http://127.0.0.1:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173
```

### Seed demo data

```bash
cd backend
python manage.py seed_demo_data --username <your-username>
```

---

## Environment Variables

### Backend (`backend/.env`)

```env
SECRET_KEY=your-long-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=expense_tracker
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# Production only (overrides DB_* above when set)
DATABASE_URL=postgresql://user:pass@host:5432/db

CORS_ALLOWED_ORIGINS=http://localhost:5173

CRON_SECRET=your-cron-secret
```

### Frontend (`frontend/.env`)

```env
VITE_API_URL=http://127.0.0.1:8000
```

---

## Deployment

The backend deploys to **AWS ECS Fargate** (ap-south-1). The frontend deploys to **Vercel**.

### AWS ECS — first-time setup

```bash
cd infra

# 1. Copy and fill in the vars file (contains secrets — never commit it)
cp terraform.tfvars.example terraform.tfvars

# 2. Init and apply
terraform init
terraform apply

# 3. Build and push the first Docker image
aws ecr get-login-password --region ap-south-1 --profile ledgerly \
  | docker login --username AWS --password-stdin <ECR_URL>

docker build -t <ECR_URL>:latest ./backend
docker push <ECR_URL>:latest

# 4. Force ECS to pull the new image
aws ecs update-service \
  --cluster ledgerly-cluster \
  --service ledgerly-service \
  --force-new-deployment \
  --profile ledgerly \
  --region ap-south-1
```

After the first deploy, GitHub Actions handles all subsequent deployments on every push to `master`.

### Get the backend URL

The task gets a public IP on every deploy. Run this to find it:

```bash
TASK_ARN=$(aws ecs list-tasks \
  --cluster ledgerly-cluster \
  --service-name ledgerly-service \
  --query 'taskArns[0]' --output text \
  --profile ledgerly --region ap-south-1)

ENI_ID=$(aws ecs describe-tasks \
  --cluster ledgerly-cluster --tasks "$TASK_ARN" \
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
  --output text --profile ledgerly --region ap-south-1)

aws ec2 describe-network-interfaces \
  --network-interface-ids "$ENI_ID" \
  --query 'NetworkInterfaces[0].Association.PublicIp' \
  --output text --profile ledgerly --region ap-south-1
```

Then update the `BACKEND_URL` secret in **GitHub → Settings → Secrets → Actions**.

### Stop the backend (no compute charges)

```bash
aws ecs update-service \
  --cluster ledgerly-cluster \
  --service ledgerly-service \
  --desired-count 0 \
  --profile ledgerly --region ap-south-1
```

Storage (ECR + CloudWatch) still runs at ~₹2/month.

### Start the backend again

```bash
aws ecs update-service \
  --cluster ledgerly-cluster \
  --service ledgerly-service \
  --desired-count 1 \
  --profile ledgerly --region ap-south-1
```

### Tear down everything

```bash
cd infra
terraform destroy
```

---

## GitHub Actions Secrets

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user access key (`ledgerly` user) |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `BACKEND_URL` | Current ECS task URL, e.g. `http://<ip>:8000` |
| `CRON_SECRET` | Matches `CRON_SECRET` in backend env |

---

## API

Base URL (local): `http://127.0.0.1:8000`

| Prefix | Description |
|--------|-------------|
| `/auth/` | JWT login, register, refresh, logout |
| `/api/` | Expenses, budgets, accounts, categories, recurring |
| `/dashboard/` | Overview, insights, analytics |
| `/health/` | Health check |
| `/api/docs/` | Swagger UI |
