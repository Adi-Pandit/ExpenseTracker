# ── ECS Cluster ────────────────────────────────────────────────────────────────
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "disabled"   # Set to "enabled" for detailed metrics (~$0.50/month extra)
  }

  tags = {
    Name        = "${var.project_name}-cluster"
    Environment = var.environment
  }
}

# ── Task Definition ─────────────────────────────────────────────────────────────
resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project_name}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "${var.project_name}-backend"
      image     = "${aws_ecr_repository.app.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]

      # Plain environment variables (non-sensitive)
      environment = [
        { name = "DEBUG",                value = "False" },
        { name = "CORS_ALLOWED_ORIGINS", value = var.cors_allowed_origins },
      ]

      # Secrets pulled from SSM Parameter Store at task startup
      secrets = [
        {
          name      = "SECRET_KEY"
          valueFrom = aws_ssm_parameter.django_secret_key.arn
        },
        {
          name      = "DATABASE_URL"
          valueFrom = aws_ssm_parameter.database_url.arn
        },
        {
          name      = "CRON_SECRET"
          valueFrom = aws_ssm_parameter.cron_secret.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      # Basic health check — ECS restarts the task if this fails 3× in a row
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}/health/ || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60   # give migrations time to run on first start
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-task"
    Environment = var.environment
  }
}

# ── ECS Service ─────────────────────────────────────────────────────────────────
resource "aws_ecs_service" "app" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  # Force new deployment when the task definition changes (e.g., new image tag)
  force_new_deployment = true

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs_task.id]
    assign_public_ip = true   # gives the task a public IP; no NAT Gateway needed
  }

  # Graceful: let the old task drain for 30s before terminating
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  lifecycle {
    # Allow desired_count to be changed outside Terraform (e.g., manual scale to 0)
    # without Terraform reverting it on the next apply.
    ignore_changes = [desired_count]
  }

  tags = {
    Name        = "${var.project_name}-service"
    Environment = var.environment
  }
}
