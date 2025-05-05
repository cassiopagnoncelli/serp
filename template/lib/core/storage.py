import boto3
from botocore.client import Config
from minio import Minio
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import io
from datetime import timedelta

class Storage:
  def __init__(self, config: Dict[str, Any], verbose: bool = False):
    """
    Initialize the storage client with configuration dictionary.
    
    Args:
        config: Dictionary containing storage configuration
        verbose: Whether to enable verbose logging (default: False)
    """
    self.verbose = verbose
    self.driver = config['driver']
    self.bucket = config['bucket']
    self.region = config['region']
    self.url_endpoint = config['url_endpoint']
    self.access_key = config['access_key']
    self.secret_key = config['secret_key']
    
    if not self.bucket:
      raise ValueError("Bucket must be specified in configuration")
    
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
      # Remove protocol and trailing slashes from endpoint
      endpoint = config['url_endpoint'].replace('https://', '').replace('http://', '').rstrip('/')
      self.client = Minio(
        endpoint,
        access_key=config['access_key'],
        secret_key=config['secret_key'],
        secure=True,
        region=self.region
      )
      
      # Ensure bucket exists
      if not self.client.bucket_exists(self.bucket):
        self.client.make_bucket(self.bucket)
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")

  def _log(self, message: str) -> None:
    """Internal logging method that respects verbosity setting."""
    if self.verbose:
      print(message)

  def upload(self, file_path: Union[str, Path], key: str) -> str:
    """
    Upload a file to the storage.
    
    Args:
        file_path: Local path to the file
        key: Key (path) where the file will be stored
        
    Returns:
        str: The URL of the uploaded file
    """
    file_path = Path(file_path)
    self._log(f"Uploading file: {file_path} to bucket={self.bucket}, key={key}")
    
    if not file_path.exists():
      raise FileNotFoundError(f"File not found: {file_path}")
        
    if self.driver == 's3':
      self.client.upload_file(str(file_path), self.bucket, key)
      return f"{self.client.meta.endpoint_url}/{self.bucket}/{key}"
    elif self.driver == 'minio':
      try:
        # Ensure bucket exists
        if not self.client.bucket_exists(self.bucket):
          self._log(f"Creating bucket: {self.bucket}")
          self.client.make_bucket(self.bucket)
        
        self._log(f"Uploading to Minio: bucket={self.bucket}, key={key}")
        self.client.fput_object(self.bucket, key, str(file_path))
        
        # Verify the upload
        try:
          objects = list(self.client.list_objects(self.bucket, prefix=key, recursive=True))
          if any(obj.object_name == key for obj in objects):
            self._log("Upload verified successfully")
          else:
            self._log("Warning: Upload verification failed - file not found in bucket")
        except Exception as e:
          self._log(f"Upload verification error: {str(e)}")
          
        return f"{self.url_endpoint}/{self.bucket}/{key}"
      except Exception as e:
        self._log(f"Minio upload error: {str(e)}")
        raise
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")

  def download(self, key: str, destination: Union[str, Path]) -> Path:
    """
    Download a file from the storage.
    
    Args:
        key: Key (path) of the file to download
        destination: Local path where the file will be saved
        
    Returns:
        Path: Path to the downloaded file
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    if self.driver == 's3':
      self.client.download_file(self.bucket, key, str(destination))
    elif self.driver == 'minio':
      self.client.fget_object(self.bucket, key, str(destination))
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")
        
    return destination

  def remove(self, key: str) -> None:
    """
    Remove a file from the storage.
    
    Args:
        key: Key (path) of the file to remove
    """
    if self.driver == 's3':
      self.client.delete_object(Bucket=self.bucket, Key=key)
    elif self.driver == 'minio':
      self.client.remove_object(self.bucket, key)
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")

  def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
    """
    List files in the storage.
    
    Args:
        prefix: Optional prefix to filter files
        
    Returns:
        List of dictionaries containing file information
    """
    self._log(f"Listing files in bucket '{self.bucket}' with prefix '{prefix}'")
    if self.driver == 's3':
      response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
      files = [
        {
          'key': obj['Key'],
          'size': obj['Size'],
          'last_modified': obj['LastModified']
        }
        for obj in response.get('Contents', [])
      ]
    elif self.driver == 'minio':
      try:
        objects = self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
        files = [
          {
            'key': obj.object_name,
            'size': obj.size,
            'last_modified': obj.last_modified
          }
          for obj in objects
        ]
      except Exception as e:
        self._log(f"Minio list error: {str(e)}")
        raise
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")
    
    self._log(f"Found {len(files)} files:")
    for file in files:
      self._log(f"- {file['key']} ({file['size']} bytes)")
    return files

  def exists(self, key: str) -> bool:
    """
    Check if a file exists in the storage.
    
    Args:
        key: Key (path) of the file to check
        
    Returns:
        bool: True if the file exists, False otherwise
    """
    self._log(f"Checking if file exists: bucket={self.bucket}, key={key}")
    
    if self.driver == 's3':
      try:
        self.client.head_object(Bucket=self.bucket, Key=key)
        self._log("File exists in S3")
        return True
      except Exception as e:
        self._log(f"S3 head_object error: {str(e)}")
        return False
    elif self.driver == 'minio':
      try:
        # First check if bucket exists
        if not self.client.bucket_exists(self.bucket):
          self._log(f"Bucket {self.bucket} does not exist")
          return False
          
        # Use stat_object directly - this is more reliable for private buckets
        try:
          self.client.stat_object(self.bucket, key)
          self._log(f"File exists in Minio: {key}")
          return True
        except Exception as e:
          if "NoSuchKey" in str(e):
            self._log(f"File does not exist in Minio: {key}")
            return False
          raise  # Re-raise if it's not a NoSuchKey error
      except Exception as e:
        self._log(f"Minio exists check error: {str(e)}")
        return False
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")

  def get_url(self, key: str, expires: int = 3600) -> str:
    """
    Get a temporary URL for a file.
    
    Args:
        key: Key (path) of the file
        expires: URL expiration time in seconds
        
    Returns:
        str: Temporary URL for the file
        
    Raises:
        FileNotFoundError: If the file does not exist in the bucket
    """
    if not self.exists(key):
      raise FileNotFoundError(f"File not found in bucket: {key}")
      
    try:
      if self.driver == 's3':
        self._log(f"Generating S3 presigned URL for {key} in bucket {self.bucket}")
        url = self.client.generate_presigned_url(
          'get_object',
          Params={
            'Bucket': self.bucket,
            'Key': key,
          },
          ExpiresIn=expires,
          HttpMethod='GET'
        )
        self._log(f"Generated S3 URL: {url}")
        return url
      elif self.driver == 'minio':
        self._log(f"Generating Minio presigned URL for {key} in bucket {self.bucket}")
        url = self.client.presigned_get_object(
          self.bucket, 
          key, 
          expires=timedelta(seconds=expires)
        )
        self._log(f"Generated Minio URL: {url}")
        return url
      else:
        raise ValueError(f"Unsupported driver: {self.driver}")
    except Exception as e:
      self._log(f"Error generating URL: {str(e)}")
      raise
