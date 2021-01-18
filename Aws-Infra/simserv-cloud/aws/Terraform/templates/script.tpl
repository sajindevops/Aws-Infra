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
