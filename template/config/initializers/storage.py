from os import environ
from io import StringIO
from jinja2 import Environment, FileSystemLoader
from ruamel.yaml import YAML

storage_env = Environment(loader=FileSystemLoader('.'), autoescape=False)
storage_template = storage_env.get_template("config/storage.yml")
storage_rendered = storage_template.render(environ)
storage_config = YAML(typ="safe").load(StringIO(storage_rendered))

from minio import Minio
from minio.error import S3Error

# client = Minio(
#   endpoint = getenv('MINIO_ENDPOINT_URL').replace('http://', '').replace('https://', ''),
#   access_key = getenv('MINIO_ACCESS_KEY'),
#   secret_key = getenv('MINIO_SECRET_KEY'),
#   secure = getenv('MINIO_ENDPOINT_URL').startswith('https')
# )

# bucket = 'resumee-production'

# # Ensure the bucket exists
# if not client.bucket_exists(bucket):
#     client.make_bucket(bucket)

# # Upload a file
# local_upload_path = 'alembic.ini'
# remote_object_name = 'alembic.txt'

# # client.fput_object(bucket, remote_object_name, local_upload_path)
# # print(f"✅ Uploaded {local_upload_path} to {bucket}/{remote_object_name}")

# # # Download the same file
# # local_download_path = 'downloaded_alembic.ini'

# # client.fget_object(bucket, remote_object_name, local_download_path)
# # print(f"✅ Downloaded {bucket}/{remote_object_name} to {local_download_path}")

# storage = client
