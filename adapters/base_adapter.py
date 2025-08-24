import os
import json
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
        
        for session in sessions:
            for region in regions:
                try:
                    client = session.client(service_name, verify=False, region_name=region)
                    region_data = self.scan_resources(client, region)
                    data.update(region_data)
                except Exception as e:
                    print(f"❌ Error scanning {service_name} in {region}: {e}")
                    continue
        
        self.write_cache(data)
    
    def write_cache(self, data: Dict[str, Any]) -> None:
        """
        Write data to cache file in current working directory.
        
        Args:
            data: Data to cache
        """
        try:
            with open(self.cache_file, 'w') as fp:
                json.dump(data, fp, indent=4)
        except Exception as e:
            print(f"❌ Error writing cache to {self.cache_file}: {e}")
    
    def read_cache(self) -> Dict[str, Any]:
        """
        Read data from cache file.
        
        Returns:
            Cached data dictionary
            
        Raises:
            AdapterCacheNotFoundError: If cache file doesn't exist
        """
        if not os.path.exists(self.cache_file):
            adapter_name = self.get_service_name()
            raise AdapterCacheNotFoundError(
                f"❌ Cache file not found for {adapter_name} adapter: {self.cache_file}\n"
                f"💡 Please run 'python3 app.py scan-resources' first to scan AWS resources."
            )
        
        try:
            with open(self.cache_file, 'r') as fp:
                return json.load(fp)
        except json.JSONDecodeError as e:
            raise AdapterCacheNotFoundError(f"❌ Invalid cache file format: {self.cache_file}") from e
        except Exception as e:
            raise AdapterCacheNotFoundError(f"❌ Error reading cache file: {self.cache_file}") from e
    
    def clear_cache(self) -> bool:
        """
        Clear the cache file.
        
        Returns:
            True if file was deleted, False if file didn't exist
        """
        try:
            os.remove(self.cache_file)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"❌ Error clearing cache {self.cache_file}: {e}")
            return False
    
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
