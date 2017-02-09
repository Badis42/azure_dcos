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
	ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USER@$SERVER "df -h | grep sd[a,c]"
done
