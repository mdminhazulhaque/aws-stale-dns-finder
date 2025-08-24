import os
import json
import glob
import tempfile
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import boto3


class AdapterCacheNotFoundError(Exception):
    """Custom exception for when adapter cache files are not found."""
    pass


class BaseAdapter(ABC):
    """
    Abstract base class for AWS service adapters.
    
    Provides common functionality for caching and AWS resource discovery.
    All concrete adapters must implement the abstract methods.
    """
    
    def __init__(self):
        """Initialize the adapter with cache file path."""
        self._cache_file = None
    
    @property
    def cache_file(self) -> str:
        """Get the cache file path for this adapter."""
        if self._cache_file is None:
            # Create cache file in current working directory
            adapter_name = self.__class__.__name__.lower().replace('adapter', '')
            self._cache_file = os.path.join(os.getcwd(), f"{adapter_name}.cache.json")
        return self._cache_file
    
    @abstractmethod
    def get_service_name(self) -> str:
        """
        Return the AWS service name for this adapter.
        
        Returns:
            AWS service name (e.g., 'ec2', 'elbv2', etc.)
        """
        pass
    
    @abstractmethod
    def scan_resources(self, client: Any, region: str) -> Dict[str, Dict[str, Any]]:
        """
        Scan resources for a specific AWS service in a region.
        
        Args:
            client: Boto3 client for the AWS service
            region: AWS region name
            
        Returns:
            Dictionary mapping resource endpoints to resource info
        """
        pass
    
    def do_search(self, sessions: List[boto3.session.Session], regions: List[str]) -> None:
        """
        Search for resources across multiple sessions and regions.
        
        Args:
            sessions: List of boto3 sessions (different AWS accounts)
            regions: List of AWS regions to search
        """
        data = {}
        service_name = self.get_service_name()
        
        # Get account ID from the first session for cache naming
        account_id = "unknown"
        if sessions:
            try:
                sts_client = sessions[0].client('sts')
                account_id = sts_client.get_caller_identity()['Account']
            except Exception:
                # Fallback to unknown if we can't get account ID
                pass
        
        for session in sessions:
            for region in regions:
                try:
                    client = session.client(service_name, verify=False, region_name=region)
                    region_data = self.scan_resources(client, region)
                    data.update(region_data)
                except Exception as e:
                    print(f"❌ Error scanning {service_name} in {region}: {e}")
                    continue
        
        self.write_cache(data, account_id)
    
    def write_cache(self, data: Dict[str, Any], account_id: str = None) -> None:
        """
        Write data to cache file in current working directory.
        
        Args:
            data: Data to cache
            account_id: AWS account ID for cache naming
        """
        try:
            if account_id:
                adapter_name = self.__class__.__name__.lower().replace('adapter', '')
                from lib.cache import Cache
                Cache.write_with_id(adapter_name, account_id, data)
            else:
                # Fallback to old method
                with open(self.cache_file, 'w') as fp:
                    json.dump(data, fp, indent=4)
        except Exception as e:
            cache_file = self.cache_file if not account_id else f"{self.__class__.__name__.lower().replace('adapter', '')}.{account_id}.cache.json"
            print(f"❌ Error writing cache to {cache_file}: {e}")
    
    def read_cache(self) -> Dict[str, Any]:
        """
        Read data from cache file.
        
        Returns:
            Cached data dictionary
            
        Raises:
            AdapterCacheNotFoundError: If cache file doesn't exist
        """
        # For reading, we need to find the cache file by pattern since we don't know the account ID
        adapter_name = self.__class__.__name__.lower().replace('adapter', '')
        
        # Try account-specific cache files first
        pattern = os.path.join(os.getcwd(), f"{adapter_name}.*.cache.json")
        matching_files = glob.glob(pattern)
        
        # If no account-specific files, try the old format
        if not matching_files:
            old_pattern = os.path.join(os.getcwd(), f"{adapter_name}.cache.json")
            matching_files = glob.glob(old_pattern)
        
        if matching_files:
            # Use the first matching file
            cache_file = matching_files[0]
            try:
                with open(cache_file, 'r') as fp:
                    return json.load(fp)
            except json.JSONDecodeError as e:
                raise AdapterCacheNotFoundError(f"❌ Invalid cache file format: {cache_file}") from e
            except Exception as e:
                raise AdapterCacheNotFoundError(f"❌ Error reading cache file: {cache_file}") from e
        else:
            # No cache files found
            adapter_name = self.get_service_name()
            raise AdapterCacheNotFoundError(
                f"❌ Cache file not found for {adapter_name} adapter\n"
                f"💡 Please run 'python3 app.py scan-resources' first to scan AWS resources."
            )
    
    def clear_cache(self) -> bool:
        """
        Clear the cache file.
        
        Returns:
            True if file was deleted, False if file didn't exist
        """
        # Clear all cache files for this adapter (across all accounts)
        import glob
        adapter_name = self.__class__.__name__.lower().replace('adapter', '')
        pattern = os.path.join(os.getcwd(), f"{adapter_name}.*.cache.json")
        matching_files = glob.glob(pattern)
        
        deleted_any = False
        for cache_file in matching_files:
            try:
                os.remove(cache_file)
                deleted_any = True
            except Exception as e:
                print(f"❌ Error clearing cache {cache_file}: {e}")
        
        return deleted_any
    
    def cache_exists(self) -> bool:
        """
        Check if cache file exists.
        
        Returns:
            True if cache file exists, False otherwise
        """
        return os.path.exists(self.cache_file)
    
    # Legacy methods for backward compatibility
    def get_data(self) -> Dict[str, Any]:
        """Legacy method for getting cached data."""
        return self.read_cache()
    
    def clear_data(self) -> bool:
        """Legacy method for clearing cached data."""
        return self.clear_cache()
    
    @staticmethod
    def find_name_tag(tags: List[Dict[str, str]]) -> str:
        """
        Utility method to find Name tag in AWS resource tags.
        
        Args:
            tags: List of tag dictionaries
            
        Returns:
            Name tag value or None if not found
        """
        if not tags:
            return None
            
        for tag in tags:
            if tag.get("Key") == "Name":
                return tag.get("Value")
        return None
