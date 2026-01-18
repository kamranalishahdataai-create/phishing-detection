"""
Database Models and Connection
SQLAlchemy models for caching, logging, and feedback
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    Text, JSON, ForeignKey, Index, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.config.settings import settings


# Base class for models
Base = declarative_base()


# =============================================================================
# Database Models
# =============================================================================

class URLScan(Base):
    """Store URL scan results for caching and analytics"""
    
    __tablename__ = "url_scans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), nullable=False, index=True)
    url_hash = Column(String(64), nullable=False, unique=True, index=True)
    
    # Prediction results
    is_phishing = Column(Boolean, nullable=False)
    phishing_probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    
    # Individual model scores
    electra_probability = Column(Float, nullable=True)
    biformer_probability = Column(Float, nullable=True)
    lgbm_probability = Column(Float, nullable=True)
    
    # Domain trust
    domain = Column(String(255), nullable=True, index=True)
    domain_trust_score = Column(Float, nullable=True)
    domain_trust_level = Column(String(20), nullable=True)
    is_whitelisted = Column(Boolean, default=False)
    
    # Metadata
    threshold_used = Column(Float, nullable=False)
    rule_flags = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Cache control
    cache_expires_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<URLScan(url={self.url[:50]}, is_phishing={self.is_phishing})>"


class URLFeatureCache(Base):
    """Cache extracted URL features"""
    
    __tablename__ = "url_feature_cache"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url_hash = Column(String(64), nullable=False, unique=True, index=True)
    
    # Features
    length = Column(Integer)
    entropy = Column(Float)
    digits = Column(Integer)
    letters = Column(Integer)
    special_chars = Column(Integer)
    has_ip = Column(Boolean)
    has_punycode = Column(Boolean)
    has_encoded = Column(Boolean)
    num_subdomains = Column(Integer)
    path_length = Column(Integer)
    has_https = Column(Boolean)
    
    # Domain info
    domain = Column(String(255))
    full_domain = Column(String(255))
    
    # Full features JSON
    features_json = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<URLFeatureCache(url_hash={self.url_hash[:20]})>"


class DomainTrustCache(Base):
    """Cache domain trust evaluations"""
    
    __tablename__ = "domain_trust_cache"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String(255), nullable=False, unique=True, index=True)
    full_domain = Column(String(255), nullable=False)
    
    # Trust evaluation
    trust_score = Column(Float, nullable=False)
    trust_level = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    is_whitelisted = Column(Boolean, default=False)
    whitelist_reason = Column(String(255), nullable=True)
    
    # Flags
    is_government = Column(Boolean, default=False)
    is_educational = Column(Boolean, default=False)
    
    # Details
    reasons = Column(JSON, nullable=True)
    keyword_matches = Column(JSON, nullable=True)
    suspicious_patterns = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<DomainTrustCache(domain={self.domain}, trust_level={self.trust_level})>"


class UserFeedback(Base):
    """Store user feedback on predictions"""
    
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Reference to scan
    url = Column(String(2048), nullable=False)
    url_hash = Column(String(64), nullable=False, index=True)
    scan_id = Column(Integer, ForeignKey('url_scans.id'), nullable=True)
    
    # Feedback
    prediction_was_correct = Column(Boolean, nullable=False)
    actual_label = Column(Integer, nullable=True)  # 0=legitimate, 1=phishing
    user_comment = Column(Text, nullable=True)
    
    # Original prediction
    predicted_label = Column(Integer, nullable=True)
    predicted_probability = Column(Float, nullable=True)
    
    # Metadata
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<UserFeedback(url={self.url[:30]}, correct={self.prediction_was_correct})>"


class ScanLog(Base):
    """Log all scan requests for analytics"""
    
    __tablename__ = "scan_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Request info
    url = Column(String(2048), nullable=False)
    endpoint = Column(String(100), nullable=False)
    request_type = Column(String(20), nullable=False)  # single, batch, quick
    
    # Response info
    is_phishing = Column(Boolean, nullable=False)
    probability = Column(Float, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    
    # Request metadata
    user_agent = Column(String(512), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ScanLog(url={self.url[:30]}, is_phishing={self.is_phishing})>"


class TrustedDomainList(Base):
    """Custom trusted domain lists"""
    
    __tablename__ = "trusted_domain_lists"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    domain = Column(String(255), nullable=False, unique=True, index=True)
    trust_level = Column(String(20), nullable=False)  # high, medium, low
    category = Column(String(50), nullable=True)  # bank, tech, government, etc.
    
    # Source
    source = Column(String(100), nullable=True)  # manual, imported, api
    added_by = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TrustedDomainList(domain={self.domain}, trust_level={self.trust_level})>"


# =============================================================================
# Indexes
# =============================================================================

# Additional indexes for common queries
Index('ix_url_scans_created_domain', URLScan.created_at, URLScan.domain)
Index('ix_scan_logs_created_phishing', ScanLog.created_at, ScanLog.is_phishing)
Index('ix_feedback_created', UserFeedback.created_at)


# =============================================================================
# Database Connection
# =============================================================================

class Database:
    """Database connection manager"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or settings.DATABASE_URL
        self.engine = None
        self.async_session_factory = None
    
    async def connect(self):
        """Create database connection"""
        self.engine = create_async_engine(
            self.database_url,
            echo=settings.DEBUG,
            future=True,
        )
        
        self.async_session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def disconnect(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
    
    async def get_session(self) -> AsyncSession:
        """Get a new database session"""
        async with self.async_session_factory() as session:
            yield session


# Singleton database instance
database = Database()


# =============================================================================
# Helper Functions
# =============================================================================

import hashlib


def get_url_hash(url: str) -> str:
    """Generate consistent hash for URL"""
    return hashlib.sha256(url.encode()).hexdigest()


async def cache_scan_result(session: AsyncSession, prediction, url: str):
    """Cache a scan result to database"""
    url_hash = get_url_hash(url)
    
    scan = URLScan(
        url=url,
        url_hash=url_hash,
        is_phishing=prediction.is_phishing,
        phishing_probability=prediction.phishing_probability,
        confidence=prediction.confidence,
        risk_level=prediction.risk_level,
        status=prediction.status,
        electra_probability=prediction.electra_probability,
        biformer_probability=prediction.biformer_probability,
        lgbm_probability=prediction.lgbm_probability,
        domain=prediction.url_features.get('domain'),
        domain_trust_score=prediction.domain_trust_score,
        domain_trust_level=prediction.domain_trust_level,
        is_whitelisted=prediction.is_whitelisted,
        threshold_used=prediction.threshold,
        rule_flags=prediction.rule_flags,
    )
    
    session.add(scan)
    await session.commit()
    
    return scan


async def get_cached_scan(session: AsyncSession, url: str) -> Optional[URLScan]:
    """Get cached scan result if exists and not expired"""
    from sqlalchemy import select
    
    url_hash = get_url_hash(url)
    
    result = await session.execute(
        select(URLScan)
        .where(URLScan.url_hash == url_hash)
        .where(URLScan.cache_expires_at > datetime.utcnow())
    )
    
    return result.scalar_one_or_none()
