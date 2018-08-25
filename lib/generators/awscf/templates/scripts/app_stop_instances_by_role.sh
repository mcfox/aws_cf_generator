#!/bin/bash

USAGE="Uso: app_stop_instances_by_role.sh <RAILS_ENV> <ROLE>"

RAILS_ENV=$1
ROLE=$2

if [ -z $RAILS_ENV ]  || [ -z $ROLE ]; then
  echo "Argumentos RAILS_ENV e ROLE são obrigatórios."
  echo $USAGE
  exit
fi

if [ $RAILS_ENV != 'staging' ]  && [ $RAILS_ENV != 'production' ]; then
  echo "Valores permitidos para o argumento RAILS_ENV são: staging, production."
  echo $USAGE
  exit
fi

if [ $ROLE != 'web' ]  && [ $ROLE != 'workermaster' ] && [ $ROLE != 'workertasks' ] && [ $ROLE != 'operation' ]; then
  echo "Valores permitidos para o argumento ROLE são: web, workermaster, workertasks e operation."
  echo $USAGE
  exit
fi

if [ $RAILS_ENV = 'production' ]; then
  REGION="us-east-1"
else
  REGION="us-west-2"
fi

# get instance ids
instance_ids=$(aws ec2 describe-instances --region $REGION --output text --filter "Name=tag:Name,Values=taxmap*" "Name=tag:Env,Values=$RAILS_ENV" "Name=tag:Role,Values=$ROLE" "Name=instance-state-name,Values=running" | grep INSTANCES | awk '{if ($18 == "ebs") print $9}')

# stop instances
aws ec2 stop-instances --region $REGION --instance-ids $instance_ids

