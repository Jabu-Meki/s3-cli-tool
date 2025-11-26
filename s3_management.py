import boto3
import logging
from botocore.exceptions import ClientError
import json
import os

# Set up logging
logging.getLogger('botocore').setLevel(logging.WARNING)


def create_bucket(bucket_name, region="us-east-1"):
    """Create an S3 bucket in a specified region"""
    try:
        s3_client = boto3.client('s3', region_name=region)
        
        if region == 'us-east-1':
            response = s3_client.create_bucket(Bucket=bucket_name)
        else:
            response = s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        logging.info(f"Bucket '{bucket_name}' created successfully in region '{region}'")
        return True
        
    except ClientError as e:
        logging.error(f"Error creating bucket: {e}")
        return False

def list_buckets():
    """List all S3 buckets"""
    try:
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        
        print('\nExisting buckets:')
        for bucket in response['Buckets']:
            print(f"  {bucket['Name']}")
            
    except ClientError as e:
        logging.error(f"Error listing buckets: {e}")

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket"""
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        logging.info(f"File '{file_name}' uploaded to '{bucket}/{object_name}'")
        return True
    except ClientError as e:
        logging.error(f"Error uploading file: {e}")
        return False

def download_file(bucket_name, object_name, file_name):
    """Download a file from S3 bucket"""
    try:
        s3 = boto3.client('s3')
        s3.download_file(bucket_name, object_name, file_name)
        logging.info(f"File '{object_name}' downloaded as '{file_name}'")
    except ClientError as e:
        logging.error(f"Error downloading file: {e}")

def set_bucket_policy(bucket_name):
    """Set a public read policy on bucket"""
    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [{
            'Sid': 'AddPerm',
            'Effect': 'Allow',
            'Principal': '*',
            'Action': ['s3:GetObject'],
            'Resource': f'arn:aws:s3:::{bucket_name}/*'
        }]
    }

    try:
        bucket_policy_json = json.dumps(bucket_policy)
        s3 = boto3.client('s3')
        s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy_json)
        logging.info(f"Public read policy applied to bucket '{bucket_name}'")
    except ClientError as e:
        logging.error(f"Error setting bucket policy: {e}")

def delete_bucket_and_contents(bucket_name):
    """Delete bucket and all its contents"""
    s3 = boto3.client('s3')

    try:
        # List and delete all objects
        objects = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in objects:
            for obj in objects['Contents']:
                s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
                print(f"Deleted {obj['Key']}")

        # Delete the bucket
        s3.delete_bucket(Bucket=bucket_name)
        print(f"Deleted bucket: {bucket_name}")
        return True
        
    except ClientError as e:
        logging.error(f"Error deleting bucket: {e}")
        return False

def main():
    while True:
        print("\n" + "="*45)
        print("   S3 Bucket Management System")
        print("="*45)
        print("1. Create New Bucket")
        print("2. List existing buckets")
        print("3. Upload file to bucket")
        print("4. Download file from bucket")
        print("5. Add public read policy to bucket")
        print("6. Delete bucket and all contents")
        print("7. Exit\n")
        
        try:
            choice = int(input("Please select an operation (1-7): "))
        except ValueError:
            print("Please enter a number from 1-7")
            continue

        if choice == 1:
            bucket_name = input("Please enter the bucket name to create: ")
            region = input("Enter region (default: us-east-1): ") or "us-east-1"
            create_bucket(bucket_name, region)
            print(f"{bucket_name} created in {region}")

        elif choice == 2:
            list_buckets()

        elif choice == 3:
            filename = input("Enter the filename to upload: ")
            bucket = input("Enter bucket name: ")
            object_name = input("Enter object name (optional, press enter to use filename): ") or None
            upload_file(filename, bucket, object_name)

        elif choice == 4:
            bucket_name = input("Enter bucket name: ")
            object_name = input("Enter object name: ")
            file_name = input("Enter local filename to save as: ")
            download_file(bucket_name, object_name, file_name)

        elif choice == 5:
            bucket_name = input("Enter the bucket to apply public read policy to: ")
            set_bucket_policy(bucket_name)

        elif choice == 6:
            bucket_name = input("Enter bucket to delete (CAUTION: ALL CONTENTS WILL BE DELETED): ")
            confirm = input(f"Type 'YES' to confirm deletion of bucket '{bucket_name}': ")
            if confirm == 'YES':
                delete_bucket_and_contents(bucket_name)
            else:
                print("Deletion cancelled.")

        elif choice == 7:
            print("Exiting. Goodbye!")
            break

        else:
            print("Invalid choice, please try again")

if __name__ == "__main__":
    main()