from tabulate import tabulate as t
import importlib
import sys
from typing import Dict, Any, List
from .dns_scanner import DNSScanner, DNSCacheNotFoundError
from .cache import Cache


class AnalysisError(Exception):
    """Custom exception for analysis errors."""
    pass


class Analyzer:
    """Handles analysis and reporting of stale DNS records."""
    
    @staticmethod
    def generate_report(app_config: Dict[str, Any]) -> None:
        """
        Generate a comprehensive stale DNS report.
        
        Args:
            app_config: Application configuration dictionary
        """
        adapters = list(app_config['search-adapters'].keys())

        try:
            dns_keys = DNSScanner.get_data()
        except DNSCacheNotFoundError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
        
        try:
            dns_values = Analyzer._collect_resource_data(adapters)
        except Exception as e:
            print(f"❌ Error collecting resource data: {e}")
            sys.exit(1)
        
        print("📊 Generating stale DNS report...")
        output = Analyzer._build_report_data(dns_keys, dns_values)
        Analyzer._display_report(output)

    @staticmethod
    def _collect_resource_data(adapters: List[str]) -> Dict[str, Dict]:
        """
        Collect resource data from all adapters.
        
        Args:
            adapters: List of adapter names
            
        Returns:
            Combined resource data from all adapters
            
        Raises:
            AnalysisError: If any adapter cache is missing
        """
        dns_values = {}
        missing_adapters = []
        
        for adapter in adapters:
            try:
                lib = importlib.import_module(f"adapters.{adapter}")
                temp = lib.get_data()
                dns_values.update(temp)
            except Exception as e:
                # Check if it's a cache not found error
                if "Cache file not found" in str(e) or "scan-resources" in str(e):
                    missing_adapters.append(adapter)
                else:
                    print(f"Warning: Error loading adapter {adapter}: {e}")
        
        if missing_adapters:
            adapter_list = ", ".join(missing_adapters)
            raise AnalysisError(
                f"Cache files not found for adapters: {adapter_list}\n"
                f"Please run 'python3 app.py scan-resources' first to scan AWS resources."
            )
            
        return dns_values

    @staticmethod
    def _build_report_data(dns_keys: Dict[str, str], dns_values: Dict[str, Dict]) -> Dict[str, List]:
        """
        Build structured report data from DNS and resource data.
        
        Args:
            dns_keys: DNS records data
            dns_values: AWS resource data
            
        Returns:
            Structured report data
        """
        output = {
            "record": [],
            "status": [],
            "type": [],
            "region": [],
            "name": []
        }

        for key in dns_keys:
            value = dns_keys[key]

            if value in dns_values:
                resource_type = dns_values[value]["type"]
                name = dns_values[value]["name"]
                region = dns_values[value]["region"]

                output["record"].append(key)
                output["status"].append("✅")
                output["type"].append(resource_type)
                output["region"].append(region)
                output["name"].append(name)
            else:
                output["record"].append(key)
                output["status"].append("❌")
                output["type"].append("")
                output["region"].append("")
                output["name"].append("")

        return output

    @staticmethod
    def _display_report(output: Dict[str, List]) -> None:
        """
        Display the formatted report.
        
        Args:
            output: Report data to display
        """
        print(t(output, headers="keys"))

    @staticmethod
    def clear_cache(app_config: Dict[str, Any]) -> None:
        """
        Clear all cached data files.
        
        Args:
            app_config: Application configuration dictionary
        """
        adapters = list(app_config['search-adapters'].keys())
        
        print("🧹 Clearing adapter caches...")
        for adapter in adapters:
            try:
                lib = importlib.import_module(f"adapters.{adapter}")
                lib.clear_data()
                print(f"✅ Cleared {adapter} cache")
            except Exception as e:
                print(f"⚠️  Failed to clear {adapter} cache: {e}")
        
        print("🧹 Clearing DNS cache...")
        # Import the module to clear its cache
        from . import dns_scanner
        Cache.clear(dns_scanner.__file__)
        
        print("✅ Cache cleanup completed")
