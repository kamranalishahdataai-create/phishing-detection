"""
Tests for domain trust evaluation
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.domain_trust import DomainTrustEvaluator, TrustLevel


class TestDomainTrustEvaluator:
    """Test domain trust evaluation"""
    
    @pytest.fixture
    def evaluator(self):
        return DomainTrustEvaluator()
    
    def test_google_high_trust(self, evaluator):
        """Test Google domain gets high trust"""
        result = evaluator.evaluate("https://www.google.com")
        
        assert result.trust_level in [TrustLevel.HIGHEST, TrustLevel.HIGH]
        assert result.trust_score >= 0.8
    
    def test_government_domain(self, evaluator):
        """Test government domain detection"""
        result = evaluator.evaluate("https://www.whitehouse.gov")
        
        assert result.is_government or result.trust_score >= 0.7
    
    def test_educational_domain(self, evaluator):
        """Test educational domain detection"""
        result = evaluator.evaluate("https://www.stanford.edu")
        
        assert result.is_educational or result.trust_score >= 0.7
    
    def test_unknown_domain(self, evaluator):
        """Test unknown domain gets low trust"""
        result = evaluator.evaluate("https://randomsite98765.xyz")
        
        assert result.trust_level in [TrustLevel.LOW, TrustLevel.SUSPICIOUS]
        assert result.trust_score < 0.5
    
    def test_suspicious_tld(self, evaluator):
        """Test suspicious TLD gets penalty"""
        result_normal = evaluator.evaluate("https://example.com")
        result_suspicious = evaluator.evaluate("https://example.tk")
        
        assert result_suspicious.trust_score < result_normal.trust_score
    
    def test_brand_in_subdomain(self, evaluator):
        """Test brand in subdomain detection"""
        result = evaluator.evaluate("https://google.malicious-site.com")
        
        # Should detect google brand in subdomain of non-google domain
        assert result.trust_score < 0.5 or "brand-in-subdomain" in str(result.suspicious_patterns)
    
    def test_whitelist_check(self, evaluator):
        """Test whitelist checking"""
        is_whitelisted, reason = evaluator.is_whitelisted("https://www.microsoft.com")
        
        assert is_whitelisted == True
        assert reason is not None
    
    def test_keyword_detection(self, evaluator):
        """Test trusted keyword detection"""
        result = evaluator.evaluate("https://google-services.com")
        
        # 'google' keyword should be detected
        assert "google" in result.keyword_matches or result.trust_score > 0.3
    
    def test_trust_score_range(self, evaluator):
        """Test trust score is in valid range"""
        urls = [
            "https://google.com",
            "https://random123.tk",
            "https://whitehouse.gov",
            "https://suspicious-login.xyz",
        ]
        
        for url in urls:
            result = evaluator.evaluate(url)
            assert 0.0 <= result.trust_score <= 1.0


class TestTrustLevels:
    """Test trust level categorization"""
    
    def test_trust_level_ordering(self):
        """Test trust level ordering"""
        evaluator = DomainTrustEvaluator()
        
        # Score to level conversion should be consistent
        high_score_result = evaluator._score_to_level(0.9)
        low_score_result = evaluator._score_to_level(0.1)
        
        assert high_score_result in [TrustLevel.HIGHEST, TrustLevel.HIGH]
        assert low_score_result in [TrustLevel.SUSPICIOUS, TrustLevel.DANGEROUS]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
