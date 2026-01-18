"""
API Routes for Phishing Detection
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from typing import List, Optional
from datetime import datetime
from loguru import logger
import asyncio

from api.schemas import (
    URLScanRequest,
    BatchScanRequest,
    WebpageScanRequest,
    FeedbackRequest,
    URLScanResponse,
    QuickScanResponse,
    BatchScanResponse,
    WebpageScanResponse,
    HealthResponse,
    ModelStatusResponse,
    FeedbackResponse,
    ErrorResponse,
    StatsResponse,
    RiskLevelEnum,
    StatusEnum,
    ModelPredictionResponse,
    TrustEvaluationResponse,
    URLFeaturesResponse,
    TrustLevelEnum,
)
from services.ensemble_predictor import get_ensemble_predictor, EnsemblePrediction
from services.domain_trust import domain_trust_evaluator
from services.feature_extractor import url_feature_extractor
from config.settings import settings


# Create router
router = APIRouter()


# =============================================================================
# Dependency to get predictor
# =============================================================================

def get_predictor():
    """Dependency to get ensemble predictor"""
    predictor = get_ensemble_predictor()
    if not predictor.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please wait for initialization."
        )
    return predictor


# =============================================================================
# URL Scanning Endpoints
# =============================================================================

@router.post("/scan", response_model=URLScanResponse)
async def scan_url(
    request: URLScanRequest,
    predictor = Depends(get_predictor),
):
    """
    Scan a single URL for phishing.
    
    Returns detailed analysis including:
    - Phishing probability from ensemble model
    - Individual model predictions
    - Domain trust evaluation
    - URL feature analysis
    - Risk assessment and recommendations
    """
    try:
        # Get prediction
        prediction = predictor.predict(request.url)
        
        # Build response
        response_data = {
            'url': prediction.url,
            'is_phishing': prediction.is_phishing,
            'phishing_probability': prediction.phishing_probability,
            'confidence': prediction.confidence,
            'risk_level': RiskLevelEnum(prediction.risk_level),
            'status': StatusEnum(prediction.status),
            'scan_timestamp': datetime.utcnow(),
            'threshold_used': prediction.threshold,
            'recommendation': _get_recommendation(prediction),
        }
        
        # Add details if requested
        if request.include_details:
            response_data['model_predictions'] = [
                ModelPredictionResponse(**mp) for mp in prediction.model_predictions
            ]
            
            response_data['trust_evaluation'] = TrustEvaluationResponse(
                trust_score=prediction.domain_trust_score,
                trust_level=TrustLevelEnum(prediction.domain_trust_level),
                is_whitelisted=prediction.is_whitelisted,
                whitelist_reason=prediction.whitelist_reason,
                is_government=prediction.url_features.get('is_government', False),
                is_educational=prediction.url_features.get('is_educational', False),
                reasons=[],
                suspicious_patterns=[],
            )
            
            response_data['url_features'] = URLFeaturesResponse(
                length=prediction.url_features['length'],
                entropy=prediction.url_features['entropy'],
                digits=prediction.url_features['digits'],
                letters=prediction.url_features['letters'],
                special_chars=prediction.url_features['special_chars'],
                has_ip=prediction.url_features['has_ip'],
                has_punycode=prediction.url_features['has_punycode'],
                has_encoded=prediction.url_features['has_encoded'],
                num_subdomains=prediction.url_features['num_subdomains'],
                domain=prediction.url_features['domain'],
                full_domain=prediction.url_features['full_domain'],
                has_https=prediction.url_features['has_https'],
            )
            
            response_data['rule_flags'] = prediction.rule_flags
        
        return URLScanResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan/quick", response_model=QuickScanResponse)
async def quick_scan(
    url: str = Query(..., description="URL to scan"),
    predictor = Depends(get_predictor),
):
    """
    Quick URL scan with minimal response.
    Optimized for speed - returns only essential information.
    """
    try:
        is_phishing, probability = predictor.get_quick_prediction(url)
        
        # Determine risk level
        if probability < 0.1:
            risk_level = RiskLevelEnum.VERY_LOW
        elif probability < 0.3:
            risk_level = RiskLevelEnum.LOW
        elif probability < 0.6:
            risk_level = RiskLevelEnum.MEDIUM
        elif probability < 0.85:
            risk_level = RiskLevelEnum.HIGH
        else:
            risk_level = RiskLevelEnum.CRITICAL
        
        return QuickScanResponse(
            url=url,
            is_phishing=is_phishing,
            probability=probability,
            risk_level=risk_level,
        )
        
    except Exception as e:
        logger.error(f"Quick scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan/batch", response_model=BatchScanResponse)
async def batch_scan(
    request: BatchScanRequest,
    predictor = Depends(get_predictor),
):
    """
    Scan multiple URLs in a single request.
    Maximum 100 URLs per request.
    """
    try:
        results = []
        phishing_count = 0
        safe_count = 0
        suspicious_count = 0
        
        for url in request.urls:
            prediction = predictor.predict(url)
            
            # Count categories
            if prediction.is_phishing:
                phishing_count += 1
            elif prediction.status == 'suspicious':
                suspicious_count += 1
            else:
                safe_count += 1
            
            # Build response
            result = URLScanResponse(
                url=prediction.url,
                is_phishing=prediction.is_phishing,
                phishing_probability=prediction.phishing_probability,
                confidence=prediction.confidence,
                risk_level=RiskLevelEnum(prediction.risk_level),
                status=StatusEnum(prediction.status),
                scan_timestamp=datetime.utcnow(),
                threshold_used=prediction.threshold,
                recommendation=_get_recommendation(prediction),
            )
            
            if request.include_details:
                result.model_predictions = [
                    ModelPredictionResponse(**mp) for mp in prediction.model_predictions
                ]
                result.rule_flags = prediction.rule_flags
            
            results.append(result)
        
        return BatchScanResponse(
            total_urls=len(request.urls),
            phishing_count=phishing_count,
            safe_count=safe_count,
            suspicious_count=suspicious_count,
            results=results,
            scan_timestamp=datetime.utcnow(),
        )
        
    except Exception as e:
        logger.error(f"Batch scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Domain Analysis Endpoints
# =============================================================================

@router.get("/domain/trust")
async def analyze_domain_trust(
    url: str = Query(..., description="URL or domain to analyze"),
):
    """
    Analyze domain trustworthiness without full phishing prediction.
    Returns detailed trust evaluation including:
    - Trust score and level
    - Whitelist status
    - Keyword matches
    - Suspicious patterns
    """
    try:
        trust_eval = domain_trust_evaluator.evaluate(url)
        is_whitelisted, whitelist_reason = domain_trust_evaluator.is_whitelisted(url)
        
        return {
            'domain': trust_eval.domain,
            'full_domain': trust_eval.full_domain,
            'trust_level': trust_eval.trust_level.value,
            'trust_score': trust_eval.trust_score,
            'confidence': trust_eval.confidence,
            'is_whitelisted': is_whitelisted,
            'whitelist_reason': whitelist_reason,
            'is_government': trust_eval.is_government,
            'is_educational': trust_eval.is_educational,
            'reasons': trust_eval.reasons,
            'keyword_matches': trust_eval.keyword_matches,
            'suspicious_patterns': trust_eval.suspicious_patterns,
            'recommendation': trust_eval.recommendation,
        }
        
    except Exception as e:
        logger.error(f"Domain trust analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/url/features")
async def extract_url_features(
    url: str = Query(..., description="URL to analyze"),
):
    """
    Extract detailed features from a URL.
    Useful for understanding what features the model uses.
    """
    try:
        features = url_feature_extractor.extract_features(url)
        return features.to_dict()
        
    except Exception as e:
        logger.error(f"Feature extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Feedback & Reporting
# =============================================================================

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    background_tasks: BackgroundTasks,
):
    """
    Submit feedback on a prediction.
    Helps improve model accuracy over time.
    """
    try:
        # In production, this would save to database
        logger.info(
            f"Feedback received for {request.url}: "
            f"correct={request.is_correct}, actual={request.actual_label}"
        )
        
        # TODO: Save feedback to database in background
        # background_tasks.add_task(save_feedback, request)
        
        return FeedbackResponse(
            success=True,
            message="Thank you for your feedback!",
            feedback_id=None,  # Would be generated by database
        )
        
    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# System Status Endpoints
# =============================================================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns system status and model availability.
    """
    try:
        predictor = get_ensemble_predictor()
        
        models_status = {
            'electra': predictor._electra is not None and predictor._electra.is_loaded() if predictor._electra else False,
            'biformer': predictor._biformer is not None and predictor._biformer.is_loaded() if predictor._biformer else False,
            'lgbm': predictor._lgbm is not None and predictor._lgbm.is_loaded() if predictor._lgbm else False,
        }
        
        return HealthResponse(
            status="healthy" if predictor.is_loaded() else "degraded",
            version=settings.APP_VERSION,
            models_loaded=models_status,
            timestamp=datetime.utcnow(),
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            version=settings.APP_VERSION,
            models_loaded={'electra': False, 'biformer': False, 'lgbm': False},
            timestamp=datetime.utcnow(),
        )


@router.get("/models/status", response_model=ModelStatusResponse)
async def model_status():
    """
    Get detailed status of all models.
    """
    try:
        predictor = get_ensemble_predictor()
        
        return ModelStatusResponse(
            electra={
                'loaded': predictor._electra is not None and predictor._electra.is_loaded() if predictor._electra else False,
                'weight': predictor.electra_weight,
            },
            biformer={
                'loaded': predictor._biformer is not None and predictor._biformer.is_loaded() if predictor._biformer else False,
                'weight': predictor.biformer_weight,
            },
            lgbm={
                'loaded': predictor._lgbm is not None and predictor._lgbm.is_loaded() if predictor._lgbm else False,
                'weight': predictor.lgbm_weight,
            },
            ensemble_ready=predictor.is_loaded(),
        )
        
    except Exception as e:
        logger.error(f"Model status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Helper Functions
# =============================================================================

def _get_recommendation(prediction: EnsemblePrediction) -> str:
    """Generate user-friendly recommendation based on prediction"""
    if prediction.is_whitelisted:
        return "This is a trusted website. Safe to proceed."
    
    if prediction.is_phishing:
        if prediction.risk_level == 'critical':
            return "⚠️ HIGH RISK: This URL is very likely a phishing attempt. Do NOT enter any personal information."
        else:
            return "⚠️ WARNING: This URL shows signs of phishing. Proceed with extreme caution."
    
    if prediction.status == 'suspicious':
        return "This URL has some suspicious characteristics. Verify the site before entering sensitive information."
    
    if prediction.risk_level == 'very_low':
        return "This URL appears safe. Normal caution advised."
    
    return "This URL appears legitimate. Standard security practices recommended."
