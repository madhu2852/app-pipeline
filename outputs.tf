output "public_elb" {
    value = data.aws_resourcegroupstaggingapi_resources.load_balancer.resource_tag_mapping_list.*.resource_arn
}

output "public_elb_lstnr" {
    value = data.aws_resourcegroupstaggingapi_resources.load_balancer_lstnr.resource_tag_mapping_list.*.resource_arn
}

output "internal_app_cert" {
    value = data.aws_resourcegroupstaggingapi_resources.internal_cert.resource_tag_mapping_list.*.resource_arn
}
output "lstnr_rule_arn" {
    value = aws_lb_listener_rule.public_alb_lstnr_rule_app.arn
}
output "target_group_arn" {
    value = aws_lb_target_group.public_alb_app.arn
}
