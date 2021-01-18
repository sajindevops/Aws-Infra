resource "aws_efs_file_system" "efs" {
  creation_token   = "EFS Shared Data"
  performance_mode = "generalPurpose"
tags = {
    Name = "EFS Shared Data"
  }
}
resource "aws_efs_mount_target" "efs" {
  file_system_id  = "${aws_efs_file_system.efs.id}"
  subnet_id       = var.subnet
  security_groups = [aws_security_group.simserv_sgg.id]
}

data "template_file" "script" {
  template = "${file("templates/script.tpl")}"
  vars = {
    efs_id = "${aws_efs_file_system.efs.id}"
  }
}
data "template_file" "script1" {
  template = "${file("templates/script1.tpl")}"
  vars = {
    security_grp_id = "${aws_security_group.simserv_sgg.id}"
  }
}

resource "aws_instance" "simserv" {
  ami           = var.AMIS
  instance_type = "c5.xlarge"
  subnet_id     = var.subnet
  vpc_security_group_ids = [aws_security_group.simserv_sgg.id]
  key_name = var.keyname
  associate_public_ip_address = false
  user_data = "${data.template_file.script.rendered}"
  root_block_device {
    volume_size = "100"
  }

  provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = ".env"
    destination = "/tmp/.env"
  }
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "ads_2020_update2.0_linux_x64.tar"
    destination = "/tmp/ads_2020_update2.0_linux_x64.tar"
  }
  
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "keysight_simserv-2.0.0b2.dev135+g0adef16-py2.py3-none-any.whl"
    destination = "/tmp/keysight_simserv-2.0.0b2.dev135+g0adef16-py2.py3-none-any.whl"
  }
  
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "sitecluster"
    destination = "/tmp/sitecluster"
  }
  
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "sitecluster.py"
    destination = "/tmp/sitecluster.py"
  }
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "slurm-17.11.8.tar.bz2"
    destination = "/home/centos/slurm-17.11.8.tar.bz2"
  }
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "slurm-compute.sh"
    destination = "/home/centos/slurm-compute1.sh"
  }
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "slurm.conf"
    destination = "/home/centos/slurm.conf"
  }
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "slurm-mgmtd.sh"
    destination = "/home/centos/slurm-mgmtd.sh"
  }
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "slurm-aws-startup.sh"
    destination = "/home/centos/slurm-aws-startup.sh"
  }
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "gres.conf"
    destination = "/home/centos/gres.conf"
  }
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "Slurm-key-2020.pem"
    destination = "/home/centos/Slurm-key-2020.pem"
  }
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "slurm-aws-shutdown.sh"
    destination = "/home/centos/slurm-aws-shutdown.sh"
  }
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "config"
    destination = "/tmp/config"
  }
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("Slurm-key-2020.pem")
  }
    source      = "credentials"
    destination = "/tmp/credentials"
  }
}
