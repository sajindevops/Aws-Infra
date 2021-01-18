####Simserv-slurm-instance deployment###########################

PreREqs:

1. AccessKey and Secretkes are used with existing user it can be replaces in the varibale.tf file
2, Secret key(simservvmkey030620.pem) to access the current instance also used with exisitng user in the varibale.tf file
3, install Terraform on the EC2 deploy/jump instance use t2.free, also keep all the components in the same Terraform folder

###############################Terraform installation#####################


sudo yum install wget unzip

sudo wget https://releases.hashicorp.com/terraform/0.12.2/terraform_0.12.2_linux_amd64.zip

sudo unzip ./terraform_0.12.2_linux_amd64.zip –d /usr/local/bin


check if it's done 

terraform –v

Setup:

1,Copy the Terraform folder to the EC2 instance or use own folder

Componets are ec2.tf  provider.tf  script.sh  script.tpl  securitygroup.tf  simservvmkey030620.pem  sitecluster  sitecluster.py  templates  _.env variable.tf also copy "ads*tar & simserv*whl file

use " mv _.env .env" ----\\\ the file name should be .env

2, run "terraform plan" in the same location (makesure terraform has installed) 
3, run "terraform apply" in the same location #//// ------>>>>>> it will ask permission hence please type 'yes' and enter

it might take a while to deploy all the components (approximatly 90 minutes)

4, check "ps -eH | grep -i simserv"  if the simserv process available then it can be used
5, api address "<private_IP>:port"  #///////------> get the newly create Instance IP (public for now)


Note: if there is a VPC for Tvpc to access to the license server then replace the VPC/Security group

############################################################Troubleshoot & update the value###################################################################

if there is any changes on varibles please check the below components

variable.tf, ec2.tf, *slurm-aws-startup.sh* and inside template script*.tpl

in head node all the slurm components sits in /nfs/slurm/bin/*slurm-aws-startup.sh*  -- if any mount issue or security group issue please check once installation is done.

/var/log/power*  this logs will help to check the process of slurm

if efs has not populated porperly this might be some cashe issue, hence update the "EFS" in /nfs/slurm/bin/*slurm-aws-startup.sh* (mostly this is the one which does all the works)

#####################################################################################################################################
