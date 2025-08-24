"""
AWS Service Adapters Package

This package contains adapters for various AWS services to scan
resources and collect DNS-related information.
"""

from .base_adapter import BaseAdapter, AdapterCacheNotFoundError
from .ec2 import EC2Adapter
from .elbv2 import ELBv2Adapter
from .globalaccelerator import GlobalAcceleratorAdapter
from .lightsail import LightsailAdapter

__all__ = [
    'BaseAdapter',
    'AdapterCacheNotFoundError',
    'EC2Adapter', 
    'ELBv2Adapter',
    'GlobalAcceleratorAdapter',
    'LightsailAdapter'
]
