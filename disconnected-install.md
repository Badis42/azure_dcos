# Build a Resource Group 

Setup to test disconnected install. 

I used the "dev" template.
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

