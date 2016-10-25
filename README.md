# Create a Template using the Python Script

<a href="arm-template-generator.py">Python Script</a>

# Add Azure Portal 

Add to Azure using "Templates"

Give the Template a Name and Description.

Cut and past the json from the file created by Python Script.



# Deploy the Template

From Azure click Deploy.

Leave the ADMIN_PASSWORD to the default long randome value or enter your own value.  This is not used but is required for connecting to the server.

Specify the RESOURCE_GROUP. I give this the same name as the new Resource Group (e.g. esri64).

Enter the username.  The script was created wi



Under the Review Legal Terms. Click "Purchase"

Click click "Create"

# Connect to the boot server

Look up the boot public id (e.g. esri60_boot).

Then connect using ssh

<pre>
$ ssh -i az az@40.112.208.40
</pre>

# Download the installer

Sudo to root and run curl command.

<pre>
$ sudo su -
# curl -o install_boot.sh 

</pre>
