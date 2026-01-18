"""
Pydantic schemas for API requests and responses
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl, field_validator
from datetime import datetime
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class RiskLevelEnum(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StatusEnum(str, Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    PHISHING = "phishing"
    UNKNOWN = "unknown"


class TrustLevelEnum(str, Enum):
    HIGHEST = "highest"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"


# =============================================================================
# Request Schemas
# =============================================================================

class URLScanRequest(BaseModel):
    """Request for scanning a single URL"""
    url: str = Field(..., description="URL to scan for phishing")
    include_details: bool = Field(
        default=True,
        description="Include detailed analysis in response"
    )
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        if len(v) > 2048:
            raise ValueError("URL too long (max 2048 characters)")
        return v


class BatchScanRequest(BaseModel):
    """Request for scanning multiple URLs"""
    urls: List[str] = Field(
        ...,
        description="List of URLs to scan",
        min_length=1,
        max_length=100
    )
    include_details: bool = Field(
        default=False,
        description="Include detailed analysis for each URL"
    )


class WebpageScanRequest(BaseModel):
    """Request for scanning a webpage and extracting URLs"""
    url: str = Field(..., description="Webpage URL to scan")
    scan_links: bool = Field(
        default=True,
        description="Also scan links found in the page"
    )
    max_links: int = Field(
        default=50,
        description="Maximum number of links to scan",
        ge=1,
        le=200
    )


class FeedbackRequest(BaseModel):
    """User feedback on a prediction"""
    url: str = Field(..., description="URL that was scanned")
    prediction_id: Optional[str] = Field(None, description="ID of the prediction")
    is_correct: bool = Field(..., description="Whether the prediction was correct")
    actual_label: Optional[int] = Field(
        None,
        description="Actual label (0=legitimate, 1=phishing)"
    )
    comment: Optional[str] = Field(None, description="Optional feedback comment")


# =============================================================================
# Response Schemas
# =============================================================================

class ModelPredictionResponse(BaseModel):
    """Individual model prediction details"""
    source: str
    probability: float
    weight: float
    weighted_contribution: float


class URLFeaturesResponse(BaseModel):
    """Extracted URL features"""
    length: int
    entropy: float
    digits: int
    letters: int
    special_chars: int
    has_ip: int
    has_punycode: int
    has_encoded: int
    num_subdomains: int
    domain: str
    full_domain: str
    has_https: int


class TrustEvaluationResponse(BaseModel):
    """Domain trust evaluation details"""
    trust_score: float
    trust_level: TrustLevelEnum
    is_whitelisted: bool
    whitelist_reason: Optional[str]
    is_government: bool
    is_educational: bool
    reasons: List[str]
    suspicious_patterns: List[str]


class URLScanResponse(BaseModel):
    """Response for URL scan"""
    url: str
    is_phishing: bool
    phishing_probability: float = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0, le=1)
    risk_level: RiskLevelEnum
    status: StatusEnum
    
    # Detailed information (optional based on include_details)
    model_predictions: Optional[List[ModelPredictionResponse]] = None
    trust_evaluation: Optional[TrustEvaluationResponse] = None
    url_features: Optional[URLFeaturesResponse] = None
    rule_flags: Optional[List[str]] = None
    
    # Metadata
    scan_timestamp: datetime = Field(default_factory=datetime.utcnow)
    threshold_used: float
    recommendation: str


class QuickScanResponse(BaseModel):
    """Minimal response for quick scans"""
    url: str
    is_phishing: bool
    probability: float
    risk_level: RiskLevelEnum


class BatchScanResponse(BaseModel):
    """Response for batch URL scan"""
    total_urls: int
    phishing_count: int
    safe_count: int
    suspicious_count: int
    results: List[URLScanResponse]
    scan_timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebpageScanResponse(BaseModel):
    """Response for webpage scan"""
    page_url: str
    page_is_phishing: bool
    page_probability: float
    links_scanned: int
    phishing_links_found: int
    suspicious_links_found: int
    link_results: List[QuickScanResponse]
    scan_timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    models_loaded: Dict[str, bool]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ModelStatusResponse(BaseModel):
    """Model status response"""
    electra: Dict[str, Any]
    biformer: Dict[str, Any]
    lgbm: Dict[str, Any]
    ensemble_ready: bool


class FeedbackResponse(BaseModel):
    """Response for feedback submission"""
    success: bool
    message: str
    feedback_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatsResponse(BaseModel):
    """System statistics response"""
    total_scans: int
    phishing_detected: int
    safe_urls: int
    average_response_time_ms: float
    uptime_seconds: float
    cache_hit_rate: float
