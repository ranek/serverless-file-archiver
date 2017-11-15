import boto3
import datetime
from botocore.vendored import requests
import os

OBJECT_NAME_FORMAT = os.environ['OBJECT_NAME_FORMAT']
S3_BUCKET_NAME = os.environ['S3_BUCKET']
DOWNLOAD_URL = os.environ['DOWNLOAD_URL']

s3_bucket = boto3.resource('s3').Bucket(S3_BUCKET_NAME)


def lambda_handler(event, context):
    object_name = (datetime.datetime.utcnow()).strftime(OBJECT_NAME_FORMAT)
    data = requests.get(DOWNLOAD_URL, timeout=30).content
    s3_bucket.put_object(Key=object_name, Body=data)
    print("Stored object %s" % object_name)
