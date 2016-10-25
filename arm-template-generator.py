import json
import string
import os
import random
import time

# Input Parameters
VERSION="1.0.0.0"

CLUSTERSIZE = "mini"

if CLUSTERSIZE == "mini":
    NUM_MASTERS=1
    NUM_AGENTS=3
    NUM_AGENTS_PUBLIC=1
elif CLUSTERSIZE == "small":
    NUM_MASTERS=3
    NUM_AGENTS=7
    NUM_AGENTS_PUBLIC=3


OUT_FOLDER = "/home/david"

MASTER_VM_SIZE="Standard_DS11_v2"
AGENT_VM_SIZE="Standard_DS4_v2"

LOCATION="westus"

USERNAME = "azureuser"    


# GROUPS
MASTER_GROUP = "master"
AGENT_GROUP = "agent"
AGENT_PUBLIC_GROUP = "agent_public"


def createAvailabilitySet(group_name):

    resource = {}

    resource["comments"] = group_name
    resource["type"] = "Microsoft.Compute/availabilitySets"
    resource["name"] = "[concat(parameters('resourceGroup'),'_', '" + group_name + "')]"
    resource["apiVersion"] = "2015-06-15"
    resource["location"] = LOCATION
    resource["properties"] = {}
    resource["resources"] = []
    resource["dependsOn"] = []

    return resource


def createVM(name, group_name, size):

    resource = {}

    dtg = time.strftime("%Y%m%d%H%M%S")
    
    resource["comments"] = name 
    resource["type"] = "Microsoft.Compute/virtualMachines"
    resource["name"] = "[concat(parameters('resourceGroup'),'_', '" + name + "')]"
    resource["apiVersion"] = "2015-06-15"
    resource["location"] = LOCATION

    resource["properties"] = {}

    if group_name != "":
        resource["properties"]["availabilitySet"] = {}
        resource["properties"]["availabilitySet"]["id"] = "[resourceId('Microsoft.Compute/availabilitySets', concat(parameters('resourceGroup'),'_', '" + group_name + "'))]"

    resource["properties"]["hardwareProfile"] = {}
    resource["properties"]["hardwareProfile"]["vmsize"] = size

    resource["properties"]["storageProfile"] = {}
    resource["properties"]["storageProfile"]["imageReference"] = {}
    resource["properties"]["storageProfile"]["imageReference"]["publisher"] = "OpenLogic"
    resource["properties"]["storageProfile"]["imageReference"]["offer"] = "CentOS"
    resource["properties"]["storageProfile"]["imageReference"]["sku"] = "7.2"
    resource["properties"]["storageProfile"]["imageReference"]["version"] = "latest"
    
    resource["properties"]["storageProfile"]["osDisk"] = {}
    resource["properties"]["storageProfile"]["osDisk"]["name"] = name
    resource["properties"]["storageProfile"]["osDisk"]["createOption"] = "FromImage"
    resource["properties"]["storageProfile"]["osDisk"]["vhd"] = {}
    resource["properties"]["storageProfile"]["osDisk"]["vhd"]["uri"] = "[concat('https', '://', parameters('resourceGroup'), '.blob.core.windows.net', concat('/vhds/', '" + name + "', '" + dtg + ".vhd'))]"
    resource["properties"]["storageProfile"]["osDisk"]["caching"] = "ReadWrite"
    resource["properties"]["storageProfile"]["dataDisks"] = []

    resource["properties"]["osProfile"] = {}
    resource["properties"]["osProfile"]["computerName"] = name
    resource["properties"]["osProfile"]["adminUsername"] = USERNAME

    resource["properties"]["osProfile"]["linuxConfiguration"] = {}
    resource["properties"]["osProfile"]["linuxConfiguration"]["disablePasswordAuthentication"] = True
    resource["properties"]["osProfile"]["linuxConfiguration"]["ssh"] = {}
    resource["properties"]["osProfile"]["linuxConfiguration"]["ssh"]["publicKeys"] = []

    publicKey = {}
    publicKey["path"] = "[concat('/home/', parameters('username'), '/.ssh/authorized_keys')]"
    publicKey["keyData"] = "[parameters('publicKey')]"
    
    resource["properties"]["osProfile"]["linuxConfiguration"]["ssh"]["publicKeys"].append(publicKey)

    resource["properties"]["networkProfile"] = {}
    resource["properties"]["networkProfile"]["networkInterfaces"] = []

    network_id = {}
    network_id["id"] = "[resourceId('Microsoft.Network/networkInterfaces', concat(parameters('resourceGroup'), '_', '" + name + "'))]"
    resource["properties"]["networkProfile"]["networkInterfaces"].append(network_id)

    resource["resources"] = []
    
    resource["dependsOn"] = []
    if group_name != "":
        resource["dependsOn"].append("[resourceId('Microsoft.Compute/availabilitySets', concat(parameters('resourceGroup'),'_', '" + group_name + "'))]")
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

    if nsg in [MASTER_GROUP]:    
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
    if nsg in [MASTER_GROUP]:    
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
    subnet["name"] = MASTER_GROUP
    subnet["properties"] = {}
    subnet["properties"]["addressPrefix"]="172.17.1.0/24"
    resource["properties"]["subnets"].append(subnet)

    subnet = {}
    subnet["name"] = AGENT_GROUP
    subnet["properties"] = {}
    subnet["properties"]["addressPrefix"]="172.17.2.0/24"
    resource["properties"]["subnets"].append(subnet)
    
    subnet = {}
    subnet["name"] = AGENT_PUBLIC_GROUP
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



def createLoadBalancer(group_name):
    resource = {}
    
    resource["comments"] = "[parameters('resourceGroup')]"
    resource["type"] = "Microsoft.Network/loadBalancers"
    resource["name"] = "[concat(parameters('resourceGroup'),'_', '" + group_name + "')]"
    resource["apiVersion"] = "2016-03-30"
    resource["location"] = LOCATION
    resource["properties"] = {}
    resource["properties"]["frontendIPConfigurations"] = []
    
    ipconfig = {}
    ipconfig["name"] = "[concat(parameters('resourceGroup'),'_', '" + group_name + "','_1')]"
    ipconfig["properties"] = {}
    ipconfig["properties"]["privateIPAllocationMethod"] = "Dynamic"
    ipconfig["properties"]["publicIPAddress"] = {}
    ipconfig["properties"]["publicIPAddress"]["id"] = "[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('resourceGroup'),'_', '" + group_name + "'))]"
    resource["properties"]["frontendIPConfigurations"].append(ipconfig)
    
    resource["properties"]["backendAddressPools"] = []
    resource["properties"]["loadBalancingRules"] = []
    resource["properties"]["probes"] = []
    resource["resources"] = []
    resource["dependsOn"] = []
    resource["dependsOn"].append("[resourceId('Microsoft.Network/publicIPAddresses', concat(parameters('resourceGroup'),'_', '" + group_name + "'))]")

    
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
    paramvals['defaultValue'] = None
    paramvals['type'] = "String"
    parameters["username"] = paramvals

    paramvals = {}
    paramvals['defaultValue'] = None
    paramvals['type'] = "String"
    parameters["publicKey"] = paramvals
    
    data['parameters'] = parameters

    resources = []

    # Create Availability Sets
    resources.append(createAvailabilitySet(MASTER_GROUP))
    resources.append(createAvailabilitySet(AGENT_PUBLIC_GROUP))
        
    # Create Virtual Machines
    resources.append(createVM("boot", "", MASTER_VM_SIZE))
    resources.append(createNetworkInterface("boot",MASTER_GROUP))
    resources.append(createPublicIP("boot"))
    
    i = 0
    while i < NUM_MASTERS:
        i += 1
        name = "m" + str(i)
        resources.append(createVM(name, MASTER_GROUP, MASTER_VM_SIZE))    
        resources.append(createNetworkInterface(name,MASTER_GROUP))
        resources.append(createPublicIP(name))

    i = 0
    while i < NUM_AGENTS:
        i += 1
        name = "a" + str(i)
        resources.append(createVM(name, "", AGENT_VM_SIZE))    
        resources.append(createNetworkInterface(name,"agent"))

    i = 0
    while i < NUM_AGENTS_PUBLIC:
        i += 1
        name = "p" + str(i)
        resources.append(createVM(name, AGENT_PUBLIC_GROUP, AGENT_VM_SIZE))    
        resources.append(createNetworkInterface(name,AGENT_PUBLIC_GROUP))
        #resources.append(createPublicIP(name))


    # Create Network Security Groups
    resources.append(createNSG(MASTER_GROUP))
    resources.append(createNSG(AGENT_GROUP))
    resources.append(createNSG(AGENT_PUBLIC_GROUP))

    # Create Public IP for load balancers
    resources.append(createPublicIP(MASTER_GROUP))
    resources.append(createPublicIP(AGENT_PUBLIC_GROUP))    

    # Create Load Balancers
    resources.append(createLoadBalancer(MASTER_GROUP))
    resources.append(createLoadBalancer(AGENT_PUBLIC_GROUP))    

    # Create VirtualNetwork
    resources.append(createVirutalNetworks())

    # Create Storage Account
    resources.append(createStorageAccounts())

    data['resources']  = resources

    #pjson_data = json.dumps(data, indent=4,sort_keys=True)
    pjson_data = json.dumps(data, indent=4)


    fout = open(OUT_FOLDER + "/trinity_" + CLUSTERSIZE + ".json","w")
    fout.write(pjson_data)
    fout.close()
    
#print(pjson_data)
