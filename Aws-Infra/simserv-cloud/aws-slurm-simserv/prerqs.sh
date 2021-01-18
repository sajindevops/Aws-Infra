######Prequest#################################3

sudo sed -i "s|enforcing|disabled|g" /etc/selinux/config
sudo setenforce 0
sudo yum update -y
sudo yum --nogpgcheck install wget curl epel-release nano nfs-utils -y
sudo yum --nogpgcheck install python2-pip -y
sudo pip install awscli
sudo pip install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz
sudo chmod +x /bin/cfn-*
sudo mkdir -p /nfs
sudo sed -i "s|@SUBNETID@|subnet-07fd3a799b83fa30c}|g" /home/centos/slurm-aws-startup.sh
sudo sed -i "s|@KEYNAME@|Slurm-key-2020|g" /home/centos/slurm-aws-startup.sh
sudo sed -i "s|@S3BUCKET@|s3://slurm-common1|g" /home/centos/slurm-aws-startup.sh
sudo sed -i "s|@BASEAMI@|ami-0cb72d2e599cffbf9|g" /home/centos/slurm-aws-startup.sh
sudo sed -i "s|@PRIVATE1@|subnet-07fd3a799b83fa30c|g" /home/centos/slurm-aws-startup.sh
sudo sed -i "s|@PRIVATE2@|subnet-0e8aeba843c58e698|g" /home/centos/slurm-aws-startup.sh
sudo sed -i "s|@PRIVATE3@|subnet-0fb818c58048da2c3|g" /home/centos/slurm-aws-startup.sh
chmod +x /home/centos/slurm-mgmtd.sh
sudo sed -i -e 's/\r$//' /home/centos/slurm-aws-startup.sh
sudo sed -i -e 's/\r$//' /home/centos/slurm-aws-shutdown.sh
sudo sed -i -e 's/\r$//' /home/centos/slurm-mgmtd.sh
sudo /home/centos/slurm-mgmtd.sh ${SlurmVersion} ${PrivateSubnet1.AvailabilityZone},${PrivateSubnet2.AvailabilityZone},${PrivateSubnet3.Availabi}