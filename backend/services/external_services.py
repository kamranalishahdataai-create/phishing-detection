"""
External Services Integration
Google Safe Browsing, Domain Age, WHOIS, and other external APIs
"""

import asyncio
import hashlib
import base64
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import socket

import httpx
from loguru import logger

try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False
    logger.warning("python-whois not installed. Domain age checks disabled.")

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    logger.warning("dnspython not installed. DNS checks disabled.")

from config.settings import settings


@dataclass
class SafeBrowsingResult:
    """Google Safe Browsing check result"""
    url: str
    is_malicious: bool
    threats: List[str]
    checked_at: datetime
    

@dataclass
class DomainAgeResult:
    """Domain age check result"""
    domain: str
    creation_date: Optional[datetime]
    age_days: Optional[int]
    is_new_domain: bool
    registrar: Optional[str]
    checked_at: datetime


@dataclass
class DNSCheckResult:
    """DNS check result"""
    domain: str
    has_a_record: bool
    has_mx_record: bool
    has_spf_record: bool
    ip_addresses: List[str]
    checked_at: datetime


class GoogleSafeBrowsingService:
    """
    Google Safe Browsing API integration.
    Checks URLs against Google's threat database.
    """
    
    API_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    
    THREAT_TYPES = [
        "MALWARE",
        "SOCIAL_ENGINEERING",
        "UNWANTED_SOFTWARE",
        "POTENTIALLY_HARMFUL_APPLICATION",
    ]
    
    PLATFORM_TYPES = ["ANY_PLATFORM"]
    THREAT_ENTRY_TYPES = ["URL"]
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_SAFE_BROWSING_API_KEY
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.warning("Google Safe Browsing API key not configured")
    
    async def check_url(self, url: str) -> SafeBrowsingResult:
        """
        Check a single URL against Google Safe Browsing.
        
        Args:
            url: URL to check
            
        Returns:
            SafeBrowsingResult with threat information
        """
        if not self.enabled:
            return SafeBrowsingResult(
                url=url,
                is_malicious=False,
                threats=[],
                checked_at=datetime.utcnow(),
            )
        
        return await self.check_urls([url])[0]
    
    async def check_urls(self, urls: List[str]) -> List[SafeBrowsingResult]:
        """
        Check multiple URLs against Google Safe Browsing.
        
        Args:
            urls: List of URLs to check
            
        Returns:
            List of SafeBrowsingResult
        """
        if not self.enabled:
            return [
                SafeBrowsingResult(
                    url=url,
                    is_malicious=False,
                    threats=[],
                    checked_at=datetime.utcnow(),
                )
                for url in urls
            ]
        
        try:
            request_body = {
                "client": {
                    "clientId": "phishing-detection-tool",
                    "clientVersion": settings.APP_VERSION,
                },
                "threatInfo": {
                    "threatTypes": self.THREAT_TYPES,
                    "platformTypes": self.PLATFORM_TYPES,
                    "threatEntryTypes": self.THREAT_ENTRY_TYPES,
                    "threatEntries": [{"url": url} for url in urls],
                },
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.API_URL}?key={self.api_key}",
                    json=request_body,
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
            
            # Process matches
            matches = data.get("matches", [])
            url_threats = {url: [] for url in urls}
            
            for match in matches:
                threat_url = match.get("threat", {}).get("url")
                threat_type = match.get("threatType")
                if threat_url and threat_type:
                    url_threats[threat_url].append(threat_type)
            
            # Build results
            results = []
            for url in urls:
                threats = url_threats.get(url, [])
                results.append(SafeBrowsingResult(
                    url=url,
                    is_malicious=len(threats) > 0,
                    threats=threats,
                    checked_at=datetime.utcnow(),
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Google Safe Browsing API error: {e}")
            # Return safe results on error (fail open)
            return [
                SafeBrowsingResult(
                    url=url,
                    is_malicious=False,
                    threats=[],
                    checked_at=datetime.utcnow(),
                )
                for url in urls
            ]


class DomainAgeService:
    """
    Domain age checking service using WHOIS.
    Newer domains are more likely to be phishing sites.
    """
    
    def __init__(self):
        self.enabled = WHOIS_AVAILABLE
        
        if not self.enabled:
            logger.warning("WHOIS not available. Install python-whois.")
    
    def check_domain_age(self, domain: str) -> DomainAgeResult:
        """
        Check domain age using WHOIS lookup.
        
        Args:
            domain: Domain to check (without protocol)
            
        Returns:
            DomainAgeResult with age information
        """
        if not self.enabled:
            return DomainAgeResult(
                domain=domain,
                creation_date=None,
                age_days=None,
                is_new_domain=False,
                registrar=None,
                checked_at=datetime.utcnow(),
            )
        
        try:
            w = whois.whois(domain)
            
            # Get creation date
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            # Calculate age
            age_days = None
            is_new_domain = False
            
            if creation_date:
                if isinstance(creation_date, datetime):
                    age_days = (datetime.utcnow() - creation_date).days
                    is_new_domain = age_days < settings.MIN_DOMAIN_AGE_DAYS
            
            # Get registrar
            registrar = w.registrar
            if isinstance(registrar, list):
                registrar = registrar[0]
            
            return DomainAgeResult(
                domain=domain,
                creation_date=creation_date,
                age_days=age_days,
                is_new_domain=is_new_domain,
                registrar=registrar,
                checked_at=datetime.utcnow(),
            )
            
        except Exception as e:
            logger.warning(f"WHOIS lookup failed for {domain}: {e}")
            return DomainAgeResult(
                domain=domain,
                creation_date=None,
                age_days=None,
                is_new_domain=False,
                registrar=None,
                checked_at=datetime.utcnow(),
            )


class DNSCheckService:
    """
    DNS checking service.
    Validates domain DNS records.
    """
    
    def __init__(self):
        self.enabled = DNS_AVAILABLE
        
        if not self.enabled:
            logger.warning("DNS resolver not available. Install dnspython.")
    
    async def check_domain(self, domain: str) -> DNSCheckResult:
        """
        Check DNS records for a domain.
        
        Args:
            domain: Domain to check
            
        Returns:
            DNSCheckResult with DNS information
        """
        has_a = False
        has_mx = False
        has_spf = False
        ip_addresses = []
        
        if not self.enabled:
            return DNSCheckResult(
                domain=domain,
                has_a_record=False,
                has_mx_record=False,
                has_spf_record=False,
                ip_addresses=[],
                checked_at=datetime.utcnow(),
            )
        
        try:
            # Check A records
            try:
                answers = dns.resolver.resolve(domain, 'A')
                has_a = True
                ip_addresses = [str(rdata) for rdata in answers]
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                pass
            
            # Check MX records
            try:
                dns.resolver.resolve(domain, 'MX')
                has_mx = True
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                pass
            
            # Check SPF (TXT records)
            try:
                answers = dns.resolver.resolve(domain, 'TXT')
                for rdata in answers:
                    if 'v=spf1' in str(rdata):
                        has_spf = True
                        break
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                pass
                
        except Exception as e:
            logger.warning(f"DNS check failed for {domain}: {e}")
        
        return DNSCheckResult(
            domain=domain,
            has_a_record=has_a,
            has_mx_record=has_mx,
            has_spf_record=has_spf,
            ip_addresses=ip_addresses,
            checked_at=datetime.utcnow(),
        )


class VirusTotalService:
    """
    VirusTotal API integration (optional).
    """
    
    API_URL = "https://www.virustotal.com/api/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.VIRUSTOTAL_API_KEY
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.info("VirusTotal API key not configured")
    
    async def check_url(self, url: str) -> Dict:
        """
        Check URL against VirusTotal.
        
        Args:
            url: URL to check
            
        Returns:
            VirusTotal scan results
        """
        if not self.enabled:
            return {"enabled": False}
        
        try:
            # URL needs to be base64 encoded
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.API_URL}/urls/{url_id}",
                    headers={"x-apikey": self.api_key},
                    timeout=10.0,
                )
                
                if response.status_code == 404:
                    # URL not in database, submit for scanning
                    return {"status": "not_found", "url": url}
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"VirusTotal API error: {e}")
            return {"error": str(e)}


class ExternalServicesManager:
    """
    Manager for all external services.
    Provides unified interface for external checks.
    """
    
    def __init__(self):
        self.safe_browsing = GoogleSafeBrowsingService()
        self.domain_age = DomainAgeService()
        self.dns_check = DNSCheckService()
        self.virustotal = VirusTotalService()
    
    async def comprehensive_check(self, url: str, domain: str) -> Dict:
        """
        Perform comprehensive external checks.
        
        Args:
            url: Full URL to check
            domain: Domain extracted from URL
            
        Returns:
            Dictionary with all check results
        """
        results = {
            'safe_browsing': None,
            'domain_age': None,
            'dns': None,
            'virustotal': None,
        }
        
        # Run checks concurrently
        try:
            safe_browsing_result = await self.safe_browsing.check_url(url)
            results['safe_browsing'] = {
                'is_malicious': safe_browsing_result.is_malicious,
                'threats': safe_browsing_result.threats,
            }
        except Exception as e:
            logger.error(f"Safe browsing check failed: {e}")
        
        try:
            domain_age_result = self.domain_age.check_domain_age(domain)
            results['domain_age'] = {
                'age_days': domain_age_result.age_days,
                'is_new_domain': domain_age_result.is_new_domain,
                'registrar': domain_age_result.registrar,
            }
        except Exception as e:
            logger.error(f"Domain age check failed: {e}")
        
        try:
            dns_result = await self.dns_check.check_domain(domain)
            results['dns'] = {
                'has_a_record': dns_result.has_a_record,
                'has_mx_record': dns_result.has_mx_record,
                'ip_addresses': dns_result.ip_addresses,
            }
        except Exception as e:
            logger.error(f"DNS check failed: {e}")
        
        return results
    
    def calculate_risk_adjustment(self, check_results: Dict) -> float:
        """
        Calculate risk adjustment based on external checks.
        
        Returns value between -0.3 and +0.3 to adjust phishing probability.
        """
        adjustment = 0.0
        
        # Safe browsing flags
        if check_results.get('safe_browsing', {}).get('is_malicious'):
            adjustment += 0.3  # Strong indicator of phishing
        
        # Domain age
        domain_age = check_results.get('domain_age', {})
        if domain_age.get('is_new_domain'):
            adjustment += 0.15  # New domains are riskier
        elif domain_age.get('age_days', 0) > 365:
            adjustment -= 0.1  # Older domains are safer
        
        # DNS checks
        dns = check_results.get('dns', {})
        if not dns.get('has_a_record'):
            adjustment += 0.1  # No A record is suspicious
        if dns.get('has_mx_record') and dns.get('has_spf_record'):
            adjustment -= 0.05  # Proper email setup indicates legitimacy
        
        return max(-0.3, min(0.3, adjustment))


# Singleton instance
external_services = ExternalServicesManager()
