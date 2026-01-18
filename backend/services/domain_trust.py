"""
Domain Trust System
Evaluates domain trustworthiness using multiple signals:
- Trusted domain databases (high/medium/low trust levels)
- Keyword detection in domain names
- Government and educational domain detection
- TLD analysis
- Domain popularity checking
"""

import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import tldextract
from loguru import logger

from backend.config.constants import (
    HIGH_TRUST_DOMAINS,
    MEDIUM_TRUST_DOMAINS,
    GOVERNMENT_TLD_PATTERNS,
    GOVERNMENT_DOMAINS,
    HIGH_TRUST_KEYWORDS,
    MEDIUM_TRUST_KEYWORDS,
    SUSPICIOUS_KEYWORDS,
    PHISHING_TLD_PATTERNS,
    PHISHING_SUBSTRINGS,
    TOP_1K_DOMAINS_SAMPLE,
    TRUST_LEVELS,
)


class TrustLevel(Enum):
    """Trust level enumeration"""
    HIGHEST = "highest"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"


@dataclass
class TrustEvaluation:
    """Result of domain trust evaluation"""
    domain: str
    full_domain: str
    trust_level: TrustLevel
    trust_score: float
    confidence: float
    reasons: List[str]
    is_government: bool
    is_educational: bool
    keyword_matches: List[str]
    suspicious_patterns: List[str]
    recommendation: str
    
    def to_dict(self) -> Dict:
        return {
            'domain': self.domain,
            'full_domain': self.full_domain,
            'trust_level': self.trust_level.value,
            'trust_score': self.trust_score,
            'confidence': self.confidence,
            'reasons': self.reasons,
            'is_government': self.is_government,
            'is_educational': self.is_educational,
            'keyword_matches': self.keyword_matches,
            'suspicious_patterns': self.suspicious_patterns,
            'recommendation': self.recommendation,
        }


class DomainTrustEvaluator:
    """
    Evaluates domain trustworthiness using multiple signals.
    
    Trust Scoring:
    - Base score from trust databases (0.0 - 1.0)
    - Bonus for keywords (+0.1 - +0.3)
    - Penalty for suspicious patterns (-0.2 - -0.5)
    - Final score clamped to [0, 1]
    """
    
    # Educational TLDs
    EDUCATIONAL_TLDS = {'.edu', '.ac.uk', '.edu.au', '.ac.jp', '.edu.cn'}
    
    # Suspicious TLD penalty map
    TLD_PENALTIES = {
        '.tk': 0.4, '.ml': 0.4, '.ga': 0.4, '.cf': 0.4, '.gq': 0.4,
        '.xyz': 0.2, '.top': 0.2, '.work': 0.15, '.click': 0.25,
        '.link': 0.15, '.loan': 0.3, '.men': 0.25, '.party': 0.2,
    }
    
    def __init__(self, custom_trusted_domains: Optional[Set[str]] = None):
        """
        Initialize the trust evaluator.
        
        Args:
            custom_trusted_domains: Optional set of additional trusted domains
        """
        self.tld_extractor = tldextract.TLDExtract(cache_dir=None)
        
        # Build combined trust databases
        self._high_trust = HIGH_TRUST_DOMAINS.copy()
        self._medium_trust = MEDIUM_TRUST_DOMAINS.copy()
        self._government = GOVERNMENT_DOMAINS.copy()
        self._top_sites = TOP_1K_DOMAINS_SAMPLE.copy()
        
        if custom_trusted_domains:
            self._high_trust.update(custom_trusted_domains)
        
        logger.info(f"Trust evaluator initialized with {len(self._high_trust)} high-trust domains")
    
    def evaluate(self, url: str) -> TrustEvaluation:
        """
        Evaluate the trustworthiness of a URL/domain.
        
        Args:
            url: URL or domain to evaluate
            
        Returns:
            TrustEvaluation with detailed trust analysis
        """
        # Extract domain components
        extracted = self.tld_extractor(url)
        domain = extracted.domain.lower()
        subdomain = extracted.subdomain.lower()
        suffix = extracted.suffix.lower()
        full_domain = extracted.registered_domain.lower() if extracted.registered_domain else f"{domain}.{suffix}"
        
        # Initialize evaluation
        reasons = []
        keyword_matches = []
        suspicious_patterns = []
        trust_score = 0.3  # Base score for unknown domains
        confidence = 0.5
        
        # Check trust databases
        db_result = self._check_trust_databases(full_domain, domain, suffix)
        trust_score = db_result['score']
        reasons.extend(db_result['reasons'])
        confidence = db_result['confidence']
        
        # Check government/educational status
        is_government = self._is_government_domain(full_domain, suffix)
        is_educational = self._is_educational_domain(suffix)
        
        if is_government:
            trust_score = max(trust_score, 0.9)
            reasons.append("Government domain detected")
            confidence = max(confidence, 0.95)
        
        if is_educational:
            trust_score = max(trust_score, 0.8)
            reasons.append("Educational domain detected")
            confidence = max(confidence, 0.85)
        
        # Keyword analysis
        keyword_result = self._analyze_keywords(domain, subdomain)
        keyword_matches = keyword_result['matches']
        trust_score += keyword_result['score_adjustment']
        reasons.extend(keyword_result['reasons'])
        
        # Suspicious pattern detection
        suspicious_result = self._detect_suspicious_patterns(url, domain, subdomain, full_domain)
        suspicious_patterns = suspicious_result['patterns']
        trust_score += suspicious_result['score_adjustment']
        reasons.extend(suspicious_result['reasons'])
        
        # TLD analysis
        tld_result = self._analyze_tld(suffix)
        trust_score += tld_result['score_adjustment']
        reasons.extend(tld_result['reasons'])
        
        # Clamp final score
        trust_score = max(0.0, min(1.0, trust_score))
        
        # Determine trust level
        trust_level = self._score_to_level(trust_score)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(trust_level, trust_score, suspicious_patterns)
        
        return TrustEvaluation(
            domain=domain,
            full_domain=full_domain,
            trust_level=trust_level,
            trust_score=round(trust_score, 4),
            confidence=round(confidence, 4),
            reasons=reasons,
            is_government=is_government,
            is_educational=is_educational,
            keyword_matches=keyword_matches,
            suspicious_patterns=suspicious_patterns,
            recommendation=recommendation,
        )
    
    def _check_trust_databases(self, full_domain: str, domain: str, suffix: str) -> Dict:
        """Check domain against trust databases"""
        reasons = []
        
        # Check top sites first (highest trust)
        if full_domain in self._top_sites:
            return {
                'score': 0.95,
                'confidence': 0.98,
                'reasons': [f"Top global website: {full_domain}"]
            }
        
        # Check high trust database
        if full_domain in self._high_trust:
            return {
                'score': 0.85,
                'confidence': 0.95,
                'reasons': [f"High-trust domain: {full_domain}"]
            }
        
        # Check if base domain (without country suffix) is in high trust
        # e.g., google.com.br -> check google.com
        base_variations = self._get_domain_variations(domain, suffix)
        for variation in base_variations:
            if variation in self._high_trust:
                return {
                    'score': 0.80,
                    'confidence': 0.90,
                    'reasons': [f"Regional variant of trusted domain: {variation}"]
                }
        
        # Check medium trust database
        if full_domain in self._medium_trust:
            return {
                'score': 0.60,
                'confidence': 0.75,
                'reasons': [f"Medium-trust domain: {full_domain}"]
            }
        
        # Unknown domain
        return {
            'score': 0.30,
            'confidence': 0.50,
            'reasons': [f"Unknown domain: {full_domain}"]
        }
    
    def _get_domain_variations(self, domain: str, suffix: str) -> List[str]:
        """Get variations of domain to check (for regional domains)"""
        variations = []
        
        # Common TLD variations
        common_tlds = ['.com', '.org', '.net', '.io']
        for tld in common_tlds:
            variations.append(f"{domain}{tld}")
        
        return variations
    
    def _is_government_domain(self, full_domain: str, suffix: str) -> bool:
        """Check if domain is government-related"""
        # Check explicit government domains
        if full_domain in self._government:
            return True
        
        # Check government TLD patterns
        for pattern in GOVERNMENT_TLD_PATTERNS:
            if suffix.endswith(pattern.lstrip('.')):
                return True
            if full_domain.endswith(pattern):
                return True
        
        return False
    
    def _is_educational_domain(self, suffix: str) -> bool:
        """Check if domain is educational"""
        suffix_with_dot = f".{suffix}"
        return suffix_with_dot in self.EDUCATIONAL_TLDS or suffix == 'edu'
    
    def _analyze_keywords(self, domain: str, subdomain: str) -> Dict:
        """Analyze domain for trusted/suspicious keywords"""
        matches = []
        reasons = []
        score_adjustment = 0.0
        
        full_host = f"{subdomain}.{domain}" if subdomain else domain
        
        # Check high-trust keywords
        for keyword in HIGH_TRUST_KEYWORDS:
            if keyword in domain:
                matches.append(keyword)
                score_adjustment += 0.1
                reasons.append(f"Contains trusted keyword: {keyword}")
        
        # Check medium-trust keywords
        for keyword in MEDIUM_TRUST_KEYWORDS:
            if keyword in domain or keyword in subdomain:
                if keyword not in matches:
                    matches.append(keyword)
                    score_adjustment += 0.05
                    reasons.append(f"Contains trust-indicating keyword: {keyword}")
        
        # Check suspicious keywords (potential phishing attempt)
        suspicious_count = 0
        for keyword in SUSPICIOUS_KEYWORDS:
            if keyword in full_host:
                if len(matches) > 0:  # Brand keyword + suspicious keyword
                    suspicious_count += 1
        
        if suspicious_count > 0 and len(matches) > 0:
            score_adjustment -= 0.3  # Significant penalty for brand + suspicious combo
            reasons.append(f"Warning: Brand keyword with {suspicious_count} suspicious terms")
        
        return {
            'matches': matches,
            'score_adjustment': score_adjustment,
            'reasons': reasons,
        }
    
    def _detect_suspicious_patterns(self, url: str, domain: str, subdomain: str, full_domain: str) -> Dict:
        """Detect suspicious patterns in URL"""
        patterns = []
        reasons = []
        score_adjustment = 0.0
        
        url_lower = url.lower()
        
        # Check phishing substrings
        for substring in PHISHING_SUBSTRINGS:
            if substring in subdomain or substring in domain:
                patterns.append(substring)
                score_adjustment -= 0.15
        
        if patterns:
            reasons.append(f"Suspicious substrings found: {', '.join(patterns[:3])}")
        
        # Check for excessive hyphens in domain
        hyphen_count = domain.count('-')
        if hyphen_count > 2:
            patterns.append(f"excessive-hyphens ({hyphen_count})")
            score_adjustment -= 0.1 * min(hyphen_count - 2, 3)
            reasons.append(f"Excessive hyphens in domain: {hyphen_count}")
        
        # Check for brand name in subdomain (potential impersonation)
        for brand in HIGH_TRUST_KEYWORDS:
            if brand in subdomain and brand not in domain:
                patterns.append(f"brand-in-subdomain ({brand})")
                score_adjustment -= 0.25
                reasons.append(f"Brand name '{brand}' in subdomain (potential impersonation)")
                break
        
        # Check for long subdomain (often used in phishing)
        if len(subdomain) > 30:
            patterns.append("long-subdomain")
            score_adjustment -= 0.15
            reasons.append("Unusually long subdomain")
        
        # Check for IP-like patterns in domain
        if re.search(r'\d{1,3}-\d{1,3}-\d{1,3}', domain):
            patterns.append("ip-like-domain")
            score_adjustment -= 0.2
            reasons.append("IP-address-like pattern in domain")
        
        # Check for homograph attack indicators
        if 'xn--' in url_lower:  # Punycode
            patterns.append("punycode-domain")
            score_adjustment -= 0.1
            reasons.append("Internationalized domain name (potential homograph attack)")
        
        return {
            'patterns': patterns,
            'score_adjustment': score_adjustment,
            'reasons': reasons,
        }
    
    def _analyze_tld(self, suffix: str) -> Dict:
        """Analyze TLD for trust signals"""
        reasons = []
        score_adjustment = 0.0
        
        suffix_with_dot = f".{suffix}"
        
        # Check suspicious TLDs
        if suffix_with_dot in PHISHING_TLD_PATTERNS:
            penalty = self.TLD_PENALTIES.get(suffix_with_dot, 0.2)
            score_adjustment -= penalty
            reasons.append(f"High-risk TLD: {suffix}")
        
        # Trusted TLDs get small bonus
        trusted_tlds = {'.com', '.org', '.net', '.edu', '.gov'}
        if suffix_with_dot in trusted_tlds:
            score_adjustment += 0.05
        
        return {
            'score_adjustment': score_adjustment,
            'reasons': reasons,
        }
    
    def _score_to_level(self, score: float) -> TrustLevel:
        """Convert trust score to trust level"""
        if score >= 0.85:
            return TrustLevel.HIGHEST
        elif score >= 0.70:
            return TrustLevel.HIGH
        elif score >= 0.50:
            return TrustLevel.MEDIUM
        elif score >= 0.30:
            return TrustLevel.LOW
        elif score >= 0.15:
            return TrustLevel.SUSPICIOUS
        else:
            return TrustLevel.DANGEROUS
    
    def _generate_recommendation(self, trust_level: TrustLevel, score: float, suspicious_patterns: List[str]) -> str:
        """Generate human-readable recommendation"""
        if trust_level == TrustLevel.HIGHEST:
            return "This domain is highly trusted. Safe to proceed."
        elif trust_level == TrustLevel.HIGH:
            return "This domain has a good reputation. Exercise standard caution."
        elif trust_level == TrustLevel.MEDIUM:
            return "This domain has moderate trust. Verify before entering sensitive information."
        elif trust_level == TrustLevel.LOW:
            return "This domain is unknown. Be cautious with any sensitive actions."
        elif trust_level == TrustLevel.SUSPICIOUS:
            return f"This domain shows suspicious patterns: {', '.join(suspicious_patterns[:2])}. Avoid entering personal information."
        else:
            return "This domain appears dangerous. Do not proceed or enter any information."
    
    def get_trust_score_for_prediction(self, url: str) -> float:
        """
        Get a simple trust score for use in ML ensemble predictions.
        Returns value between 0 and 1.
        """
        evaluation = self.evaluate(url)
        return evaluation.trust_score
    
    def is_whitelisted(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Quick check if URL is from a whitelisted domain.
        Returns (is_whitelisted, reason)
        """
        extracted = self.tld_extractor(url)
        full_domain = extracted.registered_domain
        
        if not full_domain:
            return False, None
        
        full_domain = full_domain.lower()
        
        if full_domain in self._top_sites:
            return True, f"Top global website: {full_domain}"
        
        if full_domain in self._high_trust:
            return True, f"High-trust domain: {full_domain}"
        
        if full_domain in self._government:
            return True, f"Government domain: {full_domain}"
        
        return False, None


# Singleton instance
domain_trust_evaluator = DomainTrustEvaluator()
