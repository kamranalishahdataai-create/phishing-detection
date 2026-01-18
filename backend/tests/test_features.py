"""
Tests for feature extractor
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.feature_extractor import URLFeatureExtractor, url_feature_extractor


class TestURLFeatureExtractor:
    """Test URL feature extraction"""
    
    @pytest.fixture
    def extractor(self):
        return URLFeatureExtractor()
    
    def test_basic_extraction(self, extractor):
        """Test basic feature extraction"""
        features = extractor.extract_features("https://www.google.com")
        
        assert features.length > 0
        assert features.entropy > 0
        assert features.domain == "google"
        assert features.has_https == 1
        assert features.has_ip == 0
    
    def test_ip_detection(self, extractor):
        """Test IP address detection"""
        features = extractor.extract_features("http://192.168.1.1/login")
        assert features.has_ip == 1
    
    def test_subdomain_counting(self, extractor):
        """Test subdomain counting"""
        features = extractor.extract_features("https://www.mail.google.com")
        assert features.num_subdomains >= 2  # www and mail
    
    def test_special_characters(self, extractor):
        """Test special character counting"""
        features = extractor.extract_features("https://example.com/path?q=test&id=123")
        assert features.special_chars > 0
        assert features.digits > 0
    
    def test_entropy_calculation(self, extractor):
        """Test entropy calculation"""
        # Low entropy (repetitive)
        features1 = extractor.extract_features("http://aaaaaa.com")
        
        # Higher entropy (varied)
        features2 = extractor.extract_features("http://abcdef123.com/xyz")
        
        assert features2.entropy >= features1.entropy
    
    def test_punycode_detection(self, extractor):
        """Test punycode detection"""
        features = extractor.extract_features("https://xn--80ak6aa92e.com")
        assert features.has_punycode == 1
    
    def test_url_encoding_detection(self, extractor):
        """Test URL encoding detection"""
        features = extractor.extract_features("https://example.com/path%20with%20spaces")
        assert features.has_encoded == 1
    
    def test_lgbm_features(self, extractor):
        """Test LightGBM feature extraction"""
        features = extractor.extract_lgbm_features("https://www.google.com")
        
        assert isinstance(features, list)
        assert len(features) == 12  # Expected number of features
        assert all(isinstance(f, (int, float)) for f in features)


class TestEntropy:
    """Test entropy calculation specifically"""
    
    def test_zero_entropy(self):
        """Test entropy of single character string"""
        extractor = URLFeatureExtractor()
        entropy = extractor._calculate_entropy("aaaa")
        assert entropy == 0.0
    
    def test_max_entropy(self):
        """Test entropy of highly varied string"""
        extractor = URLFeatureExtractor()
        entropy = extractor._calculate_entropy("abcdefghijklmnopqrstuvwxyz")
        assert entropy > 4.0  # Should be close to log2(26)
    
    def test_empty_string(self):
        """Test entropy of empty string"""
        extractor = URLFeatureExtractor()
        entropy = extractor._calculate_entropy("")
        assert entropy == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
