import json
import os
from typing import Any, Union


class CacheNotFoundError(Exception):
    """Custom exception for when cache files are not found."""
    pass


class Cache:
    """Handles file-based caching operations for the application."""
    
    @staticmethod
    def write(key: Union[str, Any], data: Any) -> None:
        """
        Write data to cache file.
        
        Args:
            key: Cache key (typically __file__ path)
            data: Data to cache
        """
        # Extract filename without extension and create cache file in current working directory
        base_name = os.path.splitext(os.path.basename(str(key)))[0]
        file_path = os.path.join(os.getcwd(), f"{base_name}.cache.json")
        with open(file_path, "w") as fp:
            json.dump(data, fp, indent=4)

    @staticmethod
    def read(key: Union[str, Any]) -> Any:
        """
        Read data from cache file.
        
        Args:
            key: Cache key (typically __file__ path)
            
        Returns:
            Cached data
            
        Raises:
            CacheNotFoundError: If cache file doesn't exist
        """
        # Extract filename without extension and look for cache file in current working directory
        base_name = os.path.splitext(os.path.basename(str(key)))[0]
        file_path = os.path.join(os.getcwd(), f"{base_name}.cache.json")
        if not os.path.exists(file_path):
            raise CacheNotFoundError(f"Cache file not found: {file_path}")
        
        try:
            with open(file_path, "r") as fp:
                return json.load(fp)
        except json.JSONDecodeError as e:
            raise CacheNotFoundError(f"Invalid cache file format: {file_path}") from e
        except Exception as e:
            raise CacheNotFoundError(f"Error reading cache file: {file_path}") from e

    @staticmethod
    def clear(key: Union[str, Any]) -> bool:
        """
        Clear specific cache file.
        
        Args:
            key: Cache key (typically __file__ path)
            
        Returns:
            True if file was deleted, False if file didn't exist
        """
        # Extract filename without extension and look for cache file in current working directory
        base_name = os.path.splitext(os.path.basename(str(key)))[0]
        file_path = os.path.join(os.getcwd(), f"{base_name}.cache.json")
        try:
            os.remove(file_path)
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def clear_file(file_path: str) -> bool:
        """
        Clear cache file by direct file path.
        
        Args:
            file_path: Direct path to cache file
            
        Returns:
            True if file was deleted, False if file didn't exist
        """
        cache_path = f"{file_path}.json"
        try:
            os.remove(cache_path)
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def exists(key: Union[str, Any]) -> bool:
        """
        Check if cache file exists.
        
        Args:
            key: Cache key (typically __file__ path)
            
        Returns:
            True if cache file exists, False otherwise
        """
        file_path = f"{key}.json"
        return os.path.exists(file_path)

    @staticmethod
    def clear_all(pattern: str = "*.json") -> int:
        """
        Clear all cache files matching pattern.
        
        Args:
            pattern: File pattern to match (default: "*.json")
            
        Returns:
            Number of files deleted
        """
        import glob
        
        files = glob.glob(pattern)
        count = 0
        
        for file_path in files:
            try:
                os.remove(file_path)
                count += 1
            except OSError:
                pass
                
        return count
