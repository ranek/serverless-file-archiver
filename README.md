# serverless-file-archiver

This is a simple [AWS Lambda](https://aws.amazon.com/lambda/) function that downloads a file from a given URL and stores it in an S3 bucket. This is useful if you encounter some frequently changing data on the web and want to keep a copy in S3. For example, you may wish to keep a copy of nightly builds of an open source project, or archive a regularly updated dump of open data. Using Lambda absolves you of having to keep a server on-line to run an infrequent task. With the help of CloudWatch Events, your function can automatically run on a regular basis, either at a fixed rate (e.g. minutely, hourly, daily), or per a cron expression (e.g. every Sunday at 12:00, the first day of every month at midnight).

In some cases, you may wish to very frequently poll a small, textual web resource, for example to save a few kilobytes of realtime data, or archive a small JSON or XML feed. If you're running every one to five minutes, the S3 put request charges may exceed the cost of writing to CloudWatch Logs, and CloudWatch Logs also provides useful filtering and alarming functionality. If this interests you, you may wish to visit my similar [serverless-feed-logger](https://github.com/ranek/serverless-file-archiver) app, which doesn't require and S3 bucket.

## Deployment

Deploying this serverless app to your AWS account is quick and easy using [AWS CloudFormation](https://aws.amazon.com/cloudformation/). 

### Packaging

With the [AWS CLI](https://aws.amazon.com/cli/) installed, run the following command to upload the code to S3. You need to re-run this if you change the code in `archiver.py`. Be sure to set `DEPLOYMENT_S3_BUCKET` to a **bucket you own**; CloudFormation will copy the code function into a ZIP file in this S3 bucket, which can be deployed to AWS Lambda in the following steps. 

```sh
DEPLOYMENT_S3_BUCKET="YOUR_S3_BUCKET"
aws cloudformation package --template-file cloudformation.yaml --s3-bucket $DEPLOYMENT_S3_BUCKET \
  --output-template-file cloudformation-packaged.yaml
```

Now you will have `cloudformation-packaged.yaml`, which contains the full path to the ZIP file created by the previous step. 

### Configuring

Next, let's set the required configuration. You can set the following parameters:

 * `STACK_NAME` is the name of the CloudFormation stack that you'll create to manage all the resources (Lambda functions, CloudWatch Events, S3 buckets, IAM policies) associated with this app. You can set this to a new value to create a new instance with different parameters in your account, or use the same value when re-running to update parameters of an existing deployment.
 * `OBJECT_NAME_FORMAT` determines the name of the saved archives in S3. It will be passed to Python's [strftime](https://docs.python.org/3.6/library/datetime.html#strftime-strptime-behavior) function. You may wish to add an appropriate file extension.
 * `DOWNLOAD_URL` is the path to the file you want to download and save to S3.
 * `SCHEDULE` is a [CloudWatch Event Schedule Expression](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html) at which to invoke this function.

```sh
STACK_NAME="serverless-file-archiver"
OBJECT_NAME_FORMAT="%Y-%m-%dT%H:%M:%S.zip"
DOWNLOAD_URL="https://wordpress.org/nightly-builds/wordpress-latest.zip"
SCHEDULE="rate(1 day)"
```

With these configuration parameters defined, we can call `cloudformation deploy` to create the necessary resources in your AWS account:

```sh
aws cloudformation deploy --template-file cloudformation-packaged.yaml --capabilities CAPABILITY_IAM \
  --parameter-overrides \
  "Schedule=$SCHEDULE" \
  "ObjectNameFormat=$OBJECT_NAME_FORMAT" \
  "DownloadURL=$DOWNLOAD_URL" \
  --stack-name $STACK_NAME
````

If all went well, your stack has been created. You can view the destination S3 bucket it created by running the following command. You can also view the stack in the AWS Console for more information.

```sh
aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs' --output text
```
