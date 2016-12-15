# Install DCOS on Disconnected Servers (no internet)

Install DCOS on Servers without Internet connection. Instructions are for setting up Azure cluster as a test envrionment.

Created a using "Dev" Template.

<pre>
Boot Server (boot)
Masters (m1)
Agents (a1, a2, a3, a4, a5)
Public Agents (p1)
</pre>

Move files up.

<pre>
$ scp -i azureuser azureuser azureuser@23.99.111.111:.

$ ssh -i azureuser azureuser@23.99.111.111
</pre>

The azureuser is a sudoer.

NOTE: Assume you have Red Hat private repo available with base install packages.

Install some required packages on each server.

<pre>
$ sudo yum install -y ipset unzip libtool-ltdl libseccomp policycoreutils-python
</pre>

Disable outbound access from master.  In Azure this can be done via the Network Security Groups master, agent, and public_agent.
Create an outbound security rule. Priority 100; Port Range * and Action Deny.
Create an outbound security rule, Priority 200; allow CIDR 172.17.0.0/16; port range *, Action Allow


NOTE: I left the boot Network Security Group alone so I could still download files to the server if needed.

<pre>
<boot># curl -O https://yum.dockerproject.org/repo/main/centos/7/Packages/docker-engine-selinux-1.12.4-1.el7.centos.noarch.rpm

<boot># curl -O https://yum.dockerproject.org/repo/main/centos/7/Packages/docker-engine-1.12.4-1.el7.centos.x86_64.rpm

<boot># curl -k -O https://downloads.dcos.io/dcos/stable/dcos_generate_config.sh
</pre>

NOTE: Uploading to azure from my home is limited by the 7Mbps upload of my ISP.  So uploading dcos_generate_config.sh (726MB) would takes about 15 minutes. 

Uploaded the docker image for nginx. 

NOTE: Created nginx.tar.gz file on my home computer using docker save.  

<pre>
$ scp -i azureuser nginx.tar.gz  azureuser@23.99.111.111:.
</pre>

<pre>
# docker load < nginx.tar.gz
</pre>

NOTE: You could block boot from Internet using Network Security Groups Now.

Run script <a href="../master/dcos/install_dcos_disconnected.sh"> dcos_install_disconnected.sh </a>.

<pre>
$ scp -i azureuser dcos_install_disconnected.sh  azureuser@23.99.111.111:.

$ sudo su -

# cp /home/azureuser/azureuser .
# cp /home/azureuser/dcos_install_disconnected.sh .

# bash dcos_install_disconnected.sh dev

</pre>


Used these instructions https://docs.mesosphere.com/1.8/administration/installing/deploying-a-local-dcos-universe/ to create local-universe.tar.gz.

Note: Default only includes four packages. Not the ones we need.

I used: --include="marathon-lb,kafka,chronos"

Compile took a few minutes.
<pre>
$ scp -i azureuser local-universe.tar.gz azureuser@23.99.82.81:.
</pre>

Took a few minutes to move.  It was 527MB.

<pre>
$ ssh -i azureuser azureuser@23.99.82.81
$ scp -i azureuser local-universe.tar.gz m1:.

$ ssh -i azureuser m1
$ sudo su - 

# docker load -i /home/azureuser/local-universe.tar.gz


# vi /etc/systemd/system/dcos-local-universe-http.service
[Unit]
Description=DCOS: Serve the (http) local universe
After=docker.service

[Service]
Restart=always
StartLimitInterval=0
RestartSec=15
TimeoutStartSec=120
TimeoutStopSec=15
ExecStart=/usr/bin/docker run --rm --name %n -p 8082:80 mesosphere/universe nginx -g "daemon off;"
:wq

# vi /etc/systemd/system/dcos-local-universe-registry.service
[Unit]
Description=DCOS: Serve the (http) local universe
After=docker.service

[Service]
Restart=always
StartLimitInterval=0
RestartSec=15
TimeoutStartSec=120
TimeoutStopSec=15
ExecStart=/usr/bin/docker run --rm --name %n -p 5000:5000 -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key mesosphere/universe registry serve /etc/docker/registry/config.yml
:wq


# systemctl daemon-reload


# systemctl start dcos-local-universe-http
# systemctl start dcos-local-universe-registry


# systemctl enable dcos-local-universe-http
# systemctl enable dcos-local-universe-registry
</pre>


### From WebUI

Delete the Default Repositry

<pre>
Universe
https://universe.mesosphere.com/repo
0
</pre>

<pre>
Local Universe
http://master.mesos:8082/repo
0

</pre>
On each private and public agent

<pre>
# mkdir -p /etc/docker/certs.d/master.mesos:5000
# curl -o /etc/docker/certs.d/master.mesos:5000/ca.crt http://master.mesos:8082/certs/domain.crt
# systemctl restart docker
</pre>



## Setup Private Docker Repo

http://davidssysadminnotes.blogspot.com/2016/04/create-private-docker-registry.html

You'll need to modify override.conf on all servers
<pre>
# vi /etc/systemd/system/docker.service.d/override.conf
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd --storage-driver=overlay --insecure-registry boot:5000

Append --insecure-registry option.

# systemctl daemon-reload
# systemctl restart docker

For offline you'd need to save the images; burn to DVD; then load the images.

For testing I just downloaded directly onto "boot" server.

# docker login
# docker pull esritrinity/realtime-taskmanager:0.8.6
# docker tag esritrinity/realtime-taskmanager:0.8.6 boot:5000/esritrinity/realtime-taskmanager:0.8.6
# docker push boot:5000/realtime-taskmanager:0.8.6 

# docker pull esritrinity/realtime-monitoring:0.8.6
# docker tag esritrinity/realtime-monitoring:0.8.6 boot:5000/esritrinity/realtime-monitoring:0.8.6
# docker push boot:5000/realtime-monitoring:0.8.6 
</pre>



