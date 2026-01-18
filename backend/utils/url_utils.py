"""
Utility functions for the phishing detection backend
"""

import hashlib
import re
from typing import Optional, List
from urllib.parse import urlparse
import tldextract


def normalize_url(url: str) -> str:
    """
    Normalize URL for consistent processing.
    
    Args:
        url: Raw URL string
        
    Returns:
        Normalized URL
    """
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    # Convert to lowercase (domain part only)
    parsed = urlparse(url)
    if parsed.netloc:
        normalized = f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        if parsed.fragment:
            normalized += f"#{parsed.fragment}"
        return normalized
    
    return url.lower()


def get_url_hash(url: str) -> str:
    """
    Generate consistent SHA256 hash for URL.
    
    Args:
        url: URL to hash
        
    Returns:
        64-character hex string
    """
    normalized = normalize_url(url)
    return hashlib.sha256(normalized.encode()).hexdigest()


def extract_domain(url: str) -> str:
    """
    Extract registered domain from URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Registered domain (e.g., "google.com")
    """
    extracted = tldextract.extract(url)
    if extracted.suffix:
        return f"{extracted.domain}.{extracted.suffix}"
    return extracted.domain


def extract_full_hostname(url: str) -> str:
    """
    Extract full hostname including subdomains.
    
    Args:
        url: URL to extract hostname from
        
    Returns:
        Full hostname
    """
    parsed = urlparse(normalize_url(url))
    return parsed.netloc or ""


def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL
    """
    try:
        url = normalize_url(url)
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False


def is_ip_address(hostname: str) -> bool:
    """
    Check if hostname is an IP address.
    
    Args:
        hostname: Hostname to check
        
    Returns:
        True if IP address
    """
    # IPv4 pattern
    ipv4_pattern = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    
    # IPv6 pattern (simplified)
    ipv6_pattern = re.compile(r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$')
    
    return bool(ipv4_pattern.match(hostname) or ipv6_pattern.match(hostname))


def clean_url_for_display(url: str, max_length: int = 100) -> str:
    """
    Clean and truncate URL for display.
    
    Args:
        url: URL to clean
        max_length: Maximum length
        
    Returns:
        Cleaned URL string
    """
    url = url.strip()
    
    if len(url) <= max_length:
        return url
    
    return url[:max_length - 3] + "..."


def split_url_parts(url: str) -> dict:
    """
    Split URL into components.
    
    Args:
        url: URL to split
        
    Returns:
        Dictionary with URL components
    """
    url = normalize_url(url)
    parsed = urlparse(url)
    extracted = tldextract.extract(url)
    
    return {
        'scheme': parsed.scheme,
        'hostname': parsed.hostname,
        'port': parsed.port,
        'path': parsed.path,
        'query': parsed.query,
        'fragment': parsed.fragment,
        'subdomain': extracted.subdomain,
        'domain': extracted.domain,
        'suffix': extracted.suffix,
        'registered_domain': extracted.registered_domain,
    }


def batch_urls(urls: List[str], batch_size: int = 32) -> List[List[str]]:
    """
    Split URLs into batches.
    
    Args:
        urls: List of URLs
        batch_size: Size of each batch
        
    Returns:
        List of URL batches
    """
    return [urls[i:i + batch_size] for i in range(0, len(urls), batch_size)]
