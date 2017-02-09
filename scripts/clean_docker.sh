#!/bin/bash

# Require install of jq

# CentOS
# yum install -y epel-release
# yum install -y jq

# Ubuntu 
# apt-get install jq

# CoreOS ??

if [ "$#" -ne 3 ];then
        echo "Usage: $0 <user> <pkifile> <master>"
        echo "Example: $0 azureuser azureuser m1"
        exit 99
fi

USER=$1
PKIFILE=$2
MASTER=$3

echo "Starting to fetch the server information from $MASTER"
for SERVER in $(curl -s $MASTER/mesos/slaves | jq -r .slaves[].hostname)
do 
	echo "******** $SERVER ********"
	echo "- Remove Docker Containers that have Exited"
	ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USER@$SERVER "sudo docker ps -qa -f status=exited | xargs -r sudo docker rm"
	echo "- Remove Docker Containers that are dead"
	ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USER@$SERVER "sudo docker ps -qa -f status=dead | xargs -r sudo docker rm -f -v"
	echo "- Remove Docker Images"
	ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USER@$SERVER "sudo docker images -q | xargs -r sudo docker rmi"
	echo 
	echo "***********************************"	
done
