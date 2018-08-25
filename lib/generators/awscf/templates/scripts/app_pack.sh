#!/bin/bash

pwd=$(pwd)
if [[ $pwd =~ .*"/aws/scripts" ]]; then
  cd ../..
elif [[ $pwd =~ .*"/aws" ]]; then
  cd ..
fi

mkdir -p dist
RAILS_ENV=$1
APP_NAME=taxmap

# get current branch
BRANCH=`git branch | grep "*" | awk '{print $2}'`

# if RAILS_ENV was not set on the call, define it based on the current branch
if [ -z "$RAILS_ENV" ]; then
  if [ $BRANCH = 'master' ]; then
    RAILS_ENV="production"
  else
    RAILS_ENV="staging"
  fi
fi

# define the filename
if [ $RAILS_ENV = 'staging' ]; then
    FILENAME=source-hml.zip
else
    FILENAME=source.zip
fi

echo Packing branch $BRANCH to $FILENAME
git archive -o dist/$FILENAME $BRANCH
git show $BRANCH:aws/scripts/app_update.sh > dist/app_update.sh
s3cmd sync dist/app_update.sh s3://taxweb-deploy/$APP_NAME/app_update.sh
git show $BRANCH:aws/nginx/nginx_default.conf > dist/nginx_default.conf
s3cmd sync dist/nginx_default.conf s3://taxweb-deploy/$APP_NAME/nginx_default.conf
git show $BRANCH:aws/nginx/app_nginx.conf > dist/app_nginx.conf
s3cmd sync dist/app_nginx.conf s3://taxweb-deploy/$APP_NAME/app_nginx.conf

s3cmd sync dist/$FILENAME s3://taxweb-deploy/$APP_NAME/$FILENAME

s3cmd setacl s3://taxweb-deploy/$APP_NAME/$FILENAME --acl-public
s3cmd setacl s3://taxweb-deploy/$APP_NAME/app_update.sh --acl-public
s3cmd setacl s3://taxweb-deploy/$APP_NAME/nginx_default.conf --acl-public
s3cmd setacl s3://taxweb-deploy/$APP_NAME/app_nginx.conf --acl-public
