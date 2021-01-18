#!/bin/bash

#----Script Deployment to deploy all the service----------------
#----Argument: No----------------------------------------------
#----Run "./deploy.sh------------------------------------------
#kubectl delete -f pgadmin.yaml
#kubectl create -f pgadmin.yaml
#kubectl delete -f postgres.yaml
#kubectl create -f postgres.yaml
#kubectl delete -f simserve.yaml
#kubectl create -f simserve.yaml
kubectl apply -f simserve.yaml
