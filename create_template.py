import json
import string
import os
import random
import time

# Input Parameters
VERSION="1.0.0.0"

NUM_MASTERS=1
NUM_AGENTS=3
NUM_PUBLIC_AGENTS=1

MASTER_VM_SIZE="Standard_DS4_v2"
AGENT_VM_SIZE="Standard_DS11_v2"

LOCATION="westus"

USER = "azureuser"    
PUBLIC_KEY_DATA = "ssh-rsa AAAAB3..."


# IMAGE_REFERENCE
IMAGE_REFERENCE = {}
IMAGE_REFERENCE["publisher"]="OpenLogic"
IMAGE_REFERENCE["offer"]="CentOS"
IMAGE_REFERENCE["sku"]="7.2"
IMAGE_REFERENCE["version"]="latest"

# PUBLIC_KEY
PUBLIC_KEY = {}
PUBLIC_KEY["path"]="/home/" + USER + "/.ssh/authorized_keys"
PUBLIC_KEY["keyData"]="[parameters('publicKey')]"


def createVM(name, size):

    resource = {}

    dtg = time.strftime("%Y%m%d%H%M%S")
    
    resource["comments"] = name 
    resource["type"] = "Microsoft.Compute/virtualMachines"
    resource["name"] = "[concat(parameters('resourceGroup'),'_', '" + name + "')]"
    resource["apiVersion"] = "2015-06-15"
    resource["location"] = LOCATION

    resource["properties"] = {}

    resource["properties"]["hardwareProfile"] = {}
    resource["properties"]["hardwareProfile"]["vmsize"] = size

    resource["properties"]["storageProfile"] = {}
    resource["properties"]["storageProfile"]["imageReference"] = IMAGE_REFERENCE
    resource["properties"]["storageProfile"]["osDisk"] = {}
    resource["properties"]["storageProfile"]["osDisk"]["name"] = name
    resource["properties"]["storageProfile"]["osDisk"]["createOption"] = "FromImage"
    resource["properties"]["storageProfile"]["osDisk"]["vhd"] = {}
    resource["properties"]["storageProfile"]["osDisk"]["vhd"]["uri"] = "[concat('https', '://', parameters('resourceGroup'), '.blob.core.windows.net', concat('/vhds/', '" + name + "', '" + dtg + ".vhd'))]"
    resource["properties"]["storageProfile"]["osDisk"]["caching"] = "ReadWrite"
    resource["properties"]["storageProfile"]["dataDisks"] = []

    resource["properties"]["osProfile"] = {}
    resource["properties"]["osProfile"]["computerName"] = name
    resource["properties"]["osProfile"]["adminUsername"] = "azureuser"

    resource["properties"]["osProfile"]["linuxConfiguration"] = {}
    resource["properties"]["osProfile"]["linuxConfiguration"]["disablePasswordAuthentication"] = True
    resource["properties"]["osProfile"]["linuxConfiguration"]["ssh"] = {}
    resource["properties"]["osProfile"]["linuxConfiguration"]["ssh"]["publicKeys"] = []
    resource["properties"]["osProfile"]["linuxConfiguration"]["ssh"]["publicKeys"].append(PUBLIC_KEY)

    resource["properties"]["networkProfile"] = {}
    resource["properties"]["networkProfile"]["networkInterfaces"] = []

    network_id = {}
    network_id["id"] = "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('resourceGroup'), '_', '" + name + "'))]"
    resource["properties"]["networkProfile"]["networkInterfaces"].append(network_id)

    resource["resources"] = []
    
    resource["dependsOn"] = []
    resource["dependsOn"].append("[resourceId('Microsoft.Storage/storageAccounts', parameters('resourceGroup'))]")
    resource["dependsOn"].append("[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('resourceGroup'),'_','" + name + "'))]")
    
    return resource


def createNetworkInterface(name,nsg):

    resource = {}
    
    resource["comments"] = name 
    resource["type"] = "Microsoft.Network/networkInterfaces"
    resource["name"] = "[concat(parameters('resourceGroup'), '_', '" + name + "')]"
    resource["apiVersion"] = "2016-03-30"
    resource["location"] = LOCATION

    resource["properties"] = {}

    resource["properties"]["ipConfigurations"] = []

    ipconfig = {}

    ipconfig["name"] = "ipconfig1"
    ipconfig["properties"] = {}
    ipconfig["properties"]["privateIPAllocatedMethod"] = "Dynamic"

    if nsg in ["master","public_agent"]:    
        ipconfig["properties"]["publicIPAddress"] = {}
        ipconfig["properties"]["publicIPAddress"]["id"] = "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('resourceGroup'),'_','" + name + "'))]"
    ipconfig["properties"]["subnet"] = {}
    ipconfig["properties"]["subnet"]["id"] = "[concat(resourceId('Microsoft.Network/virtualNetworks', parameters('resourceGroup')), '/subnets/" + nsg + "')]"

    resource["properties"]["ipConfigurations"].append(ipconfig)

    resource["properties"]["dnsSettings"] = {}
    resource["properties"]["dnsSettings"]["dnsServers"] = []
    resource["properties"]["enabledIPForwarding"] = False
    resource["properties"]["networkSecurityGroup"] = {}
    resource["properties"]["networkSecurityGroup"]["id"] = "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resourceGroup'), '_', '" + nsg + "'))]"
    resource["resources"] = []
    
    resource["dependsOn"] = []
    if nsg in ["master","public_agent"]:    
        resource["dependsOn"].append("[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('resourceGroup'),'_','" + name + "'))]")
    resource["dependsOn"].append("[resourceId('Microsoft.Network/virtualNetworks', parameters('resourceGroup'))]")
    resource["dependsOn"].append("[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resourceGroup'),'_','" + nsg + "'))]")
    
    return resource    


def createNSG(nsg):

    resource = {}
    
    resource["comments"] = nsg 
    resource["type"] = "Microsoft.Network/networkSecurityGroups"
    resource["name"] = "[concat(parameters('resourceGroup'),'_', '" + nsg + "')]"
    resource["apiVersion"] = "2016-03-30"
    resource["location"] = LOCATION

    resource["properties"] = {}

    resource["properties"]["securityRules"] = []

    rule = {}

    rule["name"] = "default-allow-ssh"
    rule["properties"] = {}
    rule["properties"]["protocol"] = "TCP"
    rule["properties"]["sourcePortRange"] = "*"
    rule["properties"]["destinationPortRange"] = "22"
    rule["properties"]["sourceAddressPrefix"] = "*"
    rule["properties"]["destinationAddressPrefix"] = "*"
    rule["properties"]["access"] = "Allow"
    rule["properties"]["priority"] = 1000
    rule["properties"]["direction"] = "Inbound"
    
    resource["properties"]["securityRules"].append(rule)
    
    resource["resources"] = []
    
    resource["dependsOn"] = []

    return resource    

def createPublicIP(name):

    resource = {}
    
    resource["comments"] = name 
    resource["type"] = "Microsoft.Network/publicIPAddresses"
    resource["name"] = "[concat(parameters('resourceGroup'),'_', '" + name + "')]"
    resource["apiVersion"] = "2016-03-30"
    resource["location"] = LOCATION

    resource["properties"] = {}

    resource["properties"]["publicAllocationMethod"] = "Dynamic"
    resource["properties"]["idelTimeoutInMinutes"] = 4
    
    resource["resources"] = []
    
    resource["dependsOn"] = []

    return resource


def createVirutalNetworks():

    resource = {}
    
    resource["comments"] = "[parameters('resourceGroup')]"
    resource["type"] = "Microsoft.Network/virtualNetworks"
    resource["name"] = "[parameters('resourceGroup')]"
    resource["apiVersion"] = "2016-03-30"
    resource["location"] = LOCATION

    resource["properties"] = {}

    resource["properties"]["addressSpace"] = {}
    resource["properties"]["addressSpace"]["addressPrefixes"] = []
    resource["properties"]["addressSpace"]["addressPrefixes"].append("172.17.0.0/16")
    resource["properties"]["subnets"] = []

    subnet = {}
    subnet["name"] = "default"
    subnet["properties"] = {}
    subnet["properties"]["addressPrefix"]="172.17.0.0/24"
    resource["properties"]["subnets"].append(subnet)

    subnet = {}
    subnet["name"] = "master"
    subnet["properties"] = {}
    subnet["properties"]["addressPrefix"]="172.17.1.0/24"
    resource["properties"]["subnets"].append(subnet)

    subnet = {}
    subnet["name"] = "agent"
    subnet["properties"] = {}
    subnet["properties"]["addressPrefix"]="172.17.2.0/24"
    resource["properties"]["subnets"].append(subnet)
    
    subnet = {}
    subnet["name"] = "public_agent"
    subnet["properties"] = {}
    subnet["properties"]["addressPrefix"]="172.17.3.0/24"
    resource["properties"]["subnets"].append(subnet)
        
    resource["resources"] = []
    
    resource["dependsOn"] = []

    return resource


def createStorageAccounts():

    resource = {}
    
    resource["comments"] = "[parameters('resourceGroup')]"
    resource["type"] = "Microsoft.Storage/storageAccounts"
    resource["sku"] = {}
    resource["sku"]["name"] = "Premium_LRS"
    resource["sku"]["tier"] = "Premium"
    resource["kind"]= "Storage"
    resource["name"] = "[parameters('resourceGroup')]"
    resource["apiVersion"] = "2016-01-01"
    resource["location"] = LOCATION
    resource["tags"] = {}
    resource["properties"] = {}
    resource["resources"] = []
    resource["dependsOn"] = []

    return resource




if __name__ == '__main__':

    

    # Create a random password
    length = 32
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))
    PASSWD = ''.join(random.choice(chars) for i in range(length))
    
    data = {}

    data["$schema"] = "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#"

    data["contentVersion"] = VERSION

    parameters = {}

    paramvals = {}
    paramvals['defaultValue'] = PASSWD
    paramvals['type'] = "String"
    parameters["vmAdminPassword"] = paramvals
    
    paramvals = {}
    paramvals['defaultValue'] = None
    paramvals['type'] = "String"
    parameters["resourceGroup"] = paramvals

    paramvals = {}
    paramvals['defaultValue'] = PUBLIC_KEY_DATA
    paramvals['type'] = "String"
    parameters["publicKey"] = paramvals
    
    data['parameters'] = parameters

    resources = []


    # Create Virtual Machines
    resources.append(createVM("boot", MASTER_VM_SIZE))
    resources.append(createNetworkInterface("boot","master"))
    resources.append(createPublicIP("boot"))

    
    i = 0
    while i < NUM_MASTERS:
        i += 1
        name = "m" + str(i)
        resources.append(createVM(name, MASTER_VM_SIZE))    
        resources.append(createNetworkInterface(name,"master"))
        resources.append(createPublicIP(name))

    i = 0
    while i < NUM_AGENTS:
        i += 1
        name = "a" + str(i)
        resources.append(createVM(name, AGENT_VM_SIZE))    
        resources.append(createNetworkInterface(name,"agent"))

    i = 0
    while i < NUM_PUBLIC_AGENTS:
        i += 1
        name = "p" + str(i)
        resources.append(createVM(name, AGENT_VM_SIZE))    
        resources.append(createNetworkInterface(name,"public_agent"))
        resources.append(createPublicIP(name))


    # Create Network Security Groups
    resources.append(createNSG("master"))
    resources.append(createNSG("agent"))
    resources.append(createNSG("public_agent"))
    

    # Create VirtualNetwork
    resources.append(createVirutalNetworks())

    # Create Storage Account
    resources.append(createStorageAccounts())

    data['resources']  = resources

    #pjson_data = json.dumps(data, indent=4,sort_keys=True)
    pjson_data = json.dumps(data, indent=4)


    fout = open("temp.json","w")
    fout.write(pjson_data)
    fout.close()
    
    #print(pjson_data)

       
You need to set parameters at top of script

 

NUM_MASTERS=1
NUM_AGENTS=3
NUM_PUBLIC_AGENTS=1

MASTER_VM_SIZE="Standard_DS4_v2"
AGENT_VM_SIZE="Standard_DS11_v2"

LOCATION="westus"

USER = "azureuser"    
PUBLIC_KEY_DATA = "ssh-rsa <with your public key>" 

 

 

  

The results json is saved to a file name temp.json.

Copy and paste this file's contents in a Azure Template. 

Posted by David Jennings at 10:54 AM No comments: Email ThisBlogThis!Share to TwitterShare to FacebookShare to Pinterest
Thursday, October 13, 2016
Advanced Install DCOS 1.8 on Azure using Azure Template

Create Resource Group using Template

From Azure Portal on far left at bottom click "More Services>"; search for "Templates"

For example "smallcluster

The template will create a boot server, three masters, three agents, and three public agents.
- Set VMADMINPASSWORD (e.g. long complicated)
- Set RESOURCEGROUP (e.g. esri64)
- Set PUBLICKEY (This is the public part of your pki key starts with ssh-rsa)

Legal terms; click Purchase

Click create.

After a few minutes servers will be created and ready for installation.

Configure Boot

Using the public IP for boot.  Azure Portal Element (e.g.  esri64_boot) Public IP Address.

NOTE: You can remove a passphrase from a private key using this command:

openssl rsa -in privkey_with_passphrase.key -out privkey_without_passphrase.key


Copy the key up to the boot server
$ scp -i azureuser2 azureuser2 azureuser@13.89.9.115:.

$ ssh -i azureuser2 azureuser@13.89.9.115

$ sudo su -

# cp /home/azureuser/azureuser2  /root/
# chown 600 /root/azureuser2

#  vim install_boot.sh

#!/bin/bash
DCOS_URL=https://downloads.dcos.io/dcos/stable/dcos_generate_config.sh
ADMIN_PASSWORD=somepassword

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
 
ssh -t -o "StrictHostKeyChecking no" -i azureuser2 azureuser@m1 "sudo curl -O boot/install.sh;sudo bash install.sh master"

ssh -t -o "StrictHostKeyChecking no" -i azureuser2 azureuser@a1 "sudo curl -O boot/install.sh;sudo bash install.sh slave"
ssh -t -o "StrictHostKeyChecking no" -i azureuser2 azureuser@a2 "sudo curl -O boot/install.sh;sudo bash install.sh slave"
ssh -t -o "StrictHostKeyChecking no" -i azureuser2 azureuser@a3 "sudo curl -O boot/install.sh;sudo bash install.sh slave"

ssh -t -o "StrictHostKeyChecking no" -i azureuser2 azureuser@p1 "sudo curl -O boot/install.sh;sudo bash install.sh slave_public"   


Edit

    Set the DCOS_URL and ADMIN_PASSWORD at the top of the script.
    Script assumes 1 master; you'll need to adjust as needed for additional masters
    Edit config.yaml as needed
        Example has oauth disabled (you'll need to enable for Enterprise Edition 
    Add additional ssh lines at bottom.  One for each master, agent, and public agent.


Run the script.

# bash install_boot.sh

This will take about two minutes per server. 

Access the Cluster

$ ssh -i azure2 -L 9001:leader.mesos:80 azureuser@<IP of a Master>

NOTE: For oauth enabled you'll need to use 443 and https.

From Browser
DCOS:  http://localhost:9001
Marathon:  http://localhost:9001/marathon
Mesos: http://localhost:9001/mesos
Exhibitor: http://localhost:9001/exhibitor


Posted by David Jennings at 1:17 PM No comments: Email ThisBlogThis!Share to TwitterShare to FacebookShare to Pinterest
Create Custom Azure Template
Create Resource Group

I created one named esri56

Create boot VM

DS2_V2; 2 Cores, 7GB RAM, 14GB SSD will work

CentOS-based 7.2 OpenLogic

Created esri56-vnet
- Storage account: New (e.g.  esri56disks)
- Mine had address space 172.17.0.0/16
- Network Security Group: esri56-masters-nsg (created one and use for masters)
- Default subnet 172.17.0.0/24

Add Additional Subnets for public and private agents

Edit the Virtual Network and add subnet
private-agents 172.17.1.0/24
public-agents 172.17.2.0/24

Create Master VM's

DS11_V2; 2 Cores, 14GB RAM, 28GB SSD

Names: m1, m2, m3
Network Security Group: esri56-masters-nsg (created one and use for rest of masters)
Default Subnet

Create Private Agent VM's 

3 - DS4_v2; 8 Cores, 28GB RAM

Names: a1, a2, a3
Subnet: private-agents
Public IP: None
Network Security Group: esri56-private-nsg (Create one and use for rest of private agents)

Create Public Agent VM's
3 - DS4_v2; 8 Cores, 28GB RAM

Names: p1, p2, p3
Subnet: public-agents
Network Security Group: esri56-public-nsg (Create one and use for rest of private agents)

Save Template
From Azure portal select the Resource Group then select "Automation Script".  Click "Add to Library".  Give it a name (e.g. esri_resource_group) and description.

The template has many hard-coded parameters for the name (e.g. esri56).  Using the template you can quickly delete and rebuild the resource group; however, you cannot create another instance easily.


Edit the Template

I customized the template making it more generic.  Now it can be used to create new instances.

{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "vmAdminPassword": {
            "defaultValue": null,
            "type": "SecureString"
        },
        "virtualMachines_a1_name": {
            "defaultValue": "a1",
            "type": "String"
        },
        "virtualMachines_a2_name": {
            "defaultValue": "a2",
            "type": "String"
        },
        "virtualMachines_a3_name": {
            "defaultValue": "a3",
            "type": "String"
        },
        "virtualMachines_boot_name": {
            "defaultValue": "boot",
            "type": "String"
        },
        "virtualMachines_m1_name": {
            "defaultValue": "m1",
            "type": "String"
        },
        "virtualMachines_m2_name": {
            "defaultValue": "m2",
            "type": "String"
        },
        "virtualMachines_m3_name": {
            "defaultValue": "m3",
            "type": "String"
        },
        "virtualMachines_p1_name": {
            "defaultValue": "p1",
            "type": "String"
        },
        "virtualMachines_p2_name": {
            "defaultValue": "p2",
            "type": "String"
        },
        "virtualMachines_p3_name": {
            "defaultValue": "p3",
            "type": "String"
        },
        "networkSecurityGroups_agents_nsg_name": {
            "defaultValue": "agents-nsg",
            "type": "String"
        },
        "networkSecurityGroups_agents_public_nsg_name": {
            "defaultValue": "agents-public-nsg",
            "type": "String"
        },
        "networkSecurityGroups_masters_nsg_name": {
            "defaultValue": "masters-nsg",
            "type": "String"
        },
        "resource_name": {
            "defaultValue": "esri56",
            "type": "String"
        }
    },
    "variables": {},
    "resources": [
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Compute/virtualMachines/a1'.",
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[parameters('virtualMachines_a1_name')]",
            "apiVersion": "2015-06-15",
            "location": "westus",
            "properties": {
                "hardwareProfile": {
                    "vmSize": "Standard_DS4_v2"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "OpenLogic",
                        "offer": "CentOS",
                        "sku": "7.2",
                        "version": "latest"
                    },
                    "osDisk": {
                        "name": "[parameters('virtualMachines_a1_name')]",
                        "createOption": "FromImage",
                        "vhd": {
                            "uri": "[concat('https', '://', parameters('resource_name'), '.blob.core.windows.net', concat('/vhds/', parameters('virtualMachines_a1_name'),'2016912113844.vhd'))]"
                        },
                        "caching": "ReadWrite"
                    },
                    "dataDisks": []
                },
                "osProfile": {
                    "computerName": "[parameters('virtualMachines_a1_name')]",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": true,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCyUNoNpGWsREQqL9YUfJyyNHueU1RbfHJNzrDZ74qag4DS2xUsLEufU3XfP6WdDcEooHv3Z6ul5jywhpo9qENxKyj3TpREeVLpMXXUtsu0ZK7NNbNWAdgq9iYSGecIulLa8VjOXTGPIX9YYk88ilcC4B0OoRwKmWNjamDSokDIYnAgz/E/PdAxjE0bR1bWznBUaxVM8KGc8vU1pKJMj3Epg+gRAgiTZTo3tG8sTUU7PkSNNZ1FIFIsLgBfV/d8UQgq2DSrh4iwluIIjKaedlr4GYlo7V7BhS7B7SnaG5InGoB1xlHNANAakyn9N2o41poiEAvMsW2PrBzZZv2QMoyb"
                                }
                            ]
                        }
                    },
                    "secrets": [],
                    "adminPassword": "[parameters('vmAdminPassword')]"
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_a1_name'), parameters('resource_name')))]"
                        }
                    ]
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Storage/storageAccounts', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_a1_name'), parameters('resource_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Compute/virtualMachines/a2'.",
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[parameters('virtualMachines_a2_name')]",
            "apiVersion": "2015-06-15",
            "location": "westus",
            "properties": {
                "hardwareProfile": {
                    "vmSize": "Standard_DS4_v2"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "OpenLogic",
                        "offer": "CentOS",
                        "sku": "7.2",
                        "version": "latest"
                    },
                    "osDisk": {
                        "name": "[parameters('virtualMachines_a2_name')]",
                        "createOption": "FromImage",
                        "vhd": {
                            "uri": "[concat('https', '://', parameters('resource_name'), '.blob.core.windows.net', concat('/vhds/', parameters('virtualMachines_a2_name'),'2016912114248.vhd'))]"
                        },
                        "caching": "ReadWrite"
                    },
                    "dataDisks": []
                },
                "osProfile": {
                    "computerName": "[parameters('virtualMachines_a2_name')]",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": true,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCyUNoNpGWsREQqL9YUfJyyNHueU1RbfHJNzrDZ74qag4DS2xUsLEufU3XfP6WdDcEooHv3Z6ul5jywhpo9qENxKyj3TpREeVLpMXXUtsu0ZK7NNbNWAdgq9iYSGecIulLa8VjOXTGPIX9YYk88ilcC4B0OoRwKmWNjamDSokDIYnAgz/E/PdAxjE0bR1bWznBUaxVM8KGc8vU1pKJMj3Epg+gRAgiTZTo3tG8sTUU7PkSNNZ1FIFIsLgBfV/d8UQgq2DSrh4iwluIIjKaedlr4GYlo7V7BhS7B7SnaG5InGoB1xlHNANAakyn9N2o41poiEAvMsW2PrBzZZv2QMoyb"
                                }
                            ]
                        }
                    },
                    "secrets": [],
                    "adminPassword": "[parameters('vmAdminPassword')]"
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_a2_name'), parameters('resource_name')))]"
                        }
                    ]
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Storage/storageAccounts', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_a2_name'), parameters('resource_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Compute/virtualMachines/a3'.",
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[parameters('virtualMachines_a3_name')]",
            "apiVersion": "2015-06-15",
            "location": "westus",
            "properties": {
                "hardwareProfile": {
                    "vmSize": "Standard_DS4_v2"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "OpenLogic",
                        "offer": "CentOS",
                        "sku": "7.2",
                        "version": "latest"
                    },
                    "osDisk": {
                        "name": "[parameters('virtualMachines_a3_name')]",
                        "createOption": "FromImage",
                        "vhd": {
                            "uri": "[concat('https', '://', parameters('resource_name'), '.blob.core.windows.net', concat('/vhds/', parameters('virtualMachines_a3_name'),'2016912114911.vhd'))]"
                        },
                        "caching": "ReadWrite"
                    },
                    "dataDisks": []
                },
                "osProfile": {
                    "computerName": "[parameters('virtualMachines_a3_name')]",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": true,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCyUNoNpGWsREQqL9YUfJyyNHueU1RbfHJNzrDZ74qag4DS2xUsLEufU3XfP6WdDcEooHv3Z6ul5jywhpo9qENxKyj3TpREeVLpMXXUtsu0ZK7NNbNWAdgq9iYSGecIulLa8VjOXTGPIX9YYk88ilcC4B0OoRwKmWNjamDSokDIYnAgz/E/PdAxjE0bR1bWznBUaxVM8KGc8vU1pKJMj3Epg+gRAgiTZTo3tG8sTUU7PkSNNZ1FIFIsLgBfV/d8UQgq2DSrh4iwluIIjKaedlr4GYlo7V7BhS7B7SnaG5InGoB1xlHNANAakyn9N2o41poiEAvMsW2PrBzZZv2QMoyb"
                                }
                            ]
                        }
                    },
                    "secrets": [],
                    "adminPassword": "[parameters('vmAdminPassword')]"
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_a3_name'), parameters('resource_name')))]"
                        }
                    ]
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Storage/storageAccounts', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_a3_name'), parameters('resource_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Compute/virtualMachines/boot'.",
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[parameters('virtualMachines_boot_name')]",
            "apiVersion": "2015-06-15",
            "location": "westus",
            "properties": {
                "hardwareProfile": {
                    "vmSize": "Standard_DS2_v2"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "OpenLogic",
                        "offer": "CentOS",
                        "sku": "7.2",
                        "version": "latest"
                    },
                    "osDisk": {
                        "name": "[parameters('virtualMachines_boot_name')]",
                        "createOption": "FromImage",
                        "vhd": {
                            "uri": "[concat('https', '://', parameters('resource_name'), '.blob.core.windows.net', concat('/vhds/', parameters('virtualMachines_boot_name'),'201691282633.vhd'))]"
                        },
                        "caching": "ReadWrite"
                    },
                    "dataDisks": []
                },
                "osProfile": {
                    "computerName": "[parameters('virtualMachines_boot_name')]",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": true,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCyUNoNpGWsREQqL9YUfJyyNHueU1RbfHJNzrDZ74qag4DS2xUsLEufU3XfP6WdDcEooHv3Z6ul5jywhpo9qENxKyj3TpREeVLpMXXUtsu0ZK7NNbNWAdgq9iYSGecIulLa8VjOXTGPIX9YYk88ilcC4B0OoRwKmWNjamDSokDIYnAgz/E/PdAxjE0bR1bWznBUaxVM8KGc8vU1pKJMj3Epg+gRAgiTZTo3tG8sTUU7PkSNNZ1FIFIsLgBfV/d8UQgq2DSrh4iwluIIjKaedlr4GYlo7V7BhS7B7SnaG5InGoB1xlHNANAakyn9N2o41poiEAvMsW2PrBzZZv2QMoyb"
                                }
                            ]
                        }
                    },
                    "secrets": [],
                    "adminPassword": "[parameters('vmAdminPassword')]"
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_boot_name'), parameters('resource_name')))]"
                        }
                    ]
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Storage/storageAccounts', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_boot_name'), parameters('resource_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Compute/virtualMachines/m1'.",
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[parameters('virtualMachines_m1_name')]",
            "apiVersion": "2015-06-15",
            "location": "westus",
            "properties": {
                "hardwareProfile": {
                    "vmSize": "Standard_DS11_v2"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "OpenLogic",
                        "offer": "CentOS",
                        "sku": "7.2",
                        "version": "latest"
                    },
                    "osDisk": {
                        "name": "[parameters('virtualMachines_m1_name')]",
                        "createOption": "FromImage",
                        "vhd": {
                            "uri": "[concat('https', '://', parameters('resource_name'), '.blob.core.windows.net', concat('/vhds/', parameters('virtualMachines_m1_name'),'2016912112740.vhd'))]"
                        },
                        "caching": "ReadWrite"
                    },
                    "dataDisks": []
                },
                "osProfile": {
                    "computerName": "[parameters('virtualMachines_m1_name')]",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": true,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCyUNoNpGWsREQqL9YUfJyyNHueU1RbfHJNzrDZ74qag4DS2xUsLEufU3XfP6WdDcEooHv3Z6ul5jywhpo9qENxKyj3TpREeVLpMXXUtsu0ZK7NNbNWAdgq9iYSGecIulLa8VjOXTGPIX9YYk88ilcC4B0OoRwKmWNjamDSokDIYnAgz/E/PdAxjE0bR1bWznBUaxVM8KGc8vU1pKJMj3Epg+gRAgiTZTo3tG8sTUU7PkSNNZ1FIFIsLgBfV/d8UQgq2DSrh4iwluIIjKaedlr4GYlo7V7BhS7B7SnaG5InGoB1xlHNANAakyn9N2o41poiEAvMsW2PrBzZZv2QMoyb"
                                }
                            ]
                        }
                    },
                    "secrets": [],
                    "adminPassword": "[parameters('vmAdminPassword')]"
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_m1_name'), parameters('resource_name')))]"
                        }
                    ]
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Storage/storageAccounts', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_m1_name'), parameters('resource_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Compute/virtualMachines/m2'.",
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[parameters('virtualMachines_m2_name')]",
            "apiVersion": "2015-06-15",
            "location": "westus",
            "properties": {
                "hardwareProfile": {
                    "vmSize": "Standard_DS11_v2"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "OpenLogic",
                        "offer": "CentOS",
                        "sku": "7.2",
                        "version": "latest"
                    },
                    "osDisk": {
                        "name": "[parameters('virtualMachines_m2_name')]",
                        "createOption": "FromImage",
                        "vhd": {
                            "uri": "[concat('https', '://', parameters('resource_name'), '.blob.core.windows.net', concat('/vhds/', parameters('virtualMachines_m2_name'),'201691211328.vhd'))]"
                        },
                        "caching": "ReadWrite"
                    },
                    "dataDisks": []
                },
                "osProfile": {
                    "computerName": "[parameters('virtualMachines_m2_name')]",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": true,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCyUNoNpGWsREQqL9YUfJyyNHueU1RbfHJNzrDZ74qag4DS2xUsLEufU3XfP6WdDcEooHv3Z6ul5jywhpo9qENxKyj3TpREeVLpMXXUtsu0ZK7NNbNWAdgq9iYSGecIulLa8VjOXTGPIX9YYk88ilcC4B0OoRwKmWNjamDSokDIYnAgz/E/PdAxjE0bR1bWznBUaxVM8KGc8vU1pKJMj3Epg+gRAgiTZTo3tG8sTUU7PkSNNZ1FIFIsLgBfV/d8UQgq2DSrh4iwluIIjKaedlr4GYlo7V7BhS7B7SnaG5InGoB1xlHNANAakyn9N2o41poiEAvMsW2PrBzZZv2QMoyb"
                                }
                            ]
                        }
                    },
                    "secrets": [],
                    "adminPassword": "[parameters('vmAdminPassword')]"
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_m2_name'), parameters('resource_name')))]"
                        }
                    ]
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Storage/storageAccounts', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_m2_name'), parameters('resource_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Compute/virtualMachines/m3'.",
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[parameters('virtualMachines_m3_name')]",
            "apiVersion": "2015-06-15",
            "location": "westus",
            "properties": {
                "hardwareProfile": {
                    "vmSize": "Standard_DS11_v2"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "OpenLogic",
                        "offer": "CentOS",
                        "sku": "7.2",
                        "version": "latest"
                    },
                    "osDisk": {
                        "name": "[parameters('virtualMachines_m3_name')]",
                        "createOption": "FromImage",
                        "vhd": {
                            "uri": "[concat('https', '://', parameters('resource_name'), '.blob.core.windows.net', concat('/vhds/', parameters('virtualMachines_m3_name'),'2016912113346.vhd'))]"
                        },
                        "caching": "ReadWrite"
                    },
                    "dataDisks": []
                },
                "osProfile": {
                    "computerName": "[parameters('virtualMachines_m3_name')]",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": true,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCyUNoNpGWsREQqL9YUfJyyNHueU1RbfHJNzrDZ74qag4DS2xUsLEufU3XfP6WdDcEooHv3Z6ul5jywhpo9qENxKyj3TpREeVLpMXXUtsu0ZK7NNbNWAdgq9iYSGecIulLa8VjOXTGPIX9YYk88ilcC4B0OoRwKmWNjamDSokDIYnAgz/E/PdAxjE0bR1bWznBUaxVM8KGc8vU1pKJMj3Epg+gRAgiTZTo3tG8sTUU7PkSNNZ1FIFIsLgBfV/d8UQgq2DSrh4iwluIIjKaedlr4GYlo7V7BhS7B7SnaG5InGoB1xlHNANAakyn9N2o41poiEAvMsW2PrBzZZv2QMoyb"
                                }
                            ]
                        }
                    },
                    "secrets": [],
                    "adminPassword": "[parameters('vmAdminPassword')]"
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_m3_name'), parameters('resource_name')))]"
                        }
                    ]
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Storage/storageAccounts', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_m3_name'), parameters('resource_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Compute/virtualMachines/p1'.",
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[parameters('virtualMachines_p1_name')]",
            "apiVersion": "2015-06-15",
            "location": "westus",
            "properties": {
                "hardwareProfile": {
                    "vmSize": "Standard_DS4_v2"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "OpenLogic",
                        "offer": "CentOS",
                        "sku": "7.2",
                        "version": "latest"
                    },
                    "osDisk": {
                        "name": "[parameters('virtualMachines_p1_name')]",
                        "createOption": "FromImage",
                        "vhd": {
                            "uri": "[concat('https', '://', parameters('resource_name'), '.blob.core.windows.net', concat('/vhds/', parameters('virtualMachines_p1_name'),'2016912114053.vhd'))]"
                        },
                        "caching": "ReadWrite"
                    },
                    "dataDisks": []
                },
                "osProfile": {
                    "computerName": "[parameters('virtualMachines_p1_name')]",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": true,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCyUNoNpGWsREQqL9YUfJyyNHueU1RbfHJNzrDZ74qag4DS2xUsLEufU3XfP6WdDcEooHv3Z6ul5jywhpo9qENxKyj3TpREeVLpMXXUtsu0ZK7NNbNWAdgq9iYSGecIulLa8VjOXTGPIX9YYk88ilcC4B0OoRwKmWNjamDSokDIYnAgz/E/PdAxjE0bR1bWznBUaxVM8KGc8vU1pKJMj3Epg+gRAgiTZTo3tG8sTUU7PkSNNZ1FIFIsLgBfV/d8UQgq2DSrh4iwluIIjKaedlr4GYlo7V7BhS7B7SnaG5InGoB1xlHNANAakyn9N2o41poiEAvMsW2PrBzZZv2QMoyb"
                                }
                            ]
                        }
                    },
                    "secrets": [],
                    "adminPassword": "[parameters('vmAdminPassword')]"
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_p1_name'), parameters('resource_name')))]"
                        }
                    ]
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Storage/storageAccounts', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_p1_name'), parameters('resource_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Compute/virtualMachines/p2'.",
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[parameters('virtualMachines_p2_name')]",
            "apiVersion": "2015-06-15",
            "location": "westus",
            "properties": {
                "hardwareProfile": {
                    "vmSize": "Standard_DS4_v2"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "OpenLogic",
                        "offer": "CentOS",
                        "sku": "7.2",
                        "version": "latest"
                    },
                    "osDisk": {
                        "name": "[parameters('virtualMachines_p2_name')]",
                        "createOption": "FromImage",
                        "vhd": {
                            "uri": "[concat('https', '://', parameters('resource_name'), '.blob.core.windows.net', concat('/vhds/', parameters('virtualMachines_p2_name'),'201691211476.vhd'))]"
                        },
                        "caching": "ReadWrite"
                    },
                    "dataDisks": []
                },
                "osProfile": {
                    "computerName": "[parameters('virtualMachines_p2_name')]",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": true,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCyUNoNpGWsREQqL9YUfJyyNHueU1RbfHJNzrDZ74qag4DS2xUsLEufU3XfP6WdDcEooHv3Z6ul5jywhpo9qENxKyj3TpREeVLpMXXUtsu0ZK7NNbNWAdgq9iYSGecIulLa8VjOXTGPIX9YYk88ilcC4B0OoRwKmWNjamDSokDIYnAgz/E/PdAxjE0bR1bWznBUaxVM8KGc8vU1pKJMj3Epg+gRAgiTZTo3tG8sTUU7PkSNNZ1FIFIsLgBfV/d8UQgq2DSrh4iwluIIjKaedlr4GYlo7V7BhS7B7SnaG5InGoB1xlHNANAakyn9N2o41poiEAvMsW2PrBzZZv2QMoyb"
                                }
                            ]
                        }
                    },
                    "secrets": [],
                    "adminPassword": "[parameters('vmAdminPassword')]"
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_p2_name'), parameters('resource_name')))]"
                        }
                    ]
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Storage/storageAccounts', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_p2_name'), parameters('resource_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Compute/virtualMachines/p3'.",
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[parameters('virtualMachines_p3_name')]",
            "apiVersion": "2015-06-15",
            "location": "westus",
            "properties": {
                "hardwareProfile": {
                    "vmSize": "Standard_DS4_v2"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "OpenLogic",
                        "offer": "CentOS",
                        "sku": "7.2",
                        "version": "latest"
                    },
                    "osDisk": {
                        "name": "[parameters('virtualMachines_p3_name')]",
                        "createOption": "FromImage",
                        "vhd": {
                            "uri": "[concat('https', '://', parameters('resource_name'), '.blob.core.windows.net', concat('/vhds/', parameters('virtualMachines_p3_name'),'2016912115059.vhd'))]"
                        },
                        "caching": "ReadWrite"
                    },
                    "dataDisks": []
                },
                "osProfile": {
                    "computerName": "[parameters('virtualMachines_p3_name')]",
                    "adminUsername": "azureuser",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": true,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "path": "/home/azureuser/.ssh/authorized_keys",
                                    "keyData": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCyUNoNpGWsREQqL9YUfJyyNHueU1RbfHJNzrDZ74qag4DS2xUsLEufU3XfP6WdDcEooHv3Z6ul5jywhpo9qENxKyj3TpREeVLpMXXUtsu0ZK7NNbNWAdgq9iYSGecIulLa8VjOXTGPIX9YYk88ilcC4B0OoRwKmWNjamDSokDIYnAgz/E/PdAxjE0bR1bWznBUaxVM8KGc8vU1pKJMj3Epg+gRAgiTZTo3tG8sTUU7PkSNNZ1FIFIsLgBfV/d8UQgq2DSrh4iwluIIjKaedlr4GYlo7V7BhS7B7SnaG5InGoB1xlHNANAakyn9N2o41poiEAvMsW2PrBzZZv2QMoyb"
                                }
                            ]
                        }
                    },
                    "secrets": [],
                    "adminPassword": "[parameters('vmAdminPassword')]"
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_p3_name'), parameters('resource_name')))]"
                        }
                    ]
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Storage/storageAccounts', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('virtualMachines_p3_name'), parameters('resource_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkInterfaces/a1773'.",
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(parameters('virtualMachines_a1_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAddress": "172.17.1.5",
                            "privateIPAllocationMethod": "Dynamic",
                            "subnet": {
                                "id": "[concat(resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name')), '/subnets/agents')]"
                            }
                        }
                    }
                ],
                "dnsSettings": {
                    "dnsServers": []
                },
                "enableIPForwarding": false,
                "networkSecurityGroup": {
                    "id": "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_nsg_name')))]"
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_nsg_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkInterfaces/a2572'.",
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(parameters('virtualMachines_a2_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAddress": "172.17.1.4",
                            "privateIPAllocationMethod": "Dynamic",
                            "subnet": {
                                "id": "[concat(resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name')), '/subnets/agents')]"
                            }
                        }
                    }
                ],
                "dnsSettings": {
                    "dnsServers": []
                },
                "enableIPForwarding": false,
                "networkSecurityGroup": {
                    "id": "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_nsg_name')))]"
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_nsg_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkInterfaces/a326'.",
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(parameters('virtualMachines_a3_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAddress": "172.17.1.6",
                            "privateIPAllocationMethod": "Dynamic",
                            "subnet": {
                                "id": "[concat(resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name')), '/subnets/agents')]"
                            }
                        }
                    }
                ],
                "dnsSettings": {
                    "dnsServers": []
                },
                "enableIPForwarding": false,
                "networkSecurityGroup": {
                    "id": "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_nsg_name')))]"
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_nsg_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkInterfaces/boot953'.",
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(parameters('virtualMachines_boot_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAddress": "172.17.0.7",
                            "privateIPAllocationMethod": "Dynamic",
                            "publicIPAddress": {
                                "id": "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_boot_name'), parameters('resource_name')))]"
                            },
                            "subnet": {
                                "id": "[concat(resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name')), '/subnets/default')]"
                            }
                        }
                    }
                ],
                "dnsSettings": {
                    "dnsServers": []
                },
                "enableIPForwarding": false,
                "networkSecurityGroup": {
                    "id": "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_masters_nsg_name')))]"
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_boot_name'), parameters('resource_name')))]",
                "[resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_masters_nsg_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkInterfaces/m1192'.",
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(parameters('virtualMachines_m1_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAddress": "172.17.0.4",
                            "privateIPAllocationMethod": "Dynamic",
                            "publicIPAddress": {
                                "id": "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_m1_name'), parameters('resource_name')))]"
                            },
                            "subnet": {
                                "id": "[concat(resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name')), '/subnets/default')]"
                            }
                        }
                    }
                ],
                "dnsSettings": {
                    "dnsServers": []
                },
                "enableIPForwarding": false,
                "networkSecurityGroup": {
                    "id": "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_masters_nsg_name')))]"
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_m1_name'), parameters('resource_name')))]",
                "[resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_masters_nsg_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkInterfaces/m2777'.",
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(parameters('virtualMachines_m2_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAddress": "172.17.0.6",
                            "privateIPAllocationMethod": "Dynamic",
                            "publicIPAddress": {
                                "id": "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_m2_name'), parameters('resource_name')))]"
                            },
                            "subnet": {
                                "id": "[concat(resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name')), '/subnets/default')]"
                            }
                        }
                    }
                ],
                "dnsSettings": {
                    "dnsServers": []
                },
                "enableIPForwarding": false,
                "networkSecurityGroup": {
                    "id": "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_masters_nsg_name')))]"
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_m2_name'), parameters('resource_name')))]",
                "[resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_masters_nsg_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkInterfaces/m3526'.",
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(parameters('virtualMachines_m3_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAddress": "172.17.0.5",
                            "privateIPAllocationMethod": "Dynamic",
                            "publicIPAddress": {
                                "id": "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_m3_name'), parameters('resource_name')))]"
                            },
                            "subnet": {
                                "id": "[concat(resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name')), '/subnets/default')]"
                            }
                        }
                    }
                ],
                "dnsSettings": {
                    "dnsServers": []
                },
                "enableIPForwarding": false,
                "networkSecurityGroup": {
                    "id": "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_masters_nsg_name')))]"
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_m3_name'), parameters('resource_name')))]",
                "[resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_masters_nsg_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkInterfaces/p1289'.",
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(parameters('virtualMachines_p1_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAddress": "172.17.2.5",
                            "privateIPAllocationMethod": "Dynamic",
                            "publicIPAddress": {
                                "id": "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_p1_name'), parameters('resource_name')))]"
                            },
                            "subnet": {
                                "id": "[concat(resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name')), '/subnets/agents-public')]"
                            }
                        }
                    }
                ],
                "dnsSettings": {
                    "dnsServers": []
                },
                "enableIPForwarding": false,
                "networkSecurityGroup": {
                    "id": "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_public_nsg_name')))]"
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_p1_name'), parameters('resource_name')))]",
                "[resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_public_nsg_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkInterfaces/p2792'.",
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(parameters('virtualMachines_p2_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAddress": "172.17.2.6",
                            "privateIPAllocationMethod": "Dynamic",
                            "publicIPAddress": {
                                "id": "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_p2_name'), parameters('resource_name')))]"
                            },
                            "subnet": {
                                "id": "[concat(resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name')), '/subnets/agents-public')]"
                            }
                        }
                    }
                ],
                "dnsSettings": {
                    "dnsServers": []
                },
                "enableIPForwarding": false,
                "networkSecurityGroup": {
                    "id": "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_public_nsg_name')))]"
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_p2_name'), parameters('resource_name')))]",
                "[resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_public_nsg_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkInterfaces/p3599'.",
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[concat(parameters('virtualMachines_p3_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAddress": "172.17.2.4",
                            "privateIPAllocationMethod": "Dynamic",
                            "publicIPAddress": {
                                "id": "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_p3_name'), parameters('resource_name')))]"
                            },
                            "subnet": {
                                "id": "[concat(resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name')), '/subnets/agents-public')]"
                            }
                        }
                    }
                ],
                "dnsSettings": {
                    "dnsServers": []
                },
                "enableIPForwarding": false,
                "networkSecurityGroup": {
                    "id": "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_public_nsg_name')))]"
                }
            },
            "resources": [],
            "dependsOn": [
                "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('virtualMachines_p3_name'), parameters('resource_name')))]",
                "[resourceId('Microsoft.Network/virtualNetworks', parameters('resource_name'))]",
                "[resourceId('Microsoft.Network/networkSecurityGroups', concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_public_nsg_name')))]"
            ]
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkSecurityGroups/agents-nsg'.",
            "type": "Microsoft.Network/networkSecurityGroups",
            "name": "[concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_nsg_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "securityRules": [
                    {
                        "name": "default-allow-ssh",
                        "properties": {
                            "protocol": "TCP",
                            "sourcePortRange": "*",
                            "destinationPortRange": "22",
                            "sourceAddressPrefix": "*",
                            "destinationAddressPrefix": "*",
                            "access": "Allow",
                            "priority": 1000,
                            "direction": "Inbound"
                        }
                    }
                ]
            },
            "resources": [],
            "dependsOn": []
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkSecurityGroups/agents-public-nsg'.",
            "type": "Microsoft.Network/networkSecurityGroups",
            "name": "[concat(parameters('resource_name'), parameters('networkSecurityGroups_agents_public_nsg_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "securityRules": [
                    {
                        "name": "default-allow-ssh",
                        "properties": {
                            "protocol": "TCP",
                            "sourcePortRange": "*",
                            "destinationPortRange": "22",
                            "sourceAddressPrefix": "*",
                            "destinationAddressPrefix": "*",
                            "access": "Allow",
                            "priority": 1000,
                            "direction": "Inbound"
                        }
                    }
                ]
            },
            "resources": [],
            "dependsOn": []
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/networkSecurityGroups/esri56-masters-nsg'.",
            "type": "Microsoft.Network/networkSecurityGroups",
            "name": "[concat(parameters('resource_name'), parameters('networkSecurityGroups_masters_nsg_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "securityRules": [
                    {
                        "name": "default-allow-ssh",
                        "properties": {
                            "protocol": "TCP",
                            "sourcePortRange": "*",
                            "destinationPortRange": "22",
                            "sourceAddressPrefix": "*",
                            "destinationAddressPrefix": "*",
                            "access": "Allow",
                            "priority": 1000,
                            "direction": "Inbound"
                        }
                    }
                ]
            },
            "resources": [],
            "dependsOn": []
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/publicIPAddresses/boot-ip'.",
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[concat(parameters('virtualMachines_boot_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "publicIPAllocationMethod": "Dynamic",
                "idleTimeoutInMinutes": 4
            },
            "resources": [],
            "dependsOn": []
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/publicIPAddresses/m1-ip'.",
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[concat(parameters('virtualMachines_m1_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "publicIPAllocationMethod": "Dynamic",
                "idleTimeoutInMinutes": 4
            },
            "resources": [],
            "dependsOn": []
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/publicIPAddresses/m2-ip'.",
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[concat(parameters('virtualMachines_m2_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "publicIPAllocationMethod": "Dynamic",
                "idleTimeoutInMinutes": 4
            },
            "resources": [],
            "dependsOn": []
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/publicIPAddresses/m3-ip'.",
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[concat(parameters('virtualMachines_m3_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "publicIPAllocationMethod": "Dynamic",
                "idleTimeoutInMinutes": 4
            },
            "resources": [],
            "dependsOn": []
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/publicIPAddresses/p1-ip'.",
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[concat(parameters('virtualMachines_p1_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "publicIPAllocationMethod": "Dynamic",
                "idleTimeoutInMinutes": 4
            },
            "resources": [],
            "dependsOn": []
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/publicIPAddresses/p2-ip'.",
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[concat(parameters('virtualMachines_p2_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "publicIPAllocationMethod": "Dynamic",
                "idleTimeoutInMinutes": 4
            },
            "resources": [],
            "dependsOn": []
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/publicIPAddresses/p3-ip'.",
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[concat(parameters('virtualMachines_p3_name'), parameters('resource_name'))]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "publicIPAllocationMethod": "Dynamic",
                "idleTimeoutInMinutes": 4
            },
            "resources": [],
            "dependsOn": []
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Network/virtualNetworks/esri56-vnet'.",
            "type": "Microsoft.Network/virtualNetworks",
            "name": "[parameters('resource_name')]",
            "apiVersion": "2016-03-30",
            "location": "westus",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        "172.17.0.0/16"
                    ]
                },
                "subnets": [
                    {
                        "name": "default",
                        "properties": {
                            "addressPrefix": "172.17.0.0/24"
                        }
                    },
                    {
                        "name": "agents",
                        "properties": {
                            "addressPrefix": "172.17.1.0/24"
                        }
                    },
                    {
                        "name": "agents-public",
                        "properties": {
                            "addressPrefix": "172.17.2.0/24"
                        }
                    }
                ]
            },
            "resources": [],
            "dependsOn": []
        },
        {
            "comments": "Generalized from resource: '/subscriptions/a17613f2-c602-4fc3-bfde-a40bc97a54b6/resourceGroups/esri56/providers/Microsoft.Storage/storageAccounts/esri56disks'.",
            "type": "Microsoft.Storage/storageAccounts",
            "sku": {
                "name": "Premium_LRS",
                "tier": "Premium"
            },
            "kind": "Storage",
            "name": "[parameters('resource_name')]",
            "apiVersion": "2016-01-01",
            "location": "westus",
            "tags": {},
            "properties": {},
            "resources": [],
            "dependsOn": []
        }
    ]
}
