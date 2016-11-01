import json
import string
import os
import random
import time

# Input Parameters
VERSION="1.0.0.0"

CLUSTERSIZE = "dev"

if CLUSTERSIZE == "mini":
    NUM_MASTERS=1
    NUM_AGENTS=3
    NUM_AGENTS_PUBLIC=1
elif CLUSTERSIZE == "small":
    NUM_MASTERS=3
    NUM_AGENTS=7
    NUM_AGENTS_PUBLIC=3
elif CLUSTERSIZE == "dev":
    NUM_MASTERS=1
    NUM_AGENTS=5
    NUM_AGENTS_PUBLIC=1


OUT_FOLDER = "/home/david"

MASTER_VM_SIZE="Standard_DS11_v2"
AGENT_VM_SIZE="Standard_DS4_v2"
    
# GROUPS
MASTER_GROUP = "master"
AGENT_GROUP = "agent"
AGENT_PUBLIC_GROUP = "agent_public"


def createAvailabilitySet(group_name):

    resource = {}

    resource["comments"] = group_name
    resource["type"] = "Microsoft.Compute/availabilitySets"
    resource["name"] = "[concat(resourceGroup().name,'_', '" + group_name + "')]"
    resource["apiVersion"] = "2015-06-15"
    resource["location"] = "[resourceGroup().location]"
    resource["properties"] = {}
    resource["resources"] = []
    resource["dependsOn"] = []

    return resource


def createVM(name, group_name, size):

    resource = {}

    dtg = time.strftime("%Y%m%d%H%M%S")
    
    resource["comments"] = name 
    resource["type"] = "Microsoft.Compute/virtualMachines"
    resource["name"] = "[concat(resourceGroup().name,'_', '" + name + "')]"
    resource["apiVersion"] = "2015-06-15"
    resource["location"] = "[resourceGroup().location]"

    resource["properties"] = {}

    if group_name != "":
        resource["properties"]["availabilitySet"] = {}
        resource["properties"]["availabilitySet"]["id"] = "[resourceId('Microsoft.Compute/availabilitySets', concat(resourceGroup().name,'_', '" + group_name + "'))]"

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
    resource["properties"]["storageProfile"]["osDisk"]["vhd"]["uri"] = "[concat('https', '://', resourceGroup().name, '.blob.core.windows.net', concat('/vhds/', '" + name + "', '" + dtg + ".vhd'))]"
    resource["properties"]["storageProfile"]["osDisk"]["caching"] = "ReadWrite"
    resource["properties"]["storageProfile"]["dataDisks"] = []

    resource["properties"]["osProfile"] = {}
    resource["properties"]["osProfile"]["computerName"] = name
    resource["properties"]["osProfile"]["adminUsername"] = "[parameters('username')]"

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
    network_id["id"] = "[resourceId('Microsoft.Network/networkInterfaces', concat(resourceGroup().name, '_', '" + name + "'))]"
    resource["properties"]["networkProfile"]["networkInterfaces"].append(network_id)

    resource["resources"] = []
    
    resource["dependsOn"] = []
    if group_name != "":
        resource["dependsOn"].append("[resourceId('Microsoft.Compute/availabilitySets', concat(resourceGroup().name,'_', '" + group_name + "'))]")
    resource["dependsOn"].append("[resourceId('Microsoft.Storage/storageAccounts', resourceGroup().name)]")
    resource["dependsOn"].append("[resourceId('Microsoft.Network/networkInterfaces', concat(resourceGroup().name,'_','" + name + "'))]")
    
    return resource


def createNetworkInterface(name,group_name,cnt):

    resource = {}
    
    resource["comments"] = name 
    resource["type"] = "Microsoft.Network/networkInterfaces"
    resource["name"] = "[concat(resourceGroup().name, '_', '" + name + "')]"
    resource["apiVersion"] = "2016-03-30"
    resource["location"] = "[resourceGroup().location]"

    resource["properties"] = {}

    resource["properties"]["ipConfigurations"] = []

    ipconfig = {}

    ipconfig["name"] = "ipconfig1"
    ipconfig["properties"] = {}
    

    if group_name == MASTER_GROUP:
        # Offset dynamic addresses to start at 10
        ipconfig["properties"]["privateIPAddress"] = "172.17.1." + str(10 + cnt)
        ipconfig["properties"]["privateIPAllocationMethod"] = "Static"    
        ipconfig["properties"]["publicIPAddress"] = {}
        ipconfig["properties"]["publicIPAddress"]["id"] = "[resourceId('Microsoft.Network/publicIPAddresses', concat(resourceGroup().name,'_','" + name + "'))]"
    elif group_name == AGENT_PUBLIC_GROUP:
        ipconfig["properties"]["privateIPAllocatedMethod"] = "Dynamic"

    else:
        ipconfig["properties"]["privateIPAllocatedMethod"] = "Dynamic"
        
        
    ipconfig["properties"]["subnet"] = {}
    ipconfig["properties"]["subnet"]["id"] = "[concat(resourceId('Microsoft.Network/virtualNetworks', resourceGroup().name), '/subnets/" + group_name + "')]"

    resource["properties"]["ipConfigurations"].append(ipconfig)

    resource["properties"]["dnsSettings"] = {}
    resource["properties"]["dnsSettings"]["dnsServers"] = []
    resource["properties"]["enabledIPForwarding"] = False
    resource["properties"]["networkSecurityGroup"] = {}
    resource["properties"]["networkSecurityGroup"]["id"] = "[resourceId('Microsoft.Network/networkSecurityGroups', concat(resourceGroup().name, '_', '" + group_name + "'))]"
    resource["resources"] = []
    
    resource["dependsOn"] = []
    if group_name == MASTER_GROUP:    
        resource["dependsOn"].append("[resourceId('Microsoft.Network/publicIPAddresses', concat(resourceGroup().name,'_','" + name + "'))]")
    elif group_name == AGENT_PUBLIC_GROUP:
        resource["dependsOn"].append("[resourceId('Microsoft.Network/loadBalancers', concat(resourceGroup().name,'_', '" + group_name + "'))]")
    resource["dependsOn"].append("[resourceId('Microsoft.Network/virtualNetworks', resourceGroup().name)]")
    resource["dependsOn"].append("[resourceId('Microsoft.Network/networkSecurityGroups', concat(resourceGroup().name,'_','" + group_name + "'))]")
    
    return resource    


def createNSG(group_name):

    resource = {}
    
    resource["comments"] = group_name 
    resource["type"] = "Microsoft.Network/networkSecurityGroups"
    resource["name"] = "[concat(resourceGroup().name,'_', '" + group_name + "')]"
    resource["apiVersion"] = "2016-03-30"
    resource["location"] = "[resourceGroup().location]"

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
    resource["name"] = "[concat(resourceGroup().name,'_', '" + name + "')]"
    resource["apiVersion"] = "2016-03-30"
    resource["location"] = "[resourceGroup().location]"

    resource["properties"] = {}

    resource["properties"]["publicAllocationMethod"] = "Dynamic"
    resource["properties"]["idelTimeoutInMinutes"] = 4
    
    resource["resources"] = []
    
    resource["dependsOn"] = []

    return resource


def createVirutalNetworks():

    resource = {}
    
    resource["comments"] = "[resourceGroup().name]"
    resource["type"] = "Microsoft.Network/virtualNetworks"
    resource["name"] = "[resourceGroup().name]"
    resource["apiVersion"] = "2016-03-30"
    resource["location"] = "[resourceGroup().location]"

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
    
    resource["comments"] = "[resourceGroup().name]"
    resource["type"] = "Microsoft.Storage/storageAccounts"
    resource["sku"] = {}
    resource["sku"]["name"] = "Premium_LRS"
    resource["sku"]["tier"] = "Premium"
    resource["kind"]= "Storage"
    resource["name"] = "[resourceGroup().name]"
    resource["apiVersion"] = "2016-01-01"
    resource["location"] = "[resourceGroup().location]"
    resource["tags"] = {}
    resource["properties"] = {}
    resource["resources"] = []
    resource["dependsOn"] = []

    return resource



def createLoadBalancer(group_name):
    resource = {}
    
    resource["comments"] = "[resourceGroup().name]"
    resource["type"] = "Microsoft.Network/loadBalancers"
    resource["name"] = "[concat(resourceGroup().name,'_', '" + group_name + "')]"
    resource["apiVersion"] = "2016-03-30"
    resource["location"] = "[resourceGroup().location]"
    resource["properties"] = {}
    resource["properties"]["frontendIPConfigurations"] = []
    
    ipconfig = {}
    ipconfig["name"] = "[concat(resourceGroup().name,'_', '" + group_name + "','_1')]"
    ipconfig["properties"] = {}
    ipconfig["properties"]["privateIPAllocationMethod"] = "Dynamic"
    ipconfig["properties"]["publicIPAddress"] = {}
    ipconfig["properties"]["publicIPAddress"]["id"] = "[resourceId('Microsoft.Network/publicIPAddresses', concat(resourceGroup().name,'_', '" + group_name + "'))]"
    resource["properties"]["frontendIPConfigurations"].append(ipconfig)
    
    resource["properties"]["backendAddressPools"] = []
    resource["properties"]["loadBalancingRules"] = []

    ## WORKING HERE
##    if group_name == AGENT_PUBLIC_GROUP:
##        rule = {}
##        rule["name"] = AGENT_PUBLIC_GROUP + "_80"
##        rule["properties"] = {}
##        rule["properties"]["frontendIPConfiguration"] = {}
##        rule["properties"]["frontendIPConfiguration"]["id"] = AGENT_PUBLIC_GROUP + "_80"
        
        
    
    resource["properties"]["probes"] = []
    resource["resources"] = []
    resource["dependsOn"] = []
    resource["dependsOn"].append("[resourceId('Microsoft.Network/publicIPAddresses', concat(resourceGroup().name,'_', '" + group_name + "'))]")

    
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
    resources.append(createNetworkInterface("boot",MASTER_GROUP,0))
    resources.append(createPublicIP("boot"))
    
    i = 0
    while i < NUM_MASTERS:
        i += 1
        name = "m" + str(i)
        resources.append(createVM(name, MASTER_GROUP, MASTER_VM_SIZE))    
        resources.append(createNetworkInterface(name,MASTER_GROUP,i))
        resources.append(createPublicIP(name))

    i = 0
    while i < NUM_AGENTS:
        i += 1
        name = "a" + str(i)
        resources.append(createVM(name, "", AGENT_VM_SIZE))    
        resources.append(createNetworkInterface(name,"agent",i))

    i = 0
    while i < NUM_AGENTS_PUBLIC:
        i += 1
        name = "p" + str(i)
        resources.append(createVM(name, AGENT_PUBLIC_GROUP, AGENT_VM_SIZE))    
        resources.append(createNetworkInterface(name,AGENT_PUBLIC_GROUP,i))
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

       
