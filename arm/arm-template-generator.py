import json
import string
import os
import random
import time

# This Script create JSON to be used in Azure Portal Template.
# The json is saved as files; you can cut/paste the results into your Azure portal account.
# There is room for improvement; I'm not happy about all of the if statements I used to handle GROUPS

# Minor changes to the json can break the Template
# The only way I've found to debug is try to deploy then trace the Errors from Azure Portal back to the code (tedious process)

# Input Parameters
VERSION="1.0.0.0"

# Look at Main Fucntion to see what sets are created (e.g. mini, dev, small)

OUT_FOLDER = "/home/david"

BOOT_VM_SIZE="Standard_DS11_v2"
MASTER_VM_SIZE="Standard_DS11_v2"
AGENT_VM_SIZE="Standard_DS4_v2"
AGENT_PUBLIC_VM_SIZE="Standard_DS11_v2"
    
# GROUPS
BOOT_GROUP="boot"
MASTER_GROUP = "master"
AGENT_GROUP = "agent"
AGENT_PUBLIC_GROUP = "agent_public"

# 80 and 443 will provide access to Web Server running on the public agents
# 9090 provides access to haproxy (if you install Marathon-LB)
# Ports 10000 to 10010 are opened here by default; more could be added if needed.  NOTE: open ports are potential security vulnerabilities (be careful what you expose)
AGENT_PUBLIC_PORTS = [80,443,9090] + range(10000,10010)

# 80 and 443 will provide access to Web Server running on the public agents
MASTER_PORTS = [80,443]



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
    resource["name"] = "[concat(resourceGroup().name, '" + name + "')]"
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

    
    if group_name == BOOT_GROUP:
        # Start Static addresses to start at 10  (DCOS requires Master Internal IP's to be Static)
        ipconfig["properties"]["privateIPAllocatedMethod"] = "Dynamic"

        # Boot Get's a Public IP
        ipconfig["properties"]["publicIPAddress"] = {}
        ipconfig["properties"]["publicIPAddress"]["id"] = "[resourceId('Microsoft.Network/publicIPAddresses', concat(resourceGroup().name,'_','" + name + "'))]"        

    if group_name == MASTER_GROUP:
        # Start Static addresses to start at 10  (DCOS requires Master Internal IP's to be Static)
        ipconfig["properties"]["privateIPAddress"] = "172.17.1." + str(10 + cnt)
        ipconfig["properties"]["privateIPAllocationMethod"] = "Static"

        # Each Master Get's a Public IP
        ipconfig["properties"]["publicIPAddress"] = {}
        ipconfig["properties"]["publicIPAddress"]["id"] = "[resourceId('Microsoft.Network/publicIPAddresses', concat(resourceGroup().name,'_','" + name + "'))]"

        # Configure Load Balancer For Master 
        ipconfig["properties"]["loadBalancerBackendAddressPools"] = []
        pool = {}
        pool["id"] = "[concat(resourceId('Microsoft.Network/loadBalancers', concat(resourceGroup().name,'_', '" + group_name + "')),'/backendAddressPools/',resourceGroup().name,'_" + group_name + "','_pool')]"        
        ipconfig["properties"]["loadBalancerBackendAddressPools"].append(pool)
        
    elif group_name == AGENT_PUBLIC_GROUP:
        # Interanally they get a dynamic IP
        ipconfig["properties"]["privateIPAllocatedMethod"] = "Dynamic"
        
        ipconfig["properties"]["loadBalancerBackendAddressPools"] = []
        pool = {}
        pool["id"] = "[concat(resourceId('Microsoft.Network/loadBalancers', concat(resourceGroup().name,'_', '" + group_name + "')),'/backendAddressPools/',resourceGroup().name,'_" + group_name + "','_pool')]"        
        ipconfig["properties"]["loadBalancerBackendAddressPools"].append(pool)

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
    if group_name == BOOT_GROUP:
        resource["dependsOn"].append("[resourceId('Microsoft.Network/publicIPAddresses', concat(resourceGroup().name,'_','" + name + "'))]")
    elif group_name == MASTER_GROUP:    
        resource["dependsOn"].append("[resourceId('Microsoft.Network/publicIPAddresses', concat(resourceGroup().name,'_','" + name + "'))]")
        resource["dependsOn"].append("[resourceId('Microsoft.Network/loadBalancers', concat(resourceGroup().name,'_', '" + group_name + "'))]")
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

##    if group_name == MASTER_GROUP:
##        priority = 1010
##        for port in MASTER_PORTS:
##            rule = {}
##            rule["name"] = "[concat(resourceGroup().name,'_" + group_name + "_p','" + str(port) + "','_rule')]"
##            rule["properties"] = {}
##            rule["properties"]["protocol"] = "TCP"
##            rule["properties"]["sourcePortRange"] = "*"
##            rule["properties"]["destinationPortRange"] = port
##            rule["properties"]["sourceAddressPrefix"] = "*"
##            rule["properties"]["destinationAddressPrefix"] = "*"
##            rule["properties"]["access"] = "Allow"
##            rule["properties"]["priority"] = priority
##            rule["properties"]["direction"] = "Inbound"    
##            resource["properties"]["securityRules"].append(rule)
##            priority += 10

    
    if group_name == AGENT_PUBLIC_GROUP:
        priority = 1010
        for port in AGENT_PUBLIC_PORTS:
            rule = {}
            rule["name"] = "[concat(resourceGroup().name,'_" + group_name + "_p','" + str(port) + "','_rule')]"
            rule["properties"] = {}
            rule["properties"]["protocol"] = "TCP"
            rule["properties"]["sourcePortRange"] = "*"
            rule["properties"]["destinationPortRange"] = port
            rule["properties"]["sourceAddressPrefix"] = "*"
            rule["properties"]["destinationAddressPrefix"] = "*"
            rule["properties"]["access"] = "Allow"
            rule["properties"]["priority"] = priority
            rule["properties"]["direction"] = "Inbound"    
            resource["properties"]["securityRules"].append(rule)
            priority += 10
    
    
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
    subnet["name"] = BOOT_GROUP
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





def createLoadBalancer(group_name, ports):
    
    
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

    backend_pool = {}
    backend_pool["name"]= "[concat(resourceGroup().name,'_" + group_name + "','_pool')]"
    resource["properties"]["backendAddressPools"].append(backend_pool)
        
    resource["properties"]["loadBalancingRules"] = []

    for port in ports:
        rule = {}
        rule["name"] = "[concat(resourceGroup().name,'_" + group_name + "_p','" + str(port) + "','_lbr')]"
        rule["properties"] = {}
        rule["properties"]["frontendIPConfiguration"] = {}
        rule["properties"]["frontendIPConfiguration"]["id"] = "[concat(resourceId('Microsoft.Network/loadBalancers', concat(resourceGroup().name,'_', '" + group_name + "')),'/frontendIPConfigurations/',resourceGroup().name,'_', '" + group_name + "','_1')]"
        rule["properties"]["frontendPort"] = port
        rule["properties"]["backendPort"] = port
        rule["properties"]["enableFloatingIP"] = False
        rule["properties"]["idleTimeoutInMinutes"] = 4
        rule["properties"]["protocol"] = "Tcp"
        rule["properties"]["loadDistribution"] = "Default"
        rule["properties"]["backendAddressPool"] = {}
        rule["properties"]["backendAddressPool"]["id"] = "[concat(resourceId('Microsoft.Network/loadBalancers', concat(resourceGroup().name,'_', '" + group_name + "')),'/backendAddressPools/',resourceGroup().name,'_" + group_name + "','_pool')]"
        rule["properties"]["probe"] = {}
        rule["properties"]["probe"]["id"] = "[concat(resourceId('Microsoft.Network/loadBalancers', concat(resourceGroup().name,'_', '" + group_name + "')),'/probes/',resourceGroup().name,'_" + group_name + "_p','" + str(port) + "','_probe')]"
        resource["properties"]["loadBalancingRules"].append(rule)
        
    
    resource["properties"]["probes"] = []
        
    for port in ports:
        probe = {}
        probe["name"] = "[concat(resourceGroup().name,'_" + group_name + "_p','" + str(port) + "','_probe')]"
        probe["properties"] = {}
        probe["properties"]["protocol"] = "Tcp"
        probe["properties"]["port"] = port
        probe["properties"]["intervalInSeconds"] = 5
        probe["properties"]["numberOfProbes"] = 2
        resource["properties"]["probes"].append(probe)
    
    
    resource["resources"] = []
    resource["dependsOn"] = []
    resource["dependsOn"].append("[resourceId('Microsoft.Network/publicIPAddresses', concat(resourceGroup().name,'_', '" + group_name + "'))]")

    
    return resource

    

def createJsonFile(num_masters, num_agents, num_public_agents):
    

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
    resources.append(createVM("boot", "", BOOT_VM_SIZE))
    resources.append(createNetworkInterface("boot",BOOT_GROUP,0))
    resources.append(createPublicIP("boot"))
    
    i = 0
    while i < num_masters:
        i += 1
        name = "m" + str(i)
        resources.append(createVM(name, MASTER_GROUP, MASTER_VM_SIZE))    
        resources.append(createNetworkInterface(name,MASTER_GROUP,i))
        resources.append(createPublicIP(name))

    i = 0
    while i < num_agents:
        i += 1
        name = "a" + str(i)
        resources.append(createVM(name, "", AGENT_VM_SIZE))    
        resources.append(createNetworkInterface(name,"agent",i))

    i = 0
    while i < num_public_agents:
        i += 1
        name = "p" + str(i)
        resources.append(createVM(name, AGENT_PUBLIC_GROUP, AGENT_PUBLIC_VM_SIZE))    
        resources.append(createNetworkInterface(name,AGENT_PUBLIC_GROUP,i))
        #resources.append(createPublicIP(name))


    # Create Network Security Groups
    resources.append(createNSG(BOOT_GROUP))
    resources.append(createNSG(MASTER_GROUP))
    resources.append(createNSG(AGENT_GROUP))
    resources.append(createNSG(AGENT_PUBLIC_GROUP))
    

    # Create Public IP for load balancers
    resources.append(createPublicIP(MASTER_GROUP))
    resources.append(createPublicIP(AGENT_PUBLIC_GROUP))    

    # Create Load Balancers
    resources.append(createLoadBalancer(MASTER_GROUP, MASTER_PORTS))
    resources.append(createLoadBalancer(AGENT_PUBLIC_GROUP,AGENT_PUBLIC_PORTS))    

    # Create VirtualNetwork
    resources.append(createVirutalNetworks())

    # Create Storage Account
    resources.append(createStorageAccounts())

    data['resources']  = resources

    #pjson_data = json.dumps(data, indent=4,sort_keys=True)
    pjson_data = json.dumps(data, indent=4)
    return pjson_data



if __name__ == '__main__':


    # Create Mini
    pjson_data = createJsonFile(1,3,1)    
    fout = open(OUT_FOLDER + "/trinity_mini.json","w")
    fout.write(pjson_data)
    fout.close()
    
    # Create Dev
    pjson_data = createJsonFile(1,5,1)    
    fout = open(OUT_FOLDER + "/trinity_dev.json","w")
    fout.write(pjson_data)
    fout.close()
       
    # Create Small
    pjson_data = createJsonFile(3,7,3)    
    fout = open(OUT_FOLDER + "/trinity_small.json","w")
    fout.write(pjson_data)
    fout.close()

    # Create Medium
    pjson_data = createJsonFile(3,47,3)    
    fout = open(OUT_FOLDER + "/trinity_medium.json","w")
    fout.write(pjson_data)
    fout.close()

    # Create Large
    pjson_data = createJsonFile(3,97,3)    
    fout = open(OUT_FOLDER + "/trinity_large.json","w")
    fout.write(pjson_data)
    fout.close()

