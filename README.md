# Provision Azure resources using the Azure Portal
This option uses the Azure Portal to individually establish the raw resources needed as a pre-requisite to run the DC/OS installer. Step-by-step instructions for the following topics are included:<br>



<br>

## Create an Azure Resource Group
An Azure Resource Group is a logical place where resources that are common to a purpose can be organized.  We will establish a new resource group so all the resources we provision for running an o/eDC/OS environment can be logically grouped together.<br>
<br><b>Step 1:</b> Login to the Azure Portal using the Azure subscription you wish to provision resources to: <a href="https://portal.azure.com">https://portal.azure.com</a><br>
<img src="../../images/dcos-portal/00-resourcegroup/01.png"/><br>
<br><b>Step 2:</b> Click on the 'Resources Groups' menu option and click the 'Add' button.<br>
<img src="../../images/dcos-portal/00-resourcegroup/02.png"/><br>
<br><b>Step 3:</b> Give your Resource group a name, select the Azure subscription, select the region you wish to use and click the 'Create' button.<br>
<img src="../../images/dcos-portal/00-resourcegroup/03.png"/><br>
<br><b>Step 4:</b> Verify that the Resource groups listing contains the new resource group that was just created.<br>
<img src="../../images/dcos-portal/00-resourcegroup/04.png"/><br>

<br>

## Create a Boot VM

A Boot VM is needed when installing o/eDC/OS manually as we will do later on in this deploment option.<br>
<br><b>Step 5:</b> Open up the resource group that was just created and notice that it has 'No resources to display'.  Click the 'Add' button on the resource group to add a New Item.<br>
<img src="../../images/dcos-portal/01-boot/01.png"/><br>
<br><b>Step 6:</b> Enter 'CentOS 7.2' in the 'Search Everything' text box and hit Enter to see the results.<br>
<img src="../../images/dcos-portal/01-boot/02.png"/><br>
<br><b>Step 7:</b> Select the 'CentOS-based 7.2' item from the publisher OpenLogic.  Click the 'Create' button to create a new VM based on the 'CentOS-based 7.2' VM image.<br>
<img src="../../images/dcos-portal/01-boot/03.png"/><br>
<br><b>Step 8:</b> Fill in the 'Create Virtual Machine -> Basics' form as follows:<br>
<img src="../../images/dcos-portal/01-boot/04.png"/><br>
<ul><li>Name: (your resource group name)-boot</li>
<li>VM disk type: SSD</li>
<li>User name: azureuser</li>
<li>Authentication type: SSH public key</li>
<li>SSH public key: (copy the contents of your public ssh key)</li>
<li>Subscription: (your Azure subscription)</li>
<li>Resource Group: Use existing (select your resource group)</li>
<li>Location: (select your desired Azure region location)</li></ul>
<br><b>Step 9:</b> 'Choose a size' for your boot VM image.  A DS2_V2 Standard image is sufficient for the boot VM.<br>
<img src="../../images/dcos-portal/01-boot/05.png"/><br>
## Create Network Security Groups
<br><b>Step 10:</b> Configure the first few 'Settings' as follows:<br>
<img src="../../images/dcos-portal/01-boot/06.png"/><br>
<ul><li>Storage account: (leave default)</li>
<li>Virtual network: (new) (your resource group name)-vnet</li>
<li>Subnet: default (e.g. 172.17.0.0/24)</li>
<li>Public IP address: (new) (your resource group name)-boot-ip</li></ul>
<br><b>Step 11:</b> Click the 'Public IP address' and configure it to 'Create new' with a Name: 'boot-ip' but update the Assignment to be 'Static'.<br>


<img src="../../images/dcos-portal/01-boot/07.png"/><br>
<br><b>Step 12:</b> Configure the remaining 'Settings' as follows:<br>
<img src="../../images/dcos-portal/01-boot/08.png"/><br>
<ul><li>Network security group (firewall): (new) (your resource group name)-boot-nsg</li>
<li>Extensions: No extensions</li>
<li>High availability: Availity Set None</li>
<li>Boot diagnostics: Enabled</li>
<li>Guest OS diagnostics: Disabled</li>
<li>Diagnostics storage account: (leave default)</li></ul>
<br><b>Step 13:</b> Click the 'OK' button on 'Settings' and review the 'Summary' verifying that the Validation passed.<br>
<img src="../../images/dcos-portal/01-boot/09.png"/><br>
<br><b>Step 14:</b> Press 'OK' on 'Summary' to start provisioning the Boot VM<br>
<img src="../../images/dcos-portal/01-boot/10.png"/><br>
<br><b>Step 15:</b> Once the Boot VM has been fully provisioned it will show up on the Azure dashboard as 'Running'.<br>
<img src="../../images/dcos-portal/01-boot/11.png"/><br>

<br>

## Create Network Security Groups
In oDC/OS machines are assigned to a Virtual Network (VNET) that acts as a sandbox to a collection of similar machines such as masters, private agents and public agents.  Each VNET has a Network Security Group (NSG) that defines the inbound routing rules for what HTTP/TCP traffic is allowed.  In this section we will define the NSGs that will work with our oDC/OS masters, private agents and public agents.  In the next section we will [Create Virtual Networks](#create-virtual-networks).<br>
<br><b>Step 16:</b> In the Azure Portal open the Resource Group that was created previously.<br>
<img src="../../images/dcos-portal/02-networksecuritygroup/01.png"/><br>
<br><b>Step 17:</b> Click the 'Add' button at the top of the Resource Group page and filter by 'Network Security Group'.<br>
<img src="../../images/dcos-portal/02-networksecuritygroup/02.png"/><br>
<br><b>Step 18:</b> Click on the 'Network Security Group' result that is from publisher 'Microsoft' and review the description.<br>
<img src="../../images/dcos-portal/02-networksecuritygroup/03.png"/><br>
<br><b>Step 19:</b> Click the 'Create' button on the 'Network Security Group', fill in the form as follows and click the 'Create' button to create a Network Security Group for the masters:<br>
<img src="../../images/dcos-portal/02-networksecuritygroup/04.png"/><br>
<ul><li>Name: (your resource group name)-masters-nsg</li>
<li>Subscription: (your Azure subscription)</li>
<li>Resource group: Use existing, (select your resource group)</li>
<li>Location: (your Azure region location of choice)</li></ul>
<br><b>Step 20:</b> We now will do the same to establish a Network Security Group for the Private Agents.  Click the 'Create' button on the 'Network Security Group', fill in the form as follows and click the 'Create' button:<br>
<img src="../../images/dcos-portal/02-networksecuritygroup/05.png"/><br>
<ul><li>Name: (your resource group name)-agentprivate-nsg</li>
<li>Subscription: (your Azure subscription)</li>
<li>Resource group: Use existing, (select your resource group)</li>
<li>Location: (your Azure region location of choice)</li></ul>
<br><b>Step 21:</b> We now will do the same to establish a Network Security Group for the Public Agents.  Click the 'Create' button on the 'Network Security Group', fill in the form as follows and click the 'Create' button:<br>
<img src="../../images/dcos-portal/02-networksecuritygroup/06.png"/><br>
<ul><li>Name: (your resource group name)-agentpublic-nsg</li>
<li>Subscription: (your Azure subscription)</li>
<li>Resource group: Use existing, (select your resource group)</li>
<li>Location: (your Azure region location of choice)</li></ul>
<br><b>Step 22:</b> Viewing an 'Overview' of the Resource Group we can see that NSGs in the listing and see that the resource group has a status of 'Deploying'.<br>
<img src="../../images/dcos-portal/02-networksecuritygroup/07.png"/><br>
<br><b>Step 23:</b> The oDC/OS masters network security group needs to have an 'ssh' inbound security rule enabled so that we are allowed access into establishing an ssh tunnel to manage the deployment (we will show this much later but set the access up now).  We now will drill into the masters NSG that we created and enable ssh access.  Click on the '...-masters-nsg' and review the 'Overview'.  We can see that their are currently no Inbound or Outbound security rules configured.<br>
<img src="../../images/dcos-portal/02-networksecuritygroup/08.png"/><br>
<br><b>Step 24:</b> Click on 'Inbound security rules' and click on the 'Add' button to add a new inbound security rule for the masters Network Security Group.<br>
<img src="../../images/dcos-portal/02-networksecuritygroup/09.png"/><br>
<br><b>Step 25:</b> Fill in the Inbound security rule form as follows and click the 'OK' button:<br>
<img src="../../images/dcos-portal/02-networksecuritygroup/10.png"/><br>
<ul><li>Name: ssh</li>
<li>Priority: 100</li>
<li>Source: Any</li>
<li>Service: SSH</li>
<li>Protocol: TCP</li>
<li>Port range: 22</li>
<li>Action: Allow</li></ul>
<br><b>Step 26:</b> Verify in the '...-masters-nsg' Network Security Groups Inbound security rules now show a rule for 'ssh'.<br>
<img src="../../images/dcos-portal/02-networksecuritygroup/11.png"/><br>

<br>

## Create Virtual Networks
During the step to [Create a Boot VM](#create-a-boot-vm) at step 10 when we configure the VM settings one of the configuration options was 'Network' and within that was a property for 'Virtual Network' (VNET).  Each VM instance in oDC/OS belongs to a VNET and when we created the Boot VM we specific to establish a '(new) (your resource group name)-vnet'.  oDC/OS runs applications/micro-services as containers and each container is assigned a unique IP.  In order for this to be work properly we will establish three distinct subnets within our VNET for the masters, private agents and public agents.<br>
<br><b>Step 27:</b> In the Azure Portal open the Resource Group and click on the (your resource group name)-vnet item in the listing.<br>
<img src="../../images/dcos-portal/03-virtualnetwork/01.png"/><br>
<br><b>Step 28:</b> At this point the VNET has only one connected device, the Boot VM, which belongs to the default subnet.  Note that the IP that was assigned to the Boot VM is 172.17.0.4.<br>
<img src="../../images/dcos-portal/03-virtualnetwork/02.png"/><br>
<br><b>Step 29:</b> Clicking on the 'Subnets' of the VNET we can see the 'default' subnet listed with an IP range of 172.17.0.0/24.  In oDC/OS we will use the 'default' subnet for the Boot VM (only needed during setup) as well as the masters.  We will now establish new subnets for the private agents and public agents.  Click on 'default'; click on Network Security Group; then select esri117-masters-nsg.<br>
<img src="../../images/dcos-portal/03-virtualnetwork/03.png"/><br>
<br><b>Step 30:</b> On the VNET click the 'Add Subnet' button to create a subnet for the private agents and fill in the properties of the form as follows:<br>
<img src="../../images/dcos-portal/03-virtualnetwork/04.png"/><br>
<ul><li>Name: (your resource group name)-agentprivate-subnet</li>
<li>Address Range (CIDR block): 172.17.1.0/24</li>
<li>Network security group: select (your resource group name)-agentprivate-nsg</li>
<li>Route table: None</li></ul>
<br><b>Step 31:</b> Verify that in the VNET a new subnet shows in the listing for 'agent-private-subnet'.<br>
<img src="../../images/dcos-portal/03-virtualnetwork/05.png"/><br>
<br><b>Step 32:</b> Repeat steps 30-31 again to create a subnet for the public agents using the following properties:<br>
<ul><li>Name: (your resource group name)-agentpublic-subnet</li>
<li>Address Range (CIDR block): 172.17.2.0/24</li>
<li>Network security group: select (your resource group name)-agentpublic-nsg</li>
<li>Route table: None</li></ul>
Verify that in the VNET a new subnet shows in the listing for 'agent-public-subnet'.<br>
<img src="../../images/dcos-portal/03-virtualnetwork/06.png"/><br>
<br>

## Create Availability Sets
You'll need to create Availability Sets for Load Balancers for the Masters and Public Agents.<br>
<br><b>Step 33:</b> Click Add from Resource Group. Search for Availability Set.<br>
Click on Availability Set and click 'Create'<br>
<ul><li>Name: (your resource group name)-masters-as</li>
<li>Defaults for remaining</li>
</ul>
Click Create<br>
Repease and create another Availabilty for Public Agents.  (e.g. Name: (your resource group name)-agentpublic-as)<br>
<br>

## Create Master VMs
In oDC/OS masters have the responsibility of keeping the configuration of the cluster consistent and scheduling work to be allocated on private and public agents.  To ensure consistency of the configuration it is required to have at least three nodes participating as masters to form a quorum.  In this section we will establish the raw resources needed for the masters.<br>
<br><b>Step 34:</b> In the Azure Portal open your resource group and click the 'Add' button to add a master VM.<br>
<img src="../../images/dcos-portal/04-masters/01.png"/><br>
<br><b>Step 35:</b> Enter 'CentOS 7.2' in the 'Search Everything' text box and hit Enter to see the results.<br>
<img src="../../images/dcos-portal/04-masters/02.png"/><br>
<br><b>Step 36:</b> Select the 'CentOS-based 7.2' item from the publisher OpenLogic.  Click the 'Create' button to create a new VM based on the 'CentOS-based 7.2' VM image.<br>
<img src="../../images/dcos-portal/04-masters/03.png"/><br>
<br><b>Step 37:</b> Fill in the 'Create Virtual Machine -> Basics' form as follows:<br>
<img src="../../images/dcos-portal/04-masters/04.png"/><br>
<ul><li>Name: (your resource group name)-master-01</li>
<li>VM disk type: SSD</li>
<li>User name: azureuser</li>
<li>Authentication type: SSH public key</li>
<li>SSH public key: (copy the contents of your public ssh key)</li>
<li>Subscription: (your Azure subscription)</li>
<li>Resource Group: Use existing (select your resource group)</li>
<li>Location: (select your desired Azure region location)</li></ul>
<br><b>Step 38:</b> 'Choose a size' for your boot VM image.  A DS11_V2 Standard image is sufficient for a master VM.<br>
<img src="../../images/dcos-portal/04-masters/05.png"/><br>
<br><b>Step 39:</b> Configure the 'Settings' as follows:<br>
<img src="../../images/dcos-portal/04-masters/06.png"/><br>
<ul><li>Storage account: (leave default)</li>
<li>Virtual network: (new) (your resource group name)-vnet</li>
<li>Subnet: default (172.17.0.0/24)</li>
<li>Public IP address: Click the 'Public IP address' and configure it to 'Create new' with a Name: 'master-01-ip' but update the Assignment to be 'Static'.</li>
<ul><li></li></ul>
<li>Network security group (firewall): select (your resource group name)-masters-nsg</li>
<li>Extensions: No extensions</li>
<li>High availability: (your resource group name)-masters-as</li>
<li>Boot diagnostics: Enabled</li>
<li>Guest OS diagnostics: Disabled</li>
<li>Diagnostics storage account: (leave default)</li></ul>
<br><b>Step 40:</b> Click the 'OK' button on 'Settings' and review the 'Summary' verifying that the Validation passed.<br>
<img src="../../images/dcos-portal/04-masters/07.png"/><br>
<br><b>Step 41:</b> Press 'OK' on 'Summary' to start provisioning the master VM.<br>
<img src="../../images/dcos-portal/04-masters/08.png"/><br>
<br><b>Step 42:</b> Once the Master VM has been fully provisioned it will show up on the Azure dashboard as 'Running'.<br>
<img src="../../images/dcos-portal/04-masters/09.png"/><br>
<br><b>Step 43:</b> Repeat steps 34-42 two more times to create VMs for 'master-02' and 'master-03'.<br>
<img src="../../images/dcos-portal/04-masters/10.png"/><br>
<br><b>Step 44:</b> Once the 'master-02' and 'master-03' VMs has been fully provisioned they will show up on the Azure dashboard as 'Running'.<br>
<img src="../../images/dcos-portal/04-masters/11.png"/><br>
<br><b>Step 45:</b> Open the resource group and verify that 'master-01', 'master-02' and 'master-03' are listed as VMs.<br>
<img src="../../images/dcos-portal/04-masters/12.png"/><br>

<br>

## Create Private Agent VMs
In oDC/OS private agents are the worker nodes that run tasks.  Private nodes are not accessable outside of the oDC/OS cluster and are scheduled/allocated work only by the master nodes when new tasks are requested.  The number of private agnent nodes is entirely dependent on the performance and scalability needs of the oDC/OS cluster.  In this section we will establish the raw resources needed for the private agents.<br>
<br><b>Step 46:</b> In the Azure Portal open your resource group and click the 'Add' button to add a private agent VM.<br>
<img src="../../images/dcos-portal/05-agentprivate/01.png"/><br>
<br><b>Step 47:</b> Enter 'CentOS 7.2' in the 'Search Everything' text box and hit Enter to see the results.<br>
<img src="../../images/dcos-portal/05-agentprivate/02.png"/><br>
<br><b>Step 48:</b> Select the 'CentOS-based 7.2' item from the publisher OpenLogic.  Click the 'Create' button to create a new VM based on the 'CentOS-based 7.2' VM image.<br>
<img src="../../images/dcos-portal/05-agentprivate/03.png"/><br>
<br><b>Step 49:</b> Fill in the 'Create Virtual Machine -> Basics' form as follows:<br>
<img src="../../images/dcos-portal/05-agentprivate/04.png"/><br>
<ul><li>Name: agent-private-01</li>
<li>VM disk type: SSD</li>
<li>User name: azureuser</li>
<li>Authentication type: SSH public key</li>
<li>SSH public key: (copy the contents of your public ssh key)</li>
<li>Subscription: (your Azure subscription)</li>
<li>Resource Group: Use existing (select your resource group)</li>
<li>Location: (select your desired Azure region location)</li></ul>
<br><b>Step 50:</b> 'Choose a size' for your boot VM image.  A DS4_V2 Standard image is sufficient for a private agent VM.<br>
<img src="../../images/dcos-portal/05-agentprivate/05.png"/><br>
<br><b>Step 51:</b> Configure the first few 'Settings' as follows:<br>
<img src="../../images/dcos-portal/05-agentprivate/06.png"/><br>
<ul><li>Storage account: (leave default)</li>
<li>Virtual network: (new) (your resource group name)-vnet</li>
<li>Subnet: select the agent-private-subnet (172.17.1.0/24)</li></ul>
<br><b>Step 52:</b> Configure the 'Public IP address' in 'Settings' as follows:<br>
<img src="../../images/dcos-portal/05-agentprivate/07.png"/><br>
<ul><li>Public IP address: click the 'Public IP address' and configure it to 'None'.</li></ul>
<br><b>Step 53:</b> Configure the remaining 'Settings' as follows:<br>
<img src="../../images/dcos-portal/05-agentprivate/08.png"/><br>
<li>Network security group (firewall): select (your resource group name)-agentprivate-nsg</li>
<li>Extensions: No extensions</li>
<li>High availability: Availity Set None</li>
<li>Boot diagnostics: Enabled</li>
<li>Guest OS diagnostics: Disabled</li>
<li>Diagnostics storage account: (leave default)</li></ul>
<br><b>Step 54:</b> Click the 'OK' button on 'Settings' and review the 'Summary' verifying that the Validation passed.<br>
<img src="../../images/dcos-portal/05-agentprivate/09.png"/><br>
<br><b>Step 55:</b> Press 'OK' on 'Summary' to start provisioning the private agent VM.<br>
<img src="../../images/dcos-portal/05-agentprivate/10.png"/><br>
<br><b>Step 56:</b> Once the private agent VM has been fully provisioned it will show up on the Azure dashboard as 'Running'.<br>
<img src="../../images/dcos-portal/05-agentprivate/11.png"/><br>
<br><b>Step 57:</b> Repeat steps 46-56 four more times to create VMs for 'agent-private-02', 'agent-private-03', 'agent-private-04' and 'agent-private-05'.<br>
<img src="../../images/dcos-portal/05-agentprivate/12.png"/><br>
<br><b>Step 58:</b> Open the resource group and verify that 'agent-private-01', 'agent-private-02', 'agent-private-03', 'agent-private-04' and 'agent-private-05' are listed as VMs.<br>
<img src="../../images/dcos-portal/05-agentprivate/13.png"/><br>

<br>

## Create Public Agent VMs
In oDC/OS public agents are worker nodes that run tasks that need to have public accessability outside of the oDC/OS cluster.  Public nodes are scheduled/allocated work only by the master nodes when new public tasks are requested.  The number of public agnent nodes is typically at least the number of master nodes for consistency and reliability.  Public agents can run any type of task but are typically only utilized for lightweight things such as software load balancers/proxies.  In this section we will establish the raw resources needed for the public agents.<br>
<br><b>Step 59:</b> In the Azure Portal open your resource group and click the 'Add' button to add a public agent VM.<br>
<img src="../../images/dcos-portal/06-agentpublic/01.png"/><br>
<br><b>Step 60:</b> Enter 'CentOS 7.2' in the 'Search Everything' text box and hit Enter to see the results.<br>
<img src="../../images/dcos-portal/06-agentpublic/02.png"/><br>
<br><b>Step 61:</b> Select the 'CentOS-based 7.2' item from the publisher OpenLogic.  Click the 'Create' button to create a new VM based on the 'CentOS-based 7.2' VM image.<br>
<img src="../../images/dcos-portal/06-agentpublic/03.png"/><br>
<br><b>Step 62:</b> Fill in the 'Create Virtual Machine -> Basics' form as follows:<br>
<img src="../../images/dcos-portal/06-agentpublic/04.png"/><br>
<ul><li>Name: agent-public-01</li>
<li>VM disk type: SSD</li>
<li>User name: azureuser</li>
<li>Authentication type: SSH public key</li>
<li>SSH public key: (copy the contents of your public ssh key)</li>
<li>Subscription: (your Azure subscription)</li>
<li>Resource Group: Use existing (select your resource group)</li>
<li>Location: (select your desired Azure region location)</li></ul>
<br><b>Step 63:</b> 'Choose a size' for your boot VM image.  A DS4_V2 Standard image is sufficient for a public agent VM.<br>
<img src="../../images/dcos-portal/06-agentpublic/05.png"/><br>
<br><b>Step 64:</b> Configure the first few 'Settings' as follows:<br>
<img src="../../images/dcos-portal/06-agentpublic/06.png"/><br>
<ul><li>Storage account: (leave default)</li>
<li>Virtual network: (new) (your resource group name)-vnet</li>
<li>Subnet: select the agent-public-subnet (172.17.2.0/24)</li></ul>
<br><b>Step 65:</b> Configure the 'Public IP address' in 'Settings' as follows:<br>
<img src="../../images/dcos-portal/06-agentpublic/07.png"/><br>
<ul><li>Public IP address: Click the 'Public IP address' and configure it to 'Create new' with a Name: 'agent-public-01-ip' but update the Assignment to be 'Static'.</li></ul>
<br><b>Step 66:</b> Configure the remaining 'Settings' as follows:<br>
<img src="../../images/dcos-portal/06-agentpublic/08.png"/><br>
<li>Network security group (firewall): select (your resource group name)-agentpublic-nsg</li>
<li>Extensions: No extensions</li>
<li>High availability: (your resource group name)-agentpublic-as</li>
<li>Boot diagnostics: Enabled</li>
<li>Guest OS diagnostics: Disabled</li>
<li>Diagnostics storage account: (leave default)</li></ul>
<br><b>Step 67:</b> Click the 'OK' button on 'Settings' and review the 'Summary' verifying that the Validation passed.<br>
<img src="../../images/dcos-portal/06-agentpublic/09.png"/><br>
<br><b>Step 68:</b> Press 'OK' on 'Summary' to start provisioning the public agent VM.<br>
<img src="../../images/dcos-portal/06-agentpublic/10.png"/><br>
<br><b>Step 69:</b> Once the public agent VM has been fully provisioned it will show up on the Azure dashboard as 'Running'.<br>
<img src="../../images/dcos-portal/06-agentpublic/12.png"/><br>
<br><b>Step 70:</b> Repeat steps 59-69 two more times to create VMs for 'agent-public-02' and 'agent-public-03'.<br>
<img src="../../images/dcos-portal/06-agentpublic/13.png"/><br>
<br><b>Step 71:</b> Open the resource group and verify that 'agent-public-01', 'agent-public-02' and 'agent-public-03' are listed as VMs.<br>
<img src="../../images/dcos-portal/06-agentpublic/14.png"/><br>

# Does this work
<br>

## Create Load Balancer
The Load Balancers can spread load accross a set of servers (e.g. public agents).
<br><b>Step 72:</b> From Resrouce Group Click Add. Search for Load Blanacer. Click Create <br>
<ul>
<li>Name: (your resource group name)-agents-pulbic-lb</li>
<li>Public IP: Create a new static public IP (your resource group name)-agents-public-ip</li>
<li>Default for rest of inputs </li>
</ul>
After load balancer is created open it from Resource Group. <br>
<br>
<b>Setup Load Balancer Rules</b><br>
The following is an example of how to open port 10,000 on the public agents to allow Internet Access to a Web Server running on Marathon. Installed Marathon-lb from Universe.  Then; created a Marathon App that run NGINX web server. <br>

<br><b>Step 73:</b> Add Probe <br>
<ul>
<li>Name: (your group resource name)-public-agents-10000 </li>
<li>Protocol: TCP</li>
<li>Port: 10000</li>
<li>Interval: 5</li>
<li>Unhealthy threshold: 2</li>
</ul>
Wait for Updating to complete.
<br><b>Step 74:</b> Add Backend Pool <br>
<ul>
<li>Name: (your group resource name)-public-agents </li>
<li>Availability Set: (your group resource name)-public-agents-as</li>
<li>Virtual Machines: Checkbox to left of each public server</li>
</ul>
Wait for Updating to complete. Be patient it can take a couple of minutes. 
<br><b>Step 75:</b> Add Load Balancing Rule <br>
<ul>
<li>Name: (your group resource name)-public-80-to-10000 </li>
<li>Frontend IP Address: (your group resource name)-public-agent-ip</li>
<li>Protocol: TCP</li>
<li>Port: 80</li>
<li>Backend port: 10000</li>
<li>Backend pool: (your group resource name)-public-agents-10000</li>
<li>Session persistence: Client IP and protocol</li>
<li>Idle timeout: 4 minutes</li>
</ul>
Wait for Updating to complete. 
<br><b>Step 76:</b> Add Inbound Security Rule to Public Agents Network Security Group <br>
<ul>
<li>Name: (your group resource name)-public-agents-allow-10000 </li>
<li>Priority: Default Value (e.g. 1010)</li>
<li>Source: TCP</li>
<li>Service: Custom</li>
<li>Protocol: Any</li>
<li>Port Range: 10000</li>
<li>Action: Allow</li>
</ul>
Wait for Updating to complete. <br>
Now you can try accessing the Agents Public IP with a browser.

<br><br><b>Congratulations:</b> You have established the resources needed as a pre-requisite prior to installing DC/OS.
