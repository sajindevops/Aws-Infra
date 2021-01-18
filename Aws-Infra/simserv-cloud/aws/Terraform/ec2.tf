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
  security_groups = [aws_security_group.simserv_sg.id]
}

data "template_file" "script" {
  template = "${file("templates/script.tpl")}"
  vars = {
    efs_id = "${aws_efs_file_system.efs.id}"
  }
}
resource "aws_instance" "simserv" {
  ami           = var.AMIS
  instance_type = "c5.xlarge"
  subnet_id     = var.subnet
  vpc_security_group_ids = [aws_security_group.simserv_sg.id]
  key_name = var.keyname
  associate_public_ip_address = false
  user_data = "${data.template_file.script.rendered}"
  root_block_device {
    volume_size = "100"
  }
#  provisioner "file" {
#    connection {
#    host        = coalesce(self.public_ip, self.private_ip)
#    type        = "ssh"
#    user        = "centos"
#    private_key = file("simservvmkey030620.pem")
#  }
#    source      = "script.tpl"
#    destination = "/tmp/script.tpl"
#  }
#  provisioner "remote-exec" {
#    connection {
#    host        = coalesce(self.public_ip, self.private_ip)
#    type        = "ssh"
#    user        = "centos"
#    private_key = file("simservvmkey030620.pem")
#  }
#    inline = [
#      "chmod +x /tmp/script.tpl",
#      "/tmp/script.tpl",
#    ]
#  }

#  provisioner "file" {
#    connection {
#    host        = coalesce(self.public_ip, self.private_ip)
#    type        = "ssh"
#    user        = "centos"
#    private_key = file("simservvmkey030620.pem")
#  }
#    source      = "script.sh"
#    destination = "/tmp/script.sh"
#  }
  provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("simservvmkey030620.pem")
  }
    source      = ".env"
    destination = "/tmp/.env"
  }
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("simservvmkey030620.pem")
  }
    source      = "ads_2020_update2.0_linux_x64.tar"
    destination = "/tmp/ads_2020_update2.0_linux_x64.tar"
  }
  
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("simservvmkey030620.pem")
  }
    source      = "keysight_simserv-2.0.0b2.dev135+g0adef16-py2.py3-none-any.whl"
    destination = "/tmp/keysight_simserv-2.0.0b2.dev135+g0adef16-py2.py3-none-any.whl"
  }
  
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("simservvmkey030620.pem")
  }
    source      = "sitecluster"
    destination = "/tmp/sitecluster"
  }
  
    provisioner "file" {
    connection {
    host        = coalesce(self.public_ip, self.private_ip)
    type        = "ssh"
    user        = "centos"
    private_key = file("simservvmkey030620.pem")
  }
    source      = "sitecluster.py"
    destination = "/tmp/sitecluster.py"
  }
#  provisioner "remote-exec" {
#    connection {
#    host        = coalesce(self.public_ip, self.private_ip)
#    type        = "ssh"
#    user        = "centos"
#    private_key = file("simservvmkey030620.pem")
#  }
#    inline = [
#      "chmod +x /tmp/script.sh",
#      "/tmp/script.sh",
#    ]
#  }
}
