# Install dcos
curl -O https://downloads.dcos.io/binaries/cli/linux/x86-64/0.4.15/dcos
chmod +x dcos

# Configure DCOS
./dcos config set core.dcos_url https://10.10.0.11
./dcos config set core.ssl_verify false

## The following command prompts for username/password for DCOS
## I haven't figure out how to script it yet
./dcos auth login

./dcos package install --cli dcos-enterprise-cli

# Genreate key pair 
./dcos security org service-accounts keypair trinity-private-key.pem trinity-public-key.pem

# Create Service Account
./dcos security cluster ca cacert > dcos-ca.crt
./dcos security org service-accounts show
./dcos security org service-accounts create -p trinity-public-key.pem -d "Trinity service account" trinity-principal
./dcos security org service-accounts show trinity-principal

# Create trinity-secret
./dcos security secrets create-sa-secret --strict trinity-private-key.pem trinity-principal trinity-secret
./dcos security secrets list /

# Install jq
yum install epel-release -y
yum install jq -y

# This just display the trinity-secret value
./dcos security secrets get /trinity-secret --json | jq -r .value | jq

# Adminrouter Permissions


curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:adminrouter:ops:historyservice/users/trinity-principal/full

curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:adminrouter:ops:mesos/users/trinity-principal/full

curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:adminrouter:ops:metadata/users/trinity-principal/full

curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:adminrouter:ops:networking/users/trinity-principal/full

curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:adminrouter:ops:slave/users/trinity-principal/full

curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:adminrouter:ops:system-health/users/trinity-principal/full

curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:adminrouter:package/users/trinity-principal/full

curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:adminrouter:service:marathon/users/trinity-principal/full

curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:adminrouter:service:metronome -H 'Content-Type: application/json' -d '{"description":"dcos:adminrouter:service:metronome"}'
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:adminrouter:service:metronome/users/trinity-principal/full

# Secrets Permissions

curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:secrets:default:%252Ftrinity-secret -H 'Content-Type: application/json' -d '{"description":"dcos:secrets:default:/trinity-secret"}'
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:secrets:default:%252Ftrinity-secret/users/trinity-principal/create 
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:secrets:default:%252Ftrinity-secret/users/trinity-principal/delete
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:secrets:default:%252Ftrinity-secret/users/trinity-principal/read
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:secrets:default:%252Ftrinity-secret/users/trinity-principal/update


# Service Permissions

curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:service:marathon:marathon:services:%252F -H 'Content-Type: application/json' -d '{"description":"dcos:service:marathon:marathon:services:/"}'
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:service:marathon:marathon:services:%252F/users/trinity-principal/create
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:service:marathon:marathon:services:%252F/users/trinity-principal/delete
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:service:marathon:marathon:services:%252F/users/trinity-principal/read
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:service:marathon:marathon:services:%252F/users/trinity-principal/update

# Mesos Permissions 
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:mesos:agent:endpoint:path:%252Fmetrics%252Fsnapshot -H 'Content-Type: application/json' -d '{"description":"dcos:mesos:agent:endpoint:path:/metrics/snapshot"}'
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:mesos:agent:endpoint:path:%252Fmetrics%252Fsnapshot/users/trinity-principal/read 

curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:mesos:agent:endpoint:path:%252Fcontainers -H 'Content-Type: application/json' -d '{"description":"dcos:mesos:agent:endpoint:path:/containers"}'
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:mesos:agent:endpoint:path:%252Fcontainers/users/trinity-principal/read

curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:mesos:agent:endpoint:path:%252Fmonitor%252Fstatistics -H 'Content-Type: application/json' -d '{"description":"dcos:mesos:agent:endpoint:path:/monitor/statistics"}'
curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:mesos:agent:endpoint:path:%252Fmonitor%252Fstatistics/users/trinity-principal/read


# ***********************************
# Add this permission
# dcos:adminrouter:service:hub01
# Allowed trinity to get to https://master.mesos/service/hub01/v1/plan/status

#curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:adminrouter:service:hub123 -H 'Content-Type: application/json' -d '{"description":"dcos:adminrouter:service:metronome"}'
#curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:adminrouter:service:hub123/users/trinity-principal/full

# ***********************************

# ***********************************
# The following was an attempt to allow SATs; Didn't help SAT would not start

#curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:service:marathon:marathon:services:%252Fsattasks%252Fsat01%252Fapps%252F -H 'Content-Type: application/json' -d '{"description":"dcos:service:marathon:marathon:services:/sattasks/sat01/apps/"}'
#curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:service:marathon:marathon:services:%252Fsattasks%252Fsat01%252Fapps%252F/users/trinity-principal/create
#curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:service:marathon:marathon:services:%252Fsattasks%252Fsat01%252Fapps%252F/users/trinity-principal/delete
#curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:service:marathon:marathon:services:%252Fsattasks%252Fsat01%252Fapps%252F/users/trinity-principal/read
#curl -i -X PUT --cacert dcos-ca.crt -H "Authorization: token=`./dcos config show core.dcos_acs_token`" `./dcos config show core.dcos_url`/acs/api/v1/acls/dcos:service:marathon:marathon:services:%252Fsattasks%252Fsat01%252Fapps%252F/users/trinity-principal/update

# ***********************************
