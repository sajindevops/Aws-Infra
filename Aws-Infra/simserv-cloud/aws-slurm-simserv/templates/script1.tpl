#!/bin/bash

sgid=${security_grp_id}

sed -i 's/security_grp_id/$sgid/g' /home/centos/slurm-aws-startup.sh