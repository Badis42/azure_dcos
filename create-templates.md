<h1>Create Template(s)</h1>

<p> This needs to only be done once for your user. </p>

<h2>Connect to Azure Portal</h2>
<img src="images/create-templates/001.png"/><br>


<h2>Click on More Services</h2>
<p>Search for Templates</p>
<p>Select Templates</p>
<img src="images/create-templates/002.png"/><br>

<h2>Click on Add</h2>
<img src="images/create-templates/003.png"/><br>


<h2>Enter Name and Description</h2>
<p>Name: trinity_mini</p>
<p>Description: boot, masters(1), agents(3), public_agents(1)</p>
<img src="images/create-templates/004.png"/><br>
<p>Click OK</p>

<h2>Copy the Template from Github</h2>

<p>The Templates were created using a <a href="../../azure/arm/arm-template-generator.py"> Python Script</a></p>
<p>You could use the script to create your own custom size templates.</p>
<p>Delete the contents of ARM Template on Azure</p>
<p>Copy the <a href="arm/trinity_mini.json">trinity_mini.json</a> to ARM Template on Azure</p>
<img src="images/create-templates/005.png"/><br>
Click OK
Click Add
Click Refresh
<img src="images/create-templates/006.png"/><br>

<h2>Repeat for other types as desired (dev, small, etc.)</h2>
<img src="images/create-templates/007.png"/><br>

<p>The Templates are now ready to be used</p>
