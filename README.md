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
<img src="../../images/azure-arm2/000.png"/><br>

## Goto Azure Portal
<img src="../../images/azure-arm2/001.png"/><br>

Click More Services and Search for Templates
<img src="../../images/azure-arm2/002.png"/><br>
Select Templates

## Select a Template (e.g. trinity_dev)

This will create 1 master, 5 agents, and 1 public agent

<img src="../../images/azure-arm2/003.png"/><br>

Click Deploy

## Enter Resource Group

Enter Name: (e.g. esri50)

## Under Parameters
- Enter Username (e.g. azureuser)
- Copy and Paste Public Key (starts with ssh-rsa).

Click OK 
<br/>
<br/>
<img src="../../images/azure-arm2/004.png"/><br>

## Click Legal terms
<img src="../../images/azure-arm2/005.png"/><br>
Click Purchase
