resource "aws_security_group" "simserv_sg" {
  name        = "simserv_sg"
  description = "security group that allows simserv traffic"
  vpc_id      = var.vpc
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
####################################################ssh-22###################################
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["156.140.0.0/15"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["141.121.0.0/16"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["141.182.0.0/15"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["146.208.0.0/16"]
  }
 ####################################################Api-5090################################### 
   ingress {
    from_port   = 5090
    to_port     = 5090
    protocol    = "tcp"
    cidr_blocks = ["156.140.0.0/15"]
  }
  ingress {
    from_port   = 5090
    to_port     = 5090
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
  ingress {
    from_port   = 5090
    to_port     = 5090
    protocol    = "tcp"
    cidr_blocks = ["141.121.0.0/16"]
  }
  ingress {
    from_port   = 5090
    to_port     = 5090
    protocol    = "tcp"
    cidr_blocks = ["141.182.0.0/15"]
  }
  ingress {
    from_port   = 5090
    to_port     = 5090
    protocol    = "tcp"
    cidr_blocks = ["146.208.0.0/16"]
  } 
 ####################################################postgres-5432################################### 
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["156.140.0.0/15"]
  }
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["141.121.0.0/16"]
  }
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["141.182.0.0/15"]
  }
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["146.208.0.0/16"]
  }
  
  tags = {
    Name = "simsevsg"
  }
} 

resource "aws_security_group_rule" "nfsrule" {
  type              = "ingress"
  from_port         = 2049
  to_port           = 2049
  protocol          = "tcp"
  security_group_id = "${aws_security_group.simserv_sg.id}"
  source_security_group_id = "${aws_security_group.simserv_sg.id}"
}
