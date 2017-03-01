#!/bin/bash

# This script was created to try an automate the process of uploading to S3 using AWS CLI using multi-part upload

# https://aws.amazon.com/premiumsupport/knowledge-center/s3-multipart-upload-cli/

# During testing I did not see any significant improvment in upload speed over just a simple s3 cp.

# 9 FEB 2017
#  - Added & to the aws upload-part; and commented out the rm to test uploading all parts at the same time
#  - The max upload speed was whatever my Network upload supported 600KB/s 
#  - From Corporate Network the speed for s3 cp was 6.6MB/s 

# While interesting the script doesn't seem useful

FILE=$1
BUCKET=$2
SIZE=$3

#FILE=simFile_10000_10s2.dat
#BUCKET=geoevent-ova-files
#SIZE=50M

PREFIX=$(head /dev/urandom | tr -dc A-Za-z | head -c 10)


split -a 3 -d -b $SIZE $FILE $PREFIX 

MD5=$(openssl md5 -binary $FILE | base64)

ID=$(aws s3api create-multipart-upload --bucket $BUCKET --key $FILE --metadata md5=$MD5 | jq .UploadId -r)

cnt=0
for f in ${PREFIX}*
do
	echo $f
	let CNT=CNT+1
	aws s3api upload-part --bucket $BUCKET --key $FILE --part-number  $CNT --body $f --upload-id  $ID --content-md5 $(openssl md5 -binary $f | base64) &
	#rm $f
done

echo "FILE=$FILE"
echo "PREFIX=$PREFIX"
echo "BUCKET=$BUCKET"
echo "SIZE=$SIZE"
echo "MD5=$MD5"
echo "ID=$ID"


# Create Json file input is the json from list-parts the output is a json file with object Parts with just two fields from original Json; Maps Fields
#aws s3api list-parts --bucket $BUCKET --key $FILE --upload-id $ID |  jq '{Parts: [ .Parts[] | {PartNumber: .PartNumber, ETag: .ETag}]}' > fileparts.json
echo "aws s3api list-parts --bucket \$BUCKET --key \$FILE --upload-id \$ID |  jq '{Parts: [ .Parts[] | {PartNumber: .PartNumber, ETag: .ETag}]}' > fileparts.json"


#aws s3api complete-multipart-upload --multipart-upload file://fileparts.json --bucket $BUCKET --key $FILE --upload-id $ID
echo "aws s3api complete-multipart-upload --multipart-upload file://fileparts.json --bucket \$BUCKET --key \$FILE --upload-id \$ID"

# If something goes wrong list the upload and delete as needed

#aws s3api list-multipart-uploads --bucket $BUCKET
echo "aws s3api list-multipart-uploads --bucket \$BUCKET"

#aws s3api abort-multipart-upload --bucket $BUCKET --key $FILE --upload-id $ID
echo "aws s3api abort-multipart-upload --bucket \$BUCKET --key \$FILE --upload-id \$ID"

#rm -f ${PREFIX}*
echo rm -f \${PREFIX}\*
