# ── CloudWatch Log Group ────────────────────────────────────────────────────────
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 30   # keep 30 days of logs; adjust to reduce cost

  tags = {
    Name        = "${var.project_name}-logs"
    Environment = var.environment
  }
}
