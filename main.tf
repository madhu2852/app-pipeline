provider "aws" {
  region = "us-east-1"
}
### CREATE TARGET GROUP FOR THE APP ###

resource "aws_lb_target_group" "public_alb_app" {
  name     = "pub-alb-app-${var.available_port}"
  port     = tonumber(var.available_port)
  protocol = "HTTP"
  target_type = "instance"
  vpc_id   = data.aws_vpc.ingress_vpc_id.id # use data resource to pull the info
  health_check {
    port = var.available_port
    protocol = "HTTP"
    interval = 30
    timeout = 20
    unhealthy_threshold = 10
  }
}

### CREATE LISTENER RULE FOR THE APP ###

resource "aws_lb_listener_rule" "public_alb_lstnr_rule_app" {
  listener_arn = var.PUBLIC_ALB_LSTNR_NAME
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.public_alb_app.arn
  }
  condition {
    host_header {
      values = [var.APP_FQDN]
    }
  }
}

### CREATE TARGET GROUP ATTACHMENTS FOR THE APP ###

resource "aws_lb_target_group_attachment" "public_alb_app_tg" {
  count = length(data.aws_instances.public_alb_palo_alto.ids)
  target_group_arn = aws_lb_target_group.public_alb_app.arn
  target_id        = data.aws_instances.public_alb_palo_alto.ids[count.index]
}
