"""
Tests for the phishing detection API
"""

import pytest
from fastapi.testclient import TestClient

# Import will work when running from backend directory
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_root(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
    
    def test_liveness(self, client):
        """Test liveness probe"""
        response = client.get("/live")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"
    
    def test_readiness(self, client):
        """Test readiness probe"""
        response = client.get("/ready")
        # May be 200 or 503 depending on model loading
        assert response.status_code in [200, 503]


class TestURLFeatures:
    """Test URL feature extraction"""
    
    def test_feature_extraction(self, client):
        """Test feature extraction endpoint"""
        response = client.get(
            "/api/v1/url/features",
            params={"url": "https://www.google.com"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "length" in data
        assert "entropy" in data
        assert "domain" in data
        assert data["has_https"] == 1


class TestDomainTrust:
    """Test domain trust evaluation"""
    
    def test_google_trust(self, client):
        """Test Google domain trust"""
        response = client.get(
            "/api/v1/domain/trust",
            params={"url": "https://www.google.com"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["trust_score"] > 0.7
        assert data["trust_level"] in ["highest", "high"]
    
    def test_unknown_domain(self, client):
        """Test unknown domain trust"""
        response = client.get(
            "/api/v1/domain/trust",
            params={"url": "https://randomsite123456.xyz"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["trust_level"] in ["low", "suspicious", "medium"]


class TestURLScan:
    """Test URL scanning endpoints"""
    
    def test_scan_safe_url(self, client):
        """Test scanning a safe URL"""
        response = client.post(
            "/api/v1/scan",
            json={"url": "https://www.wikipedia.org", "include_details": True}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["url"] == "https://www.wikipedia.org"
        assert "is_phishing" in data
        assert "phishing_probability" in data
        assert "risk_level" in data
    
    def test_quick_scan(self, client):
        """Test quick scan endpoint"""
        response = client.get(
            "/api/v1/scan/quick",
            params={"url": "https://www.apple.com"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["url"] == "https://www.apple.com"
        assert "probability" in data
        assert "risk_level" in data
    
    def test_batch_scan(self, client):
        """Test batch scan endpoint"""
        urls = [
            "https://www.google.com",
            "https://www.microsoft.com",
            "https://www.apple.com"
        ]
        
        response = client.post(
            "/api/v1/scan/batch",
            json={"urls": urls, "include_details": False}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_urls"] == 3
        assert len(data["results"]) == 3
    
    def test_scan_invalid_url(self, client):
        """Test scanning with empty URL"""
        response = client.post(
            "/api/v1/scan",
            json={"url": ""}
        )
        assert response.status_code == 422  # Validation error


class TestSuspiciousURLs:
    """Test detection of suspicious URLs"""
    
    def test_ip_address_url(self, client):
        """Test URL with IP address"""
        response = client.post(
            "/api/v1/scan",
            json={"url": "http://192.168.1.1/login", "include_details": True}
        )
        assert response.status_code == 200
        data = response.json()
        
        # IP addresses should be flagged
        assert data["url_features"]["has_ip"] == 1
        if "rule_flags" in data and data["rule_flags"]:
            assert "ip_address_url" in data["rule_flags"]
    
    def test_suspicious_tld(self, client):
        """Test URL with suspicious TLD"""
        response = client.get(
            "/api/v1/domain/trust",
            params={"url": "http://example.tk"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # .tk is a suspicious TLD
        assert data["trust_score"] < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
