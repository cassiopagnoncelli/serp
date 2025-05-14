import boto3
from botocore.client import Config
from minio import Minio
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import io
from datetime import timedelta
import shutil
import os

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
    self.bucket = config.get('bucket')
    self.region = config.get('region')
    self.url_endpoint = config['url_endpoint']
    self.access_key = config.get('access_key')
    self.secret_key = config.get('secret_key')
    
    if self.driver != 'local' and not self.bucket:
      raise ValueError("Bucket must be specified in configuration for non-local storage")
    
    if self.driver == 's3':
      self.client = boto3.client(
        's3',
        endpoint_url = config['url_endpoint'],
        aws_access_key_id = config['access_key'],
        aws_secret_access_key = config['secret_key'],
        region_name = self.region,
        config = Config(signature_version='s3v4')
      )
      # Check if the bucket exists
      try:
        self._log(f"Checking if S3 bucket '{self.bucket}' exists...")
        self.client.head_bucket(Bucket=self.bucket)
        self._log(f"S3 bucket '{self.bucket}' exists.")
      except Exception as e:
        self._log(f"S3 bucket '{self.bucket}' does not exist or is not accessible: {str(e)}")
        raise ValueError(f"S3 bucket '{self.bucket}' does not exist or is not accessible. Please create it or check your permissions.")
    elif self.driver == 'minio':
      # Remove protocol and trailing slashes from endpoint
      endpoint = config['url_endpoint'].replace('https://', '').replace('http://', '').rstrip('/')
      self.client = Minio(
        endpoint,
        access_key = config['access_key'],
        secret_key = config['secret_key'],
        secure = True,
        region = self.region,
        http_client = None  # Use default client with timeout
      )
      
      # Set connection timeout - this will prevent long hangs
      if hasattr(self.client._http, '_pool_kwargs'):
        self.client._http._pool_kwargs['timeout'] = 5.0
      
      # Ensure bucket exists
      try:
        if not self.client.bucket_exists(self.bucket):
          self.client.make_bucket(self.bucket)
      except Exception as e:
        self._log(f"Warning: Could not verify bucket existence: {str(e)}")
    elif self.driver == 'local':
      # For local storage, url_endpoint is the base directory
      self.base_path = Path(config['url_endpoint'])
      self.base_path.mkdir(parents=True, exist_ok=True)
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
    self._log(f"Uploading file: {file_path} to key={key}")
    
    if not file_path.exists():
      raise FileNotFoundError(f"File not found: {file_path}")
        
    if self.driver == 's3':
      try:
        self.client.upload_file(str(file_path), self.bucket, key)
        return f"{self.client.meta.endpoint_url}/{self.bucket}/{key}"
      except Exception as e:
        self._log(f"S3 upload error: {str(e)}")
        raise
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
    elif self.driver == 'local':
      dest_path = self.base_path / key
      dest_path.parent.mkdir(parents=True, exist_ok=True)
      shutil.copy2(file_path, dest_path)
      return str(dest_path)
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
    elif self.driver == 'local':
      source_path = self.base_path / key
      if not source_path.exists():
        raise FileNotFoundError(f"File not found: {key}")
      shutil.copy2(source_path, destination)
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
    elif self.driver == 'local':
      file_path = self.base_path / key
      if file_path.exists():
        file_path.unlink()
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
    self._log(f"Listing files with prefix '{prefix}'")
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
    elif self.driver == 'local':
      prefix_path = self.base_path / prefix
      files = []
      for path in prefix_path.rglob('*') if prefix else self.base_path.rglob('*'):
        if path.is_file():
          rel_path = path.relative_to(self.base_path)
          files.append({
            'key': str(rel_path),
            'size': path.stat().st_size,
            'last_modified': path.stat().st_mtime
          })
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
    self._log(f"Checking if file exists: key={key}")
    
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
    elif self.driver == 'local':
      file_path = self.base_path / key
      exists = file_path.exists()
      self._log(f"File {'exists' if exists else 'does not exist'} in local storage: {key}")
      return exists
    else:
      raise ValueError(f"Unsupported driver: {self.driver}")

  def get_url(self, key: str, expires: int = 3600) -> str:
    """
    Get a temporary URL for a file.
    
    Args:
        key: Key (path) of the file
        expires: URL expiration time in seconds (ignored for local storage)
        
    Returns:
        str: Temporary URL for the file
        
    Raises:
        FileNotFoundError: If the file does not exist in the bucket
    """
    if not self.exists(key):
      raise FileNotFoundError(f"File not found: {key}")
      
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
      elif self.driver == 'local':
        # For local storage, return a file:// URL
        file_path = self.base_path / key
        # Convert to absolute path and ensure forward slashes
        abs_path = str(file_path.absolute()).replace('\\', '/')
        # Add file:// prefix
        url = f"file://{abs_path}"
        self._log(f"Generated local file URL: {url}")
        return url
      else:
        raise ValueError(f"Unsupported driver: {self.driver}")
    except Exception as e:
      self._log(f"Error generating URL: {str(e)}")
      raise
