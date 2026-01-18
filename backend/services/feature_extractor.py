"""
URL Feature Extractor
Extracts various features from URLs for phishing detection
"""

import re
import math
import socket
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs, unquote
from collections import Counter
from dataclasses import dataclass, asdict

import tldextract


@dataclass
class URLFeatures:
    """Data class containing all extracted URL features"""
    
    # Basic features
    url: str
    length: int
    entropy: float
    
    # Character counts
    digits: int
    letters: int
    special_chars: int
    uppercase: int
    lowercase: int
    
    # Ratios
    digit_ratio: float
    letter_ratio: float
    special_char_ratio: float
    
    # URL structure
    has_ip: int
    has_punycode: int
    has_encoded: int
    num_subdomains: int
    path_length: int
    query_length: int
    fragment_length: int
    
    # Domain info
    domain: str
    subdomain: str
    suffix: str
    full_domain: str
    
    # Additional features
    num_dots: int
    num_hyphens: int
    num_underscores: int
    num_slashes: int
    num_at_symbols: int
    num_params: int
    has_https: int
    has_www: int
    
    # Suspicious patterns
    has_suspicious_port: int
    has_double_slash_redirect: int
    domain_in_path: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


class URLFeatureExtractor:
    """Extracts features from URLs for phishing detection"""
    
    # IP address pattern (IPv4)
    IP_PATTERN = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    
    # Hex encoded pattern
    HEX_PATTERN = re.compile(r'%[0-9a-fA-F]{2}')
    
    # Punycode pattern
    PUNYCODE_PATTERN = re.compile(r'xn--')
    
    # Standard ports
    STANDARD_PORTS = {80, 443, 8080}
    
    # Common TLDs for brands (for domain_in_path detection)
    COMMON_BRAND_DOMAINS = {
        'google', 'facebook', 'apple', 'microsoft', 'amazon',
        'paypal', 'ebay', 'netflix', 'instagram', 'twitter',
        'linkedin', 'yahoo', 'outlook', 'banking', 'bank'
    }
    
    def __init__(self):
        self.tld_extractor = tldextract.TLDExtract(cache_dir=None)
    
    def extract_features(self, url: str) -> URLFeatures:
        """
        Extract all features from a URL
        
        Args:
            url: The URL to analyze
            
        Returns:
            URLFeatures dataclass with all extracted features
        """
        # Normalize URL
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Parse URL components
        parsed = urlparse(url)
        extracted = self.tld_extractor(url)
        
        # Basic features
        length = len(url)
        entropy = self._calculate_entropy(url)
        
        # Character analysis
        chars = self._analyze_characters(url)
        
        # URL structure analysis
        structure = self._analyze_structure(parsed, extracted)
        
        # Domain info
        domain_info = self._extract_domain_info(extracted)
        
        # Additional features
        additional = self._extract_additional_features(url, parsed)
        
        # Suspicious patterns
        suspicious = self._detect_suspicious_patterns(url, parsed, extracted)
        
        return URLFeatures(
            url=url,
            length=length,
            entropy=entropy,
            
            # Character counts
            digits=chars['digits'],
            letters=chars['letters'],
            special_chars=chars['special'],
            uppercase=chars['uppercase'],
            lowercase=chars['lowercase'],
            
            # Ratios
            digit_ratio=chars['digit_ratio'],
            letter_ratio=chars['letter_ratio'],
            special_char_ratio=chars['special_ratio'],
            
            # URL structure
            has_ip=structure['has_ip'],
            has_punycode=structure['has_punycode'],
            has_encoded=structure['has_encoded'],
            num_subdomains=structure['num_subdomains'],
            path_length=structure['path_length'],
            query_length=structure['query_length'],
            fragment_length=structure['fragment_length'],
            
            # Domain info
            domain=domain_info['domain'],
            subdomain=domain_info['subdomain'],
            suffix=domain_info['suffix'],
            full_domain=domain_info['full_domain'],
            
            # Additional features
            num_dots=additional['num_dots'],
            num_hyphens=additional['num_hyphens'],
            num_underscores=additional['num_underscores'],
            num_slashes=additional['num_slashes'],
            num_at_symbols=additional['num_at'],
            num_params=additional['num_params'],
            has_https=additional['has_https'],
            has_www=additional['has_www'],
            
            # Suspicious patterns
            has_suspicious_port=suspicious['suspicious_port'],
            has_double_slash_redirect=suspicious['double_slash_redirect'],
            domain_in_path=suspicious['domain_in_path'],
        )
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string"""
        if not text:
            return 0.0
        
        counter = Counter(text.lower())
        length = len(text)
        
        entropy = 0.0
        for count in counter.values():
            if count > 0:
                prob = count / length
                entropy -= prob * math.log2(prob)
        
        return round(entropy, 6)
    
    def _analyze_characters(self, url: str) -> Dict:
        """Analyze character composition of URL"""
        url_lower = url.lower()
        length = len(url) if url else 1
        
        digits = sum(1 for c in url if c.isdigit())
        letters = sum(1 for c in url if c.isalpha())
        uppercase = sum(1 for c in url if c.isupper())
        lowercase = sum(1 for c in url if c.islower())
        special = sum(1 for c in url if not c.isalnum())
        
        return {
            'digits': digits,
            'letters': letters,
            'uppercase': uppercase,
            'lowercase': lowercase,
            'special': special,
            'digit_ratio': round(digits / length, 4),
            'letter_ratio': round(letters / length, 4),
            'special_ratio': round(special / length, 4),
        }
    
    def _analyze_structure(self, parsed, extracted) -> Dict:
        """Analyze URL structure"""
        hostname = parsed.hostname or ''
        
        # Check for IP address
        has_ip = 1 if self.IP_PATTERN.match(hostname) else 0
        
        # Check for punycode (IDN)
        has_punycode = 1 if self.PUNYCODE_PATTERN.search(hostname) else 0
        
        # Check for URL encoding
        has_encoded = 1 if self.HEX_PATTERN.search(parsed.path + parsed.query) else 0
        
        # Count subdomains
        subdomain = extracted.subdomain
        num_subdomains = len(subdomain.split('.')) if subdomain else 0
        
        return {
            'has_ip': has_ip,
            'has_punycode': has_punycode,
            'has_encoded': has_encoded,
            'num_subdomains': num_subdomains,
            'path_length': len(parsed.path),
            'query_length': len(parsed.query),
            'fragment_length': len(parsed.fragment),
        }
    
    def _extract_domain_info(self, extracted) -> Dict:
        """Extract domain information"""
        domain = extracted.domain or ''
        subdomain = extracted.subdomain or ''
        suffix = extracted.suffix or ''
        
        # Full registered domain
        full_domain = extracted.registered_domain or f"{domain}.{suffix}"
        
        return {
            'domain': domain,
            'subdomain': subdomain,
            'suffix': suffix,
            'full_domain': full_domain,
        }
    
    def _extract_additional_features(self, url: str, parsed) -> Dict:
        """Extract additional URL features"""
        # Count special characters
        num_dots = url.count('.')
        num_hyphens = url.count('-')
        num_underscores = url.count('_')
        num_slashes = url.count('/')
        num_at = url.count('@')
        
        # Count query parameters
        params = parse_qs(parsed.query)
        num_params = len(params)
        
        # Protocol and www
        has_https = 1 if parsed.scheme == 'https' else 0
        has_www = 1 if (parsed.hostname or '').startswith('www.') else 0
        
        return {
            'num_dots': num_dots,
            'num_hyphens': num_hyphens,
            'num_underscores': num_underscores,
            'num_slashes': num_slashes,
            'num_at': num_at,
            'num_params': num_params,
            'has_https': has_https,
            'has_www': has_www,
        }
    
    def _detect_suspicious_patterns(self, url: str, parsed, extracted) -> Dict:
        """Detect suspicious patterns in URL"""
        # Check for suspicious port
        suspicious_port = 0
        if parsed.port and parsed.port not in self.STANDARD_PORTS:
            suspicious_port = 1
        
        # Check for double slash redirect (http://legitimate.com//http://evil.com)
        double_slash_redirect = 1 if '//' in parsed.path else 0
        
        # Check if common brand domain appears in path (potential phishing)
        domain_in_path = 0
        path_lower = parsed.path.lower()
        for brand in self.COMMON_BRAND_DOMAINS:
            if brand in path_lower and brand not in (extracted.domain or '').lower():
                domain_in_path = 1
                break
        
        return {
            'suspicious_port': suspicious_port,
            'double_slash_redirect': double_slash_redirect,
            'domain_in_path': domain_in_path,
        }
    
    def extract_lgbm_features(self, url: str) -> List[float]:
        """
        Extract features in the format expected by the LightGBM model
        Based on the training data columns from test_with_probs.csv
        
        Features: length, entropy, digits, special_chars, has_ip, 
                  url_len, url_entropy, letters, has_punycode, has_encoded, 
                  num_subdomains, and additional computed features
        """
        features = self.extract_features(url)
        
        # Return features in order expected by LGBM model
        # Based on analysis of the model's feature_names
        return [
            features.length,           # Column_0: length
            features.entropy,          # Column_1: entropy  
            features.digits,           # Column_2: digits
            features.special_chars,    # Column_3: special_chars
            features.has_ip,           # Column_4: has_ip
            features.length,           # Column_5: url_len (same as length)
            features.entropy,          # Column_6: url_entropy (same as entropy)
            features.letters,          # Column_7: letters
            features.has_punycode,     # Column_8: has_punycode
            features.has_encoded,      # Column_9: has_encoded
            features.num_subdomains,   # Column_10: num_subdomains
            features.path_length,      # Column_11: additional feature
        ]
    
    def extract_batch_lgbm_features(self, urls: List[str]) -> List[List[float]]:
        """Extract LightGBM features for a batch of URLs"""
        return [self.extract_lgbm_features(url) for url in urls]


# Singleton instance
url_feature_extractor = URLFeatureExtractor()
