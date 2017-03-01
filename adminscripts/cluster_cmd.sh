#!/bin/bash

# Set username and name of the private PKI file for that username; the PKI file must allows access without password
USERNAME=centos
PKIFILE=centos.pem


if [ "$#" -ne 4 ];then
	echo "Usage: $0 <numMasters> <numAgents> <numPublicAgents> <cmd>"
	echo "Example: $0 1 3 1"
	exit 99
fi

NUM_MASTERS=$1
NUM_AGENTS=$2
NUM_PUBLIC_AGENTS=$3
CMD=$4

re='^[0-9]+$'

if ! [[ $NUM_MASTERS =~ $re ]] ; then
	echo "Usage: $0 <numMasters> <numAgents> <numPublicAgents>"
	echo "numMasters must be a number"
	exit 91
fi

if ! [[ $NUM_AGENTS =~ $re ]] ; then
	echo "Usage: $0 <numMasters> <numAgents> <numPublicAgents>"
	echo "numAgents must be a number"
	exit 92
fi

if ! [[ $NUM_PUBLIC_AGENTS =~ $re ]] ; then
	echo "Usage: $0 <numMasters> <numAgents> <numPublicAgents>"
	echo "numPublicAgents must be a number"
	exit 93
fi

echo $CMD

OFFSET=10
PREFIX="10.10.0."
for (( i=1; i<=$NUM_MASTERS; i++))
do
        SERVER=${PREFIX}$(( $OFFSET + $i ))
	echo $SERVER
        ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "$CMD" 
done

PREFIX="10.10.16."
for (( i=1; i<=$NUM_AGENTS; i++))
do
        SERVER=${PREFIX}$(( $OFFSET + $i ))
	echo $SERVER
        ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "$CMD" 
done

PREFIX="10.10.32."
for (( i=1; i<=$NUM_PUBLIC_AGENTS; i++))
do
        SERVER=${PREFIX}$(( $OFFSET + $i ))
	echo $SERVER
        ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "$CMD" 
done

