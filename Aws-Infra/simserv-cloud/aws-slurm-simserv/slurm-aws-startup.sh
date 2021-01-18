#!/bin/bash
# DESCRIPTION: SLURM STARTUP

export SLURM_HEADNODE=$(curl -sS http://169.254.169.254/latest/meta-data/local-ipv4)
export AWS_DEFAULT_REGION=$(curl -sS http://169.254.169.254/latest/dynamic/instance-identity/document | grep region | awk '{print $3}' | sed 's/"//g' | sed 's/,//g')
AWS_DEFAULT_MAC=$(curl -sS http://169.254.169.254/latest/meta-data/mac)
export AWS_SUBNET_ID=@SUBNETID@
export AWS_AMI=@BASEAMI@
export AWS_KEYNAME=@KEYNAME@
export S3BUCKET=@S3BUCKET@
export SLURM_POWER_LOG=/var/log/power_save.log

##############################################d
# DONOT EDIT BELOW THIS LINE
##############################################


function nametoip()
{
    echo $1 | tr "-" "." | cut -c 4-
}

function aws_startup()
{
    TMPFILE=$(mktemp)
    cat << END > $TMPFILE
#!/bin/bash -xe
sudo sed -i "s|enforcing|disabled|g" /etc/selinux/config
sudo yum --nogpgcheck install wget curl epel-release nfs-utils -y 
sudo yum install -y yum-utils 
sudo yum install python2-pip -y
sudo pip install awscli
sudo yum -y install git
cd /home/centos
sudo git clone https://github.com/aws/efs-utils
cd efs-utils
sudo yum -y install make
sudo yum -y install rpm-build
sudo make rpm
sudo yum -y install ./build/amazon-efs-utils*rpm
sudo mkdir -p /opt/ads/
# Mount EFS
sudo mount -t efs slurm_efs_id:/ /opt/ads
sudo mount -t efs slurm_efs_id:/ /project/code/simserv/data
sudo sed -i '$a 'slurm_efs_id':/ /opt/ads efs defaults,_netdev 0 0' /etc/fstab
sudo sed -i '$a 'slurm_efs_id':/ /project/code/simserv/data efs defaults,_netdev 0 0' /etc/fstab
sudo mkdir -p /nfs
sudo cp /home/centos/slurm-compute1.sh /home/centos/slurm-compute.sh
chmod +x /home/centos/slurm-compute.sh
sudo /home/centos/slurm-compute.sh $SLURM_HEADNODE
END

    aws ec2 run-instances --image-id $AWS_AMI --instance-type $3 --key-name $AWS_KEYNAME \
                      --security-group-ids sg-028bc1e61119b8194 --subnet-id $AWS_SUBNET_ID \
                      --user-data file://${TMPFILE} --region $AWS_DEFAULT_REGION --private-ip-address $2 \
                                  --block-device-mappings '[ {"DeviceName":"/dev/sda1","Ebs": {"DeleteOnTermination": true}} ]' \
                      --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$1_slurm-compute-processor}]" \
    >> $SLURM_POWER_LOG 2>&1


    rm -rf $TMPFILE
}

export SLURM_ROOT=/nfs/slurm
echo "`date` Resume invoked $0 $*" >> $SLURM_POWER_LOG
hosts=$($SLURM_ROOT/bin/scontrol show hostnames $1)
num_hosts=$(echo "$hosts" | wc -l)
aws cloudwatch put-metric-data --metric-name BurstNodeRequestCount --namespace SLURM --value $num_hosts --region $AWS_DEFAULT_REGION
for host in $hosts
do
   private_ip=$(nametoip $host)
   if [[ $host == *ip-10-248-156* ]]; then
      export AWS_SUBNET_ID=subnet-07fd3a799b83fa30c
      aws_startup $host $private_ip c5.2xlarge
   elif [[ $host == *ip-10-248-157* ]]; then
      export AWS_SUBNET_ID=subnet-0e8aeba843c58e698
      aws_startup $host $private_ip c5.2xlarge
   elif [[ $host == *ip-10-248-158* ]]; then
      export AWS_SUBNET_ID=subnet-0fb818c58048da2c3
      aws_startup $host $private_ip c5.2xlarge
   fi


   $SLURM_ROOT/bin/scontrol update nodename=$host nodeaddr=$private_ip nodehostname=$host
done
