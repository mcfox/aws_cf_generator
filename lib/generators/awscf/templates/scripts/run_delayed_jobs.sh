#!/bin/sh --login

app_path="/home/deploy/app/current"
QUEUE=$1
NUM_WORKERS=$2


mkdir -p $app_path/log

case "$3" in
	start)
	echo -n "Starting delayed_job: "
	sudo su - deploy -c "cd $app_path && ./bin/delayed_job -n $NUM_WORKERS --queue=$QUEUE start >> $app_path/log/delayed_job.log";
	echo "done."
	;;
	stop)
	echo -n "Stopping delayed_job: "
	sudo su - deploy -c "cd $app_path && ./bin/delayed_job stop >> $app_path/log/delayed_job.log";
	echo "done."
	;;
	*)
	echo "Usage: $N {queue_name} {num_workers} {start|stop}" >&2
	exit 1
	;;
esac
exit 0
