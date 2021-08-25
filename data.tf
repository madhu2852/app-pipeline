## VPC ID ##


data "aws_vpc" "ingress_vpc_id" {
  filter {
    name   = "tag:Name"
    values = ["gwlb_vpc"]
  }
}

## Get Palo Alto EC2 IDS ###

data "aws_instances" "public_alb_palo_alto" {
  filter {
    name   = "tag:Name"
    values = ["firewall_instances-2","firewall_instances-1"]
  }
  instance_state_names = ["running"]
}

## Public ALB ARN ##


# data "aws_resourcegroupstaggingapi_resources" "load_balancer" {
#   resource_type_filters = ["elasticloadbalancing:loadbalancer"]

#   tag_filter {
#     key    = "Name"
#     values = ["public-alb-dev","public-alb-stg"]
#   }
# }

data "aws_resourcegroupstaggingapi_resources" "load_balancer" {
  resource_type_filters = ["elasticloadbalancing:loadbalancer"]

  tag_filter {
    key    = "Name"
    values = [var.PUBLIC_ALB_NAME]
  }
}

## Public ALB LISTENER ARN ##

# data "aws_resourcegroupstaggingapi_resources" "load_balancer_lstnr" {
#   resource_type_filters = ["elasticloadbalancing:listener"]

#   tag_filter {
#     key    = "Name"
#     values = ["public-alb-lstnr-dev","public-alb-lstnr-stg"]
#   }
# }

data "aws_resourcegroupstaggingapi_resources" "load_balancer_lstnr" {
  resource_type_filters = ["elasticloadbalancing:listener"]

  tag_filter {
    key    = "Name"
    values = [var.PUBLIC_ALB_LSTNR_NAME]
  }
}

## INTERNAL APP CERT LOOKUP BY TAG NAME ##
data "aws_resourcegroupstaggingapi_resources" "internal_cert" {
  resource_type_filters = ["acm:certificate"]

  tag_filter {
    key    = "Name"
    values = [var.INTERNAL_CERT_TAG_NAME_VALUE]
  }
}

