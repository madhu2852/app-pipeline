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
}
