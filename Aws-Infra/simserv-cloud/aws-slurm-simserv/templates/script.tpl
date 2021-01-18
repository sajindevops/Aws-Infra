#!/bin/bash
sudo yum install -y yum-utils
sudo yum -y install git
sudo git clone https://github.com/aws/efs-utils
cd efs-utils
sudo yum -y install make
sudo yum -y install rpm-build
sudo make rpm
sudo yum -y install ./build/amazon-efs-utils*rpm
# Mount EFS
sudo mkdir -p /opt/ads/
sudo mkdir -p /project/code/simserv/data/inbound
efs_id="${efs_id}"
while  [ -z $efs_id ]
do
sleep 30
efs_id="${efs_id}"
done

sudo mount -t efs $efs_id:/ /opt/ads
sudo mount -t efs $efs_id:/ /project/code/simserv/data
sudo sed -i '$a '$efs_id':/ /opt/ads efs defaults,_netdev 0 0' /etc/fstab
sudo sed -i '$a '$efs_id':/ /project/code/simserv/data efs defaults,_netdev 0 0' /etc/fstab
####################################################simservdeployment##############################
sudo mkdir -p /project/code/simserv/sitecluster/bin 
sudo yum install -y epel-release \
which \
python3 \
python3-devel \
gcc \
libXau libXmu libGLU \
postgresql-libs \
postgresql-devel
sudo mv /tmp/.env /project/code/simserv
sudo mv /tmp/sitecluster /tmp/sitecluster.py /project/code/simserv/sitecluster/bin/
sudo mv /tmp/.env /project/code/simserv
########################################################privateIpAssign################################
prvIp=`hostname -i`
sudo sed -i 's/hostPubIp/'$prvIp'/' /project/code/simserv/.env
sudo mv /tmp/ads_2020_update2.0_linux_x64.tar /project/code/simserv/
sudo mv /tmp/keysight_simserv-2.0.0b2.dev135+g0adef16-py2.py3-none-any.whl /project/code/simserv/
cd /project/code/simserv/
sudo python3 -m venv /project/code/simserv/
sudo tar -xvf /project/code/simserv/ads_2020_update2.0_linux_x64.tar
sudo cd /project/code/simserv/
sudo ./SETUP.SH -i silent -DUSER_INSTALL_DIR=/opt/ads/
sudo /project/code/simserv/bin/python -m pip install /project/code/simserv/keysight_simserv-2.0.0b2.dev135+g0adef16-py2.py3-none-any.whl
sudo /project/code/simserv/bin/python -m pip install psycopg2

############################################Slurm-setup###############################################

sudo sed -i "s|enforcing|disabled|g" /etc/selinux/config
sudo setenforce 0
sudo yum update -y
sudo yum --nogpgcheck install wget curl epel-release nano nfs-utils -y
sudo yum --nogpgcheck install python2-pip -y
sudo pip install awscli
sudo pip install https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-latest.tar.gz
sudo chmod +x /bin/cfn-*
sudo mkdir -p /nfs
sudo mkdir /root/.aws
sudo mv /tmp/config /root/.aws/
sudo mv /tmp/credentials /root/.aws/
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
sudo sed -i -e 's/\r$//' /home/centos/slurm-compute1.sh
sudo sed -i  "s/slurm_efs_id/fs-e7c64756/g" /home/centos/slurm-aws-startup.sh
sudo /home/centos/slurm-mgmtd.sh 17.11.8 eu-west-3a,eu-west-3b,eu-west-3c ip-10-248-156-[6-250],ip-10-248-157-[6-250],ip-10-248-158-[6-250]

sudo mv /home/centos/slurm-17.11.8.tar.bz2 /tmp/
sudo mv /home/centos/slurm.conf /tmp/
sudo mv /home/centos/gres.conf /tmp/
sudo mv /home/centos/slurm-aws-startup.sh /tmp/
sudo mv /home/centos/slurm-aws-shutdown.sh /tmp/
sudo mv /home/centos/slurm-mgmtd.sh /tmp/
sudo mv /home/centos/slurm-17.11.8 /tmp/
sudo mv /home/centos/*.pem /root/
######Postgresql installation#########33

sudo yum -y install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo sed -i '$a host all all 0.0.0.0/0 md5' /var/lib/pgsql/data/pg_hba.conf
sudo sed -i '/^search/ s/$/ gnt.is.keysight.com keysight.com/' /etc/resolv.conf
sudo sed -i '$a nameserver 10.127.64.11' /etc/resolv.conf
sudo sed -i '$a nameserver 10.127.65.11' /etc/resolv.conf
sudo sed -i '$a nameserver 10.127.72.11' /etc/resolv.conf
sudo sed -i "/listen_addresses =*/c \listen_addresses = '*' # what IP address(es) to listen on;" /var/lib/pgsql/data/postgresql.conf
cd /project/code/simserv/
sudo chmod a+x -R /project/code/simserv/sitecluster/
sudo chmod a+x -R /project/code/simserv/data/inbound
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -i -u postgres psql -v ON_ERROR_STOP=1 --username='postgres' -c "CREATE DATABASE postgresdb;"
sudo -i -u postgres psql -v ON_ERROR_STOP=1 --username='postgres' -c "alter user postgres with password 'password#123';"
sudo rm -rf /project/code/simserv/linux_x86_64 /project/code/simserv/dongle_sup
cd /project/code/simserv/
sudo cd /project/code/simserv/
sudo /project/code/simserv/bin/simserv db upgrade
sudo /project/code/simserv/bin/simserv run  &
touch /project/code/simserv/done
