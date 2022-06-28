# Create NLB

resource "aws_lb" "test" {
  name               = "test-lb-tf"
  internal           = false
  load_balancer_type = "network"
  subnets            = ["subnet-xxx","subnet-xxx"]

  enable_deletion_protection = false

  tags = {
    Environment = "test-nlb"
  }
}

resource "aws_ec2_traffic_mirror_target" "nlb" {
  description               = "NLB target"
  network_load_balancer_arn = aws_lb.test.arn
}

resource "aws_ram_resource_share" "example" {
  name                      = "example"
  allow_external_principals = true # needed if the account is out of OU else false
  tags = {
    Environment = "test-share"
  }
}
resource "aws_ram_resource_association" "example" {
  resource_arn       = aws_ec2_traffic_mirror_target.nlb.arn
  resource_share_arn = aws_ram_resource_share.example.arn
}
resource "aws_ram_principal_association" "example" {
  principal          = "xxx"
  resource_share_arn = aws_ram_resource_share.example.arn
}


# Target Account Accept the Share - On the target Account.



resource "aws_ram_resource_share_accepter" "receiver_accept" {
  share_arn = "arn:aws:ram:us-east-1:xxx:resource-share/xxx"
}
