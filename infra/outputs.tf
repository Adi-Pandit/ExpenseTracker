# ── Outputs ─────────────────────────────────────────────────────────────────────

output "ecr_repository_url" {
  description = "ECR repository URL — used by GitHub Actions to push images."
  value       = aws_ecr_repository.app.repository_url
}

output "ecr_repository_name" {
  description = "ECR repository name."
  value       = aws_ecr_repository.app.name
}

output "ecs_cluster_name" {
  description = "ECS cluster name — used by GitHub Actions to redeploy."
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name — used by GitHub Actions to redeploy."
  value       = aws_ecs_service.app.name
}

output "aws_region" {
  description = "AWS region."
  value       = var.aws_region
}

output "get_task_ip_command" {
  description = "Run this command to get the current task's public IP after deployment."
  value       = <<-EOT
    aws ecs list-tasks \
      --cluster ${aws_ecs_cluster.main.name} \
      --service-name ${aws_ecs_service.app.name} \
      --query 'taskArns[0]' --output text \
      --profile ${var.aws_profile} --region ${var.aws_region} \
    | xargs -I{} aws ecs describe-tasks \
        --cluster ${aws_ecs_cluster.main.name} \
        --tasks {} \
        --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
        --output text --profile ${var.aws_profile} --region ${var.aws_region} \
    | xargs -I{} aws ec2 describe-network-interfaces \
        --network-interface-ids {} \
        --query 'NetworkInterfaces[0].Association.PublicIp' \
        --output text --profile ${var.aws_profile} --region ${var.aws_region}
  EOT
}

output "stop_command" {
  description = "Scale tasks to 0 (no compute charges while stopped)."
  value       = "aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.app.name} --desired-count 0 --profile ${var.aws_profile} --region ${var.aws_region}"
}

output "start_command" {
  description = "Scale tasks back to 1."
  value       = "aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.app.name} --desired-count 1 --profile ${var.aws_profile} --region ${var.aws_region}"
}
