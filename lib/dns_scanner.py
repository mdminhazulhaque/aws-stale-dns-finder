import boto3
import boto3.session
import re
from typing import Dict, Any, List
from .cache import Cache, CacheNotFoundError


class DNSCacheNotFoundError(Exception):
    """Custom exception for when DNS cache file is not found."""
    pass


class DNSScanner:
    """Handles scanning and processing of Route 53 DNS records."""
    
    @staticmethod
    def scan_records(app_config: Dict[str, Any]) -> None:
        """
        Scan DNS records from Route 53 hosted zone.
        
        Args:
            app_config: Application configuration dictionary
        """
        hostedzoneid = app_config['hostedzone']['hostedzoneid']
        profile = app_config['hostedzone']['profile']
        ignore_key = app_config['hostedzone']['ignore_key']
        ignore_value = app_config['hostedzone']['ignore_value']

        print(f"🔍 Scanning DNS records from {hostedzoneid}")

        session = boto3.session.Session(profile_name=profile)
        route53 = session.client('route53', verify=False)
        records = route53.list_resource_record_sets(
            HostedZoneId=hostedzoneid,
            MaxItems='1000'
        )

        print(f"⚙️  Processing records from {hostedzoneid}")
        data = DNSScanner._process_records(records, ignore_key, ignore_value)
        
        Cache.write(__file__, data)
        print("✅ Done")

    @staticmethod
    def _process_records(records: Dict, ignore_key: str, ignore_value: str) -> Dict[str, str]:
        """
        Process and filter DNS records.
        
        Args:
            records: Raw DNS records from Route 53
            ignore_key: Regex pattern for keys to ignore
            ignore_value: Regex pattern for values to ignore
            
        Returns:
            Processed DNS records dictionary
        """
        data = {}
        
        for record in records['ResourceRecordSets']:
            name = record['Name']
            if re.findall(r'{}'.format(ignore_key), name):
                continue

            if record['Type'] == 'A' or record['Type'] == 'CNAME':
                value = None

                if 'AliasTarget' in record:
                    value = record['AliasTarget']['DNSName']
                else:
                    value = record['ResourceRecords'][0]['Value']

                if re.findall(r'{}'.format(ignore_value), value):
                    continue
                else:
                    data[name] = value.replace("dualstack.", "").rstrip(".")
        
        return data

    @staticmethod
    def get_data() -> Dict[str, str]:
        """
        Retrieve cached DNS data.
        
        Returns:
            Dictionary of DNS records
            
        Raises:
            DNSCacheNotFoundError: If DNS cache file doesn't exist
        """
        try:
            return Cache.read(__file__)
        except CacheNotFoundError as e:
            import os
            base_name = os.path.splitext(os.path.basename(__file__))[0]
            cache_file = os.path.join(os.getcwd(), f"{base_name}.cache.json")
            raise DNSCacheNotFoundError(
                f"❌ DNS cache file not found: {cache_file}\n"
                f"💡 Please run 'python3 app.py scan-dns' first to scan DNS records."
            ) from e
