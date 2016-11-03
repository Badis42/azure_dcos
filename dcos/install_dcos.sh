#!/bin/bash

# Set the URL to DCOS config script
DCOS_URL=https://downloads.dcos.io/dcos/stable/dcos_generate_config.sh

# Set ADMIN_PASSWORD to "" to disable oauth Authentication; otherwise specify password for "admin" login
ADMIN_PASSWORD=""

# Set the Azure username and the name of the private PKI file for that user; the PKI file should allow access without a password
USERNAME=azureuser
PKIFILE=azureuser

if [ "$#" -ne 1 ];then
	echo "You must specify a Cluster size (mini,dev,small)"
	exit 99
fi

# mini,dev,small
CLUSTERSIZE=$1

# If installer fails and you need to rerun.
# In some cases you can just try again.
# If that doesn't work
# Delete everything from root's home except the PKI private key and the this script using the rm command.
# Stop docker instances  Run "docker ps" if nginx is running then run "docker stop <id>" and then "docker rm <id>"
# Now run the install script again.


# Set Number of Master, Agents, and PublicAgents
case "$CLUSTERSIZE" in
	mini)
                echo "mini"
                NUM_MASTERS=1
                NUM_AGENTS=3
                NUM_PUBLIC_AGENTS=1
                ;;  
        dev)
                echo "dev"
                NUM_MASTERS=1
                NUM_AGENTS=5
                NUM_PUBLIC_AGENTS=1
                ;;  
        small)
                echo "small"
                NUM_MASTERS=3
                NUM_AGENTS=7
                NUM_PUBLIC_AGENTS=3
                ;;  
        *)  
                echo "unrecognized CLUSTERSIZE"
                NUM_MASTERS=0
                NUM_AGENTS=0
                NUM_PUBLIC_AGENTS=0
                exit 2
esac

if [ ! -e $PKIFILE ]; then
	echo "This PKI file does not exist: " + $PKIFILE
	exit 3
fi

# Start Time
echo "Start Boot Setup"
st=$(date +%s)

# Create docker.repo
docker_repo="[dockerrepo]
name=Docker Repository
baseurl=https://yum.dockerproject.org/repo/main/centos/\$releasever/
enabled=1
gpgcheck=1
gpgkey=https://yum.dockerproject.org/gpg"

echo "$docker_repo" > docker.repo

# Create overlay.conf
overlay="overlay"

echo "$overlay" > overlay.conf

# Create override.conf
override="[Service]
ExecStart=
ExecStart=/usr/bin/dockerd --storage-driver=overlay"

echo "$override" > override.conf

# Create install.bat
install="#!/bin/bash

yum -y install ipset

mkdir /tmp/dcos
cd /tmp/dcos
curl -O boot/overlay.conf
curl -O boot/override.conf
curl -O boot/docker.repo
curl -O boot/dcos_install.sh

groupadd nogroup

cp /tmp/dcos/overlay.conf /etc/modules-load.d/
cp /tmp/dcos/docker.repo /etc/yum.repos.d/

mkdir /etc/systemd/system/docker.service.d
cp /tmp/dcos/override.conf /etc/systemd/system/docker.service.d/

yum -y install docker-engine

systemctl start docker
systemctl enable docker

systemctl stop dnsmasq
systemctl disable dnsmasq

sed -i -e 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
setenforce permissive

bash dcos_install.sh \$1"

echo "$install" > install.sh

# Copy files

cp overlay.conf /etc/modules-load.d/
cp docker.repo /etc/yum.repos.d/

mkdir /etc/systemd/system/docker.service.d

cp override.conf /etc/systemd/system/docker.service.d/

boot_log="boot.log"

yum install -y docker-engine > $boot_log 2>&1
systemctl start docker >> $boot_log 2>&1
systemctl enable docker >> $boot_log 2>&1
systemctl daemon-reload >> $boot_log 2>&1

setenforce permissive >> $boot_log 2>&1

curl -O --silent $DCOS_URL >> $boot_log 2>&1

dcos_cmd=$(basename $DCOS_URL)

bash $dcos_cmd --help >> $boot_log 2>&1

search=$(cat /etc/resolv.conf | grep search | cut -d ' ' -f2)
ns=$(cat /etc/resolv.conf | grep nameserver | cut -d ' ' -f2)

master_list=""
for (( i=1; i<=$NUM_MASTERS; i++))
do
        server="m$i"
	ip=$(host $server | cut -d ' ' -f4)
        echo "$server $ip" >> $boot_log
	master_list="$master_list""- "$ip$'\n'	
done

echo 'search: ' + $search >> $boot_log
echo 'nameserver: ' + $ns >> $boot_log

# create the config.yaml

oauthval="'false'"
pwlines=""
if [ ! -z $PASSWORD ]; then
	oauthval="'true'"
	pw=$(bash $dcos_cmd --hash-password $ADMIN_PASSWORD)	
	pwlines='''superuser_password_hash: $pw
superuser_username: admin'''
fi

config_yaml="---
bootstrap_url: http://boot:80
cluster_name: 'trinity'
exhibitor_storage_backend: static
ip_detect_filename: /genconf/ip-detect
oauth_enabled: $oauthval
master_discovery: static
check_time: 'false'
dns_search: $search
master_list:
"$master_list"
resolvers:
- $ns
$pwlines"

echo "$config_yaml" > genconf/config.yaml

# Create ip-detect
ip_detect="#!/usr/bin/env bash
set -o nounset -o errexit
export PATH=/usr/sbin:/usr/bin:$PATH
echo \$(ip addr show eth0 | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -1)"

echo "$ip_detect" > genconf/ip-detect

bash $dcos_cmd >> $boot_log 2>&1

# Copy files to server folder

mv docker.repo genconf/serve/
mv install.sh genconf/serve/
mv override.conf genconf/serve/
mv overlay.conf genconf/serve/

RESULT=$?
if [ $RESULT -ne 0 ]; then
	echo "Move files to genconf/serve folder failed!. Check boot.log for more details"
	exit 4
fi 

docker run -d -p 80:80 -v $PWD/genconf/serve:/usr/share/nginx/html:ro nginx >> $boot_log 2>&1

echo "Boot Setup Complete"
boot_fin=$(date +%s)
et=$(expr $boot_fin - $st)
echo "Time Elapsed (Seconds):  $et"
echo "This should take about 5 minutes or less. If it takes longer than 10 minutes then use Ctrl-C to exit this Script and review the log files (e.g. m1.log)"
echo "Installing DC/OS." 



DCOSTYPE=master
for (( i=1; i<=$NUM_MASTERS; i++))
do
        SERVER="m$i"
        ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "sudo curl -O boot/install.sh;sudo bash install.sh $DCOSTYPE" >$SERVER.log 2>$SERVER.log &
done

DCOSTYPE=slave
for (( i=1; i<=$NUM_AGENTS; i++))
do
        SERVER="a$i"
        ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "sudo curl -O boot/install.sh;sudo bash install.sh $DCOSTYPE" >$SERVER.log 2>$SERVER.log &
done

DCOSTYPE=slave_public
for (( i=1; i<=$NUM_AGENTS; i++))
do
        SERVER="p$i"
        ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "sudo curl -O boot/install.sh;sudo bash install.sh $DCOSTYPE" >$SERVER.log 2>$SERVER.log &
done

# Watch Master; when port 80 becomes active then its ready
curl --output /dev/null --head --silent http://m1:80

until [ "$?" == "0" ]; do
    printf '.'
    sleep 5
    curl --output /dev/null --head --silent http://m1:80
done

dcos_fin=$(date +%s)
et2=$(expr $dcos_fin - $boot_fin) # Number of seconds it too from boot finished until DCOS ready
et3=$(expr $et + $et2)

echo "Boot Server Installation (sec): $et"
echo "DCOS Installation (sec): $et2"
echo "Total Time (sec): $et3"
echo 
echo "DCOS is Ready"


