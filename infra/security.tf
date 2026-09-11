# ── Security Group: ECS Task ────────────────────────────────────────────────────
# The task runs in a public subnet with a public IP.
# Only port 8000 (Django/gunicorn) is open to the internet.
resource "aws_security_group" "ecs_task" {
  name        = "${var.project_name}-ecs-task-sg"
  description = "Allow inbound HTTP on port 8000 for the Django backend"
  vpc_id      = aws_vpc.main.id

  # Inbound: Django/gunicorn
  ingress {
    description = "Django gunicorn"
    from_port   = var.container_port
    to_port     = var.container_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound: unrestricted (needed for Supabase, ECR pulls, etc.)
  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-ecs-task-sg"
    Environment = var.environment
  }
}
