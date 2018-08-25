#!/bin/bash --login

app_path="/home/deploy/app/current"
shared_path="/home/deploy/app/shared"

# Log output of this script to file in /tmp
set -x
exec > /tmp/app_update.log 2>&1

RAILS_ENV=$1
ROLE=$2
BUCKET_NAME=$3

if [ -z $RAILS_ENV ]; then
    echo Environment must be informed
    exit 1
fi

if [ -z ROLE ]; then
    echo Role must be informed
    exit 1
fi

if [ $RAILS_ENV = 'production' ]; then
    FILENAME=source.zip
else
    FILENAME=source-hml.zip
fi

if [ -z $ROLE ]; then
    ROLE="web"
fi


echo Updating Role: $ROLE

echo Deleting old files
rm -rf ./*
rm -rf ./.*
echo done.

echo Downloading source code from S3 : $FILENAME
wget http://taxweb-deploy.s3.amazonaws.com/$BUCKET_NAME/$FILENAME -O $FILENAME >/dev/null 2>&1
echo done.

echo Extracting source code

unzip -o -q $FILENAME
echo done.

echo Installing new gems...
cd /tmp
cd $app_path
bundle config git.allow_insecure true && bundle install --without development test
echo done.

echo Installing new javascript resources...
yarn install
echo done.

export RAILS_ENV=$RAILS_ENV

if [ $ROLE = "operation" ]; then
    # install gem backup
    cd $app_path && gem install backup -v 4.4.1 --no-ri --no-rdoc
    # install mongo shell and mongo tools
    sudo bash -c 'echo -e "[mongodb-org-4.0] \nname=MongoDB Repository \nbaseurl=https://repo.mongodb.org/yum/amazon/2013.03/mongodb-org/4.0/x86_64/ \ngpgcheck=1 \nenabled=1 \ngpgkey=https://www.mongodb.org/static/pgp/server-4.0.asc" > /etc/yum.repos.d/mongodb-org-4.0.repo'
    sudo yum install -y mongodb-org-shell mongodb-org-tools
    # seta ambiente
    echo "export APP_PATH=$app_path" >> ~/.bashrc
    #echo Running Migrations...
    rake db:migrate
    echo Updating Crontab...
    whenever -w
fi

if [ $ROLE = "web" ]; then
    echo Compiling Assets...
    rake assets:precompile
    echo Restarting nginx...
    sudo service nginx restart
    echo Restarting puma...
    sudo pkill -9 -f puma
    sudo rm -rf $shared_path/tmp/sockets/puma.sock
    cd $app_path && bundle exec puma -C config/puma.rb --daemon
fi

if [ $ROLE = "workermaster" ]; then
    cd $app_path && mkdir -p log
    echo Restarting Workers Master...
    chmod 755 $app_path/aws/scripts/run_delayed_job_master.sh
    $app_path/aws/scripts/run_delayed_job_master.sh stop
    pkill -9 -f delayed
    $app_path/aws/scripts/run_delayed_job_master.sh start
fi

if [ $ROLE = "workertasks" ]; then
    cd $app_path && mkdir -p log
    echo Restarting Workers Tasks...
    chmod 755 $app_path/aws/scripts/run_delayed_job_tasks.sh
    $app_path/aws/scripts/run_delayed_job_tasks.sh stop
    pkill -9 -f delayed
    $app_path/aws/scripts/run_delayed_job_tasks.sh start
fi

echo done Role: $ROLE
