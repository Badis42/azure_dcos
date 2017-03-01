
## clean_docker.sh 
Removes exited and dead docker conatiners from the cluster.

## check_disks.sh 
Lists each node and the disk space used on that node.

## cluster_cmd.sh
You can execute any command on specified masters, agents, public agents.  

For example: 
<pre>
# bash -i centos.pem cluster_cmd.sh 1 3 1 "free -h"
</pre>
Runs the free -h command on the master, 3 agents, and 1 public agent. 

## multipart-upload.sh
Uses AWS CLI to upload a file using multipart-upload.  Based on my initial tests this wasn't any faster that just using s3 cp command.

<pre>
$ aws s3 cp /media/david/data/DCOSee/1.9/dcos_generate_config_1.9ea.ee.sh s3://geoeventdcosinstallers
</pre>
