#!/bin/bash

USAGE="Uso: app_deploy.sh <RAILS_ENV>"

pwd=$(pwd)
if [[ $pwd =~ .*"/aws/scripts" ]]; then
  cd ../..
elif [[ $pwd =~ .*"/aws" ]]; then
  cd ..
fi

RAILS_ENV=$1

if [ -z $RAILS_ENV ]; then
  echo "Argumento RAILS_ENV é obrigatório."
  echo $USAGE
  exit
fi

if [ $RAILS_ENV != 'staging' ]  && [ $RAILS_ENV != 'production' ]; then
  echo "Valores permitidos para o argumento RAILS_ENV são: staging, production."
  echo $USAGE
  exit
fi

echo "Preparing application for deployment..."
./aws/scripts/app_pack.sh $RAILS_ENV
echo "Done."

echo "Rebooting AWS instances to deploy new version."
./aws/scripts/app_stop_instances_by_role.sh $RAILS_ENV web
./aws/scripts/app_stop_instances_by_role.sh $RAILS_ENV workermaster
./aws/scripts/app_stop_instances_by_role.sh $RAILS_ENV workertasks
./aws/scripts/app_stop_instances_by_role.sh $RAILS_ENV operation
echo "Done."

