import boto3
from botocore.client import Config
from minio import Minio
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import io

class Storage:
  def __init__(self, config: Dict[str, Any], environment: str = "development"):
    """
    Initialize the storage client with configuration dictionary.
    
    Args:
        config: Dictionary containing storage configuration
        environment: Environment to use (development/production)
    """
    config = config[environment]
    
    self.driver = config['driver']
    self.bucket = config['bucket']
    self.region = config['region']
    
    if self.driver == 's3':
      self.client = boto3.client(
        's3',
        endpoint_url=config['url_endpoint'],
        aws_access_key_id=config['access_key'],
        aws_secret_access_key=config['secret_key'],
        region_name=self.region,
        config=Config(signature_version='s3v4')
      )
    elif self.driver == 'minio':
      self.client = Minio(
        config['url_endpoint'].replace('https://', ''),
        access_key=config['access_key'],
        secret_key=config['secret_key'],
        secure=True,
        region=self.region
      )
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")

  def upload(self, file_path: Union[str, Path], key: str, bucket: Optional[str] = None) -> str:
    """
    Upload a file to the storage.
    
    Args:
        file_path: Local path to the file
        key: Key (path) where the file will be stored
        bucket: Optional bucket name (overrides default)
        
    Returns:
        str: The URL of the uploaded file
    """
    bucket = bucket or self.bucket
    if not bucket:
      raise ValueError("Bucket must be specified")
        
    file_path = Path(file_path)
    if not file_path.exists():
      raise FileNotFoundError(f"File not found: {file_path}")
        
    if self.driver == 's3':
      self.client.upload_file(str(file_path), bucket, key)
      return f"{self.client.meta.endpoint_url}/{bucket}/{key}"
    elif self.driver == 'minio':
      self.client.fput_object(bucket, key, str(file_path))
      return f"{self.client._endpoint_url}/{bucket}/{key}"
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")

  def download(self, key: str, destination: Union[str, Path], bucket: Optional[str] = None) -> Path:
    """
    Download a file from the storage.
    
    Args:
        key: Key (path) of the file to download
        destination: Local path where the file will be saved
        bucket: Optional bucket name (overrides default)
        
    Returns:
        Path: Path to the downloaded file
    """
    bucket = bucket or self.bucket
    if not bucket:
      raise ValueError("Bucket must be specified")
        
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    if self.driver == 's3':
      self.client.download_file(bucket, key, str(destination))
    elif self.driver == 'minio':
      self.client.fget_object(bucket, key, str(destination))
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")
        
    return destination

  def remove(self, key: str, bucket: Optional[str] = None) -> None:
    """
    Remove a file from the storage.
    
    Args:
        key: Key (path) of the file to remove
        bucket: Optional bucket name (overrides default)
    """
    bucket = bucket or self.bucket
    if not bucket:
      raise ValueError("Bucket must be specified")
        
    if self.driver == 's3':
      self.client.delete_object(Bucket=bucket, Key=key)
    elif self.driver == 'minio':
      self.client.remove_object(bucket, key)
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")

  def list_files(self, prefix: str = "", bucket: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List files in the storage.
    
    Args:
        prefix: Optional prefix to filter files
        bucket: Optional bucket name (overrides default)
        
    Returns:
        List of dictionaries containing file information
    """
    bucket = bucket or self.bucket
    if not bucket:
      raise ValueError("Bucket must be specified")
        
    if self.driver == 's3':
      response = self.client.list_objects_v2(Bucket=bucket, Prefix=prefix)
      return [
        {
          'key': obj['Key'],
          'size': obj['Size'],
          'last_modified': obj['LastModified']
        }
        for obj in response.get('Contents', [])
      ]
    elif self.driver == 'minio':
      objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
      return [
        {
          'key': obj.object_name,
          'size': obj.size,
          'last_modified': obj.last_modified
        }
        for obj in objects
      ]
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")

  def get_url(self, key: str, bucket: Optional[str] = None, expires: int = 3600) -> str:
    """
    Get a temporary URL for a file.
    
    Args:
        key: Key (path) of the file
        bucket: Optional bucket name (overrides default)
        expires: URL expiration time in seconds
        
    Returns:
        str: Temporary URL for the file
    """
    bucket = bucket or self.bucket
    if not bucket:
      raise ValueError("Bucket must be specified")
        
    if self.driver == 's3':
      return self.client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expires
      )
    elif self.driver == 'minio':
      return self.client.presigned_get_object(bucket, key, expires=expires)
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")
