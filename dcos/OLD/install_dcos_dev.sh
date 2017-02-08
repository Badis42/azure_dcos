#!/bin/bash
DCOS_URL=https://downloads.dcos.io/dcos/stable/dcos_generate_config.sh
ADMIN_PASSWORD=somepassword
USERNAME=az
PKIFILE=az

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

sed -i '$ i vm.max_map_count=262144' /etc/sysctl.conf
sysctl -w vm.max_map_count=262144

bash dcos_install.sh \$1"

echo "$install" > install.sh

# Copy files

cp overlay.conf /etc/modules-load.d/
cp docker.repo /etc/yum.repos.d/

mkdir /etc/systemd/system/docker.service.d

cp override.conf /etc/systemd/system/docker.service.d/

yum install -y docker-engine
systemctl start docker
systemctl enable docker
systemctl daemon-reload

setenforce permissive

curl -O $DCOS_URL

dcos_cmd=$(basename $DCOS_URL)

bash $dcos_cmd --help

pw=$(bash $dcos_cmd --hash-password $ADMIN_PASSWORD)

search=$(cat /etc/resolv.conf | grep search | cut -d ' ' -f2)
ns=$(cat /etc/resolv.conf | grep nameserver | cut -d ' ' -f2)

m1ip=$(host m1 | cut -d ' ' -f4)

echo 'search: ' + $search
echo 'nameserver: ' + $ns
echo 'm1ip: ' + $m1ip

# create the config.yaml

config_yaml="---
bootstrap_url: http://boot:80
cluster_name: 'trinity'
exhibitor_storage_backend: static
ip_detect_filename: /genconf/ip-detect
oauth_enabled: 'false'
master_discovery: static
check_time: 'false'
dns_search: $search
master_list:
- $m1ip
resolvers:
- $ns
superuser_password_hash: $pw
superuser_username: admin"

echo "$config_yaml" > genconf/config.yaml

# Create ip-detect
ip_detect="#!/usr/bin/env bash
set -o nounset -o errexit
export PATH=/usr/sbin:/usr/bin:$PATH
echo \$(ip addr show eth0 | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -1)"

echo "$ip_detect" > genconf/ip-detect

bash $dcos_cmd

# Copy files to server folder

mv docker.repo genconf/serve/
mv install.sh genconf/serve/
mv override.conf genconf/serve/
mv overlay.conf genconf/serve/

docker run -d -p 80:80 -v $PWD/genconf/serve:/usr/share/nginx/html:ro nginx
 
DCOSTYPE=master
SERVER=m1
ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "sudo curl -O boot/install.sh;sudo bash install.sh $DCOSTYPE" >$SERVER.log 2>$SERVER.log &

DCOSTYPE=slave
SERVER=a1
ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "sudo curl -O boot/install.sh;sudo bash install.sh $DCOSTYPE" >$SERVER.log 2>$SERVER.log &
SERVER=a2
ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "sudo curl -O boot/install.sh;sudo bash install.sh $DCOSTYPE" >$SERVER.log 2>$SERVER.log &
SERVER=a3
ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "sudo curl -O boot/install.sh;sudo bash install.sh $DCOSTYPE" >$SERVER.log 2>$SERVER.log &
SERVER=a4
ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "sudo curl -O boot/install.sh;sudo bash install.sh $DCOSTYPE" >$SERVER.log 2>$SERVER.log &
SERVER=a5
ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "sudo curl -O boot/install.sh;sudo bash install.sh $DCOSTYPE" >$SERVER.log 2>$SERVER.log &

DCOSTYPE=slave_public
SERVER=p1
ssh -t -t -o "StrictHostKeyChecking no" -i $PKIFILE $USERNAME@$SERVER "sudo curl -O boot/install.sh;sudo bash install.sh $DCOSTYPE" >$SERVER.log 2>$SERVER.log &

