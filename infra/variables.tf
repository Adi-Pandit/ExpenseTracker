# ── AWS config ────────────────────────────────────────────────────────────────
variable "aws_region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "ap-south-1"
}

variable "aws_profile" {
  description = "AWS CLI named profile to use."
  type        = string
  default     = "ledgerly"
}

# ── Project ────────────────────────────────────────────────────────────────────
variable "project_name" {
  description = "Short name used to prefix all resources."
  type        = string
  default     = "ledgerly"
}

variable "environment" {
  description = "Deployment environment label (e.g. production, staging)."
  type        = string
  default     = "production"
}

# ── Container ──────────────────────────────────────────────────────────────────
variable "container_port" {
  description = "Port the Django/gunicorn process listens on inside the container."
  type        = number
  default     = 8000
}

variable "task_cpu" {
  description = "Fargate CPU units (256 = 0.25 vCPU). Valid: 256, 512, 1024, 2048, 4096."
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Fargate memory in MiB. Must be compatible with task_cpu."
  type        = number
  default     = 512
}

variable "desired_count" {
  description = <<-EOT
    Number of running ECS tasks.
    Set to 0 to stop all tasks (compute charges stop; ECR/CloudWatch storage stays).
    Set to 1 to start again (or run: aws ecs update-service --cluster ledgerly-cluster --service ledgerly-service --desired-count 1 --profile ledgerly).
  EOT
  type        = number
  default     = 1
}

# ── Application secrets (stored in SSM Parameter Store) ────────────────────────
variable "django_secret_key" {
  description = "Django SECRET_KEY — a long random string. Never commit the real value."
  type        = string
  sensitive   = true
}

variable "database_url" {
  description = "Supabase PostgreSQL connection string: postgresql://user:pass@host:5432/db"
  type        = string
  sensitive   = true
}

variable "cors_allowed_origins" {
  description = "Comma-separated list of allowed CORS origins, e.g. https://myapp.vercel.app"
  type        = string
  default     = ""
}

variable "cron_secret" {
  description = "Secret for the cron endpoint header X-Cron-Secret."
  type        = string
  sensitive   = true
  default     = ""
}

# ── VPC ────────────────────────────────────────────────────────────────────────
variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for each public subnet (one per AZ)."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "availability_zones" {
  description = "AZs to deploy into (must match the region)."
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]
}
