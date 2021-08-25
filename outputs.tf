output "public_elb" {
    value = data.aws_resourcegroupstaggingapi_resources.load_balancer.resource_tag_mapping_list.*.resource_arn
}

output "public_elb_lstnr" {
    value = data.aws_resourcegroupstaggingapi_resources.load_balancer_lstnr.resource_tag_mapping_list.*.resource_arn
}
