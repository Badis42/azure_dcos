# Create DC/OS Cluster From Template 

The procedure assumes you already <a href="create-templates.md">Created the Template</a>

## You'll need a SSH Key Pair
If you don't have one; here is the process to create one.

This can be done from command line on Linux, Mac, or MobaXterm (Windows).
<pre>
$ ssh-keygen
</pre>
- Change the path to the key (e.g. /home/david/azureuser)
- Leave passphrase blank.

Creates two files (azureuser and azureuser.pub)
<br/>
<br/>
<img src="../../images/readme/000.png"/><br>

## Goto Azure Portal
<img src="../../images/readme/001.png"/><br>

Click More Services and Search for Templates
<img src="../../images/readme/002.png"/><br>
Select Templates

## Select a Template (e.g. trinity_dev)

This will create 1 master, 5 agents, and 1 public agent

<img src="../../images/readme/003.png"/><br>

Click Deploy

## Enter Resource Group

Enter Name: (e.g. esri50)

## Under Parameters
- Enter Username (e.g. azureuser)
- Copy and Paste Public Key (starts with ssh-rsa).

Click OK 
<br/>
<br/>
<img src="../../images/readme/004.png"/><br>

## Click Legal terms
<img src="../../images/readme/005.png"/><br>
Click Purchase

## Click Create
You can see Deployment started under messages.
<img src="../../images/readme/006.png"/><br>


## This will take a about 5 – 10 minutes
<img src="../../images/readme/007.png"/><br>

## From Portal Navigate to the Public IP for the boot server
<img src="../../images/readme/008.png"/><br>


## Copy install_dcos.sh and Private Key to Boot
The <a href="../../azure/dcos/install_dcos.sh"> install_dcos.sh </a> is a Bash Script from GitHub.

From your local workstation.

<pre>
$ scp -i azureuser esritrinity-holistic/azure/dcos/install_dcos.sh azureuser@40.78.62.181:.

$ scp -i azureuser azureuser azureuser@40.78.62.181:.

$ ssh -i azureuser  azureuser@40.78.62.181
</pre>

You are not logged into boot server as azureuser
<pre>
$ sudo su -
</pre>

You are now root on the boot server.

<pre>
# cp /home/azureuser/azureuser .
# chmod 600 azureuser
# cp /home/azureuser/install_dcos.sh
</pre>

The script by default 
- Installs latest Stable version of DC/OS
- Assumes Azure username is “azureuser”
- Assumes the PKI private file is also named “azureuser”
- Configure DC/OS with Oauth Authentication disabled

If you want to do something different change the parameters at the top of the script.

Run the script specifying the template you used (e.g. dev)
<pre>
# bash intall_dcos.sh dev
</pre>

It takes about 2-3 minutes for the Boot Setup to complete.

The DC/OS installs in about 4-5 minutes.

The last line output is “DCOS is Ready”

Look up one of the Master Public IP in Azure Portal
<img src="../../images/readme/009.png"/><br>

From your workstation create a Tunnel to DC/OS.

<pre>
$ ssh -i azureuser -L 9001:leader.mesos:80 azureuser@40.78.59.166
</pre>

From a browser connect to DCOS (http://localhost:9001)
<img src="../../images/readme/010.png"/><br>

# Marathon and Mesos are also available
<img src="../../images/readme/011.png"/><br>

# Troubleshooting
If something goes wrong review the log files in the installation folder.

Often you can correct the problem and rerun the install_dcos.sh script.

Sometimes you may need to remove (rm) all the files root's home directory on the boot server.  You can delete everything except your private key and the install_dcos.sh script. 

You also may need to stop the nginx Docker container.
<pre>
# docker ps 
(id)
# docker stop (id)
# docker rm (id)
</pre>
