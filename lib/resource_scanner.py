import importlib
import boto3
from typing import Dict, Any, List


class ResourceScanner:
    """Handles scanning of AWS resources across multiple services and accounts."""
    
    @staticmethod
    def scan_resources(app_config: Dict[str, Any]) -> None:
        """
        Scan AWS resources across multiple profiles, regions, and services.
        
        Args:
            app_config: Application configuration dictionary
        """
        profiles = list(app_config['search-profiles'].keys())
        regions = list(app_config['search-regions'].keys())
        adapters = list(app_config['search-adapters'].keys())

        print("🌐 Scanning AWS resources across accounts and regions")

        sessions = ResourceScanner._create_sessions(profiles)

        for adapter in adapters:
            print(f"🔌 Loading adapter {adapter}")
            lib = importlib.import_module(f"adapters.{adapter}")
            lib.do_search(sessions, regions)

    @staticmethod
    def _create_sessions(profiles: List[str]) -> List[boto3.session.Session]:
        """
        Create boto3 sessions for multiple AWS profiles.
        
        Args:
            profiles: List of AWS profile names
            
        Returns:
            List of boto3 sessions
        """
        return [boto3.session.Session(profile_name=profile) for profile in profiles]
