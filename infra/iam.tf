# ── ECS Task Execution Role ─────────────────────────────────────────────────────
# Used by the ECS agent itself to pull images from ECR and push logs to CloudWatch.
resource "aws_iam_role" "ecs_execution" {
  name = "${var.project_name}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ECSTasksAssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-ecs-execution-role"
  }
}

# AWS managed policy: ECR pull + CloudWatch logs
resource "aws_iam_role_policy_attachment" "ecs_execution_managed" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Extra policy: read SSM parameters (for secrets passed to the container)
resource "aws_iam_role_policy" "ecs_execution_ssm" {
  name = "${var.project_name}-ecs-ssm-read"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ReadSSMParams"
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${var.project_name}/*"
      }
    ]
  })
}

# ── ECS Task Role ───────────────────────────────────────────────────────────────
# Assumed by the application code running inside the container.
# Add permissions here if Django ever needs to call AWS APIs (S3, SES, etc.).
resource "aws_iam_role" "ecs_task" {
  name = "${var.project_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ECSTasksAssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-ecs-task-role"
  }
}

# ── SSM Parameters (secrets) ────────────────────────────────────────────────────
# Stored as SecureString (encrypted by the default AWS-managed KMS key).
# The ECS execution role above reads these at task startup.

resource "aws_ssm_parameter" "django_secret_key" {
  name        = "/${var.project_name}/DJANGO_SECRET_KEY"
  description = "Django SECRET_KEY"
  type        = "SecureString"
  value       = var.django_secret_key

  tags = {
    Environment = var.environment
  }

  lifecycle {
    ignore_changes = [value]  # Prevent Terraform from overwriting manual updates
  }
}

resource "aws_ssm_parameter" "database_url" {
  name        = "/${var.project_name}/DATABASE_URL"
  description = "Supabase PostgreSQL connection string"
  type        = "SecureString"
  value       = var.database_url

  tags = {
    Environment = var.environment
  }

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "cron_secret" {
  name        = "/${var.project_name}/CRON_SECRET"
  description = "Secret for X-Cron-Secret header"
  type        = "SecureString"
  value       = var.cron_secret == "" ? "not-configured" : var.cron_secret

  tags = {
    Environment = var.environment
  }

  lifecycle {
    ignore_changes = [value]
  }
}
