from os import getenv
from minio import Minio
from minio.error import S3Error

# Create the MinIO client
client = Minio(
    endpoint=getenv('MINIO_ENDPOINT_URL').replace('http://', '').replace('https://', ''),
    access_key=getenv('MINIO_ACCESS_KEY'),
    secret_key=getenv('MINIO_SECRET_KEY'),
    secure=getenv('MINIO_ENDPOINT_URL').startswith('https')
)

bucket = 'resumee-production'

# Ensure the bucket exists
if not client.bucket_exists(bucket):
    client.make_bucket(bucket)

# Upload a file
local_upload_path = 'alembic.ini'
remote_object_name = 'alembic.txt'

client.fput_object(bucket, remote_object_name, local_upload_path)
print(f"✅ Uploaded {local_upload_path} to {bucket}/{remote_object_name}")

# Download the same file
local_download_path = 'downloaded_alembic.ini'

client.fget_object(bucket, remote_object_name, local_download_path)
print(f"✅ Downloaded {bucket}/{remote_object_name} to {local_download_path}")

storage = client

# class StorageS3:
#   def __init__(self):
#     self.client = client
#     self.bucket = bucket

#   def upload_file(self, local_upload_path, remote_object_name):
#     self.client.fput_object(self.bucket, remote_object_name, local_upload_path)
#     print(f"✅ Uploaded {local_upload_path} to {self.bucket}/{remote_object_name}")

#   def download_file(self, remote_object_name, local_download_path):
#     self.client.fget_object(self.bucket, remote_object_name, local_download_path)
#     print(f"✅ Downloaded {self.bucket}/{remote_object_name} to {local_download_path}")

#   def get_client(self):
#     return self.client

#   def get_bucket(self):
#     return self.bucket
