"""
Ensemble Prediction Service
Combines multiple models with domain trust evaluation for phishing detection
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from loguru import logger
import numpy as np

from config.settings import settings
from config.constants import PhishingStatus, RiskLevel
from models.electra_model import get_electra_model, ElectraURLModel
from models.biformer_model import get_biformer_model, BiformerURLModel
from models.lgbm_model import get_lgbm_model, LGBMURLModel
from services.domain_trust import domain_trust_evaluator, TrustEvaluation
from services.feature_extractor import url_feature_extractor, URLFeatures


class PredictionSource(Enum):
    """Source of prediction component"""
    ELECTRA = "electra"
    BIFORMER = "biformer"
    LGBM = "lgbm"
    DOMAIN_TRUST = "domain_trust"
    RULES = "rules"


@dataclass
class ModelPrediction:
    """Individual model prediction result"""
    source: str
    probability: float
    weight: float
    weighted_contribution: float


@dataclass
class EnsemblePrediction:
    """Complete ensemble prediction result"""
    url: str
    
    # Final prediction
    is_phishing: bool
    phishing_probability: float
    confidence: float
    risk_level: str
    status: str
    
    # Individual model predictions
    electra_probability: float
    biformer_probability: float
    lgbm_probability: float
    
    # Model contributions
    model_predictions: List[Dict]
    
    # Domain trust info
    domain_trust_score: float
    domain_trust_level: str
    is_whitelisted: bool
    whitelist_reason: Optional[str]
    
    # Feature info
    url_features: Dict
    
    # Rule-based flags
    rule_flags: List[str]
    rule_override: Optional[str]
    
    # Threshold used
    threshold: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class EnsemblePredictor:
    """
    Ensemble model that combines:
    - ELECTRA (transformer-based text model)
    - Biformer (character-level model)
    - LightGBM (feature-based model)
    - Domain trust evaluation
    - Rule-based overrides
    """
    
    def __init__(
        self,
        electra_weight: float = None,
        biformer_weight: float = None,
        lgbm_weight: float = None,
        threshold: float = None,
        enable_trust_adjustment: bool = True,
        enable_rule_overrides: bool = True,
    ):
        """
        Initialize the ensemble predictor.
        
        Args:
            electra_weight: Weight for ELECTRA model (default from settings)
            biformer_weight: Weight for Biformer model
            lgbm_weight: Weight for LightGBM model
            threshold: Phishing detection threshold
            enable_trust_adjustment: Whether to adjust predictions based on domain trust
            enable_rule_overrides: Whether to apply rule-based overrides
        """
        # Model weights
        self.electra_weight = electra_weight or settings.ELECTRA_WEIGHT
        self.biformer_weight = biformer_weight or settings.BIFORMER_WEIGHT
        self.lgbm_weight = lgbm_weight or settings.LGBM_WEIGHT
        
        # Normalize weights
        total_weight = self.electra_weight + self.biformer_weight + self.lgbm_weight
        self.electra_weight /= total_weight
        self.biformer_weight /= total_weight
        self.lgbm_weight /= total_weight
        
        # Threshold
        self.threshold = threshold or settings.PHISHING_THRESHOLD
        
        # Options
        self.enable_trust_adjustment = enable_trust_adjustment
        self.enable_rule_overrides = enable_rule_overrides
        
        # Model instances (lazy loaded)
        self._electra: Optional[ElectraURLModel] = None
        self._biformer: Optional[BiformerURLModel] = None
        self._lgbm: Optional[LGBMURLModel] = None
        
        self._loaded = False
        
        logger.info(
            f"EnsemblePredictor initialized "
            f"(weights: E={self.electra_weight:.2f}, B={self.biformer_weight:.2f}, L={self.lgbm_weight:.2f})"
        )
    
    def load_models(self) -> Dict[str, bool]:
        """
        Load all models.
        
        Returns:
            Dictionary with load status for each model
        """
        status = {}
        
        try:
            logger.info("Loading ELECTRA model...")
            self._electra = get_electra_model()
            status['electra'] = self._electra.is_loaded()
        except Exception as e:
            logger.error(f"Failed to load ELECTRA: {e}")
            status['electra'] = False
        
        try:
            logger.info("Loading Biformer model...")
            self._biformer = get_biformer_model()
            status['biformer'] = self._biformer.is_loaded()
        except Exception as e:
            logger.error(f"Failed to load Biformer: {e}")
            status['biformer'] = False
        
        try:
            logger.info("Loading LightGBM model...")
            self._lgbm = get_lgbm_model()
            status['lgbm'] = self._lgbm.is_loaded()
        except Exception as e:
            logger.error(f"Failed to load LightGBM: {e}")
            status['lgbm'] = False
        
        self._loaded = any(status.values())
        
        logger.info(f"Model loading status: {status}")
        return status
    
    def is_loaded(self) -> bool:
        """Check if at least one model is loaded"""
        return self._loaded
    
    def predict(self, url: str) -> EnsemblePrediction:
        """
        Make ensemble prediction for a single URL.
        
        Args:
            url: URL to analyze
            
        Returns:
            EnsemblePrediction with detailed results
        """
        # Extract features
        features = url_feature_extractor.extract_features(url)
        
        # Get domain trust evaluation
        trust_eval = domain_trust_evaluator.evaluate(url)
        is_whitelisted, whitelist_reason = domain_trust_evaluator.is_whitelisted(url)
        
        # Get model predictions
        model_probs = self._get_model_probabilities(url)
        
        # Apply rule-based checks
        rule_flags, rule_override = self._apply_rules(url, features, trust_eval)
        
        # Calculate ensemble probability
        ensemble_prob = self._calculate_ensemble_probability(
            model_probs,
            trust_eval,
            is_whitelisted,
            rule_override,
        )
        
        # Determine final prediction
        is_phishing = ensemble_prob >= self.threshold
        
        # Handle rule overrides
        if rule_override == 'safe':
            is_phishing = False
            ensemble_prob = min(ensemble_prob, self.threshold - 0.01)
        elif rule_override == 'phishing':
            is_phishing = True
            ensemble_prob = max(ensemble_prob, self.threshold + 0.01)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            ensemble_prob,
            model_probs,
            trust_eval,
        )
        
        # Determine risk level and status
        risk_level = self._get_risk_level(ensemble_prob, is_whitelisted)
        status = PhishingStatus.PHISHING if is_phishing else PhishingStatus.SAFE
        if not is_phishing and ensemble_prob > self.threshold * 0.5:
            status = PhishingStatus.SUSPICIOUS
        
        # Build model predictions list
        model_predictions = []
        if model_probs['electra'] is not None:
            model_predictions.append({
                'source': 'electra',
                'probability': model_probs['electra'],
                'weight': self.electra_weight,
                'weighted_contribution': model_probs['electra'] * self.electra_weight,
            })
        if model_probs['biformer'] is not None:
            model_predictions.append({
                'source': 'biformer',
                'probability': model_probs['biformer'],
                'weight': self.biformer_weight,
                'weighted_contribution': model_probs['biformer'] * self.biformer_weight,
            })
        if model_probs['lgbm'] is not None:
            model_predictions.append({
                'source': 'lgbm',
                'probability': model_probs['lgbm'],
                'weight': self.lgbm_weight,
                'weighted_contribution': model_probs['lgbm'] * self.lgbm_weight,
            })
        
        return EnsemblePrediction(
            url=url,
            is_phishing=is_phishing,
            phishing_probability=round(ensemble_prob, 6),
            confidence=round(confidence, 4),
            risk_level=risk_level,
            status=status,
            electra_probability=model_probs['electra'] or 0.0,
            biformer_probability=model_probs['biformer'] or 0.0,
            lgbm_probability=model_probs['lgbm'] or 0.0,
            model_predictions=model_predictions,
            domain_trust_score=trust_eval.trust_score,
            domain_trust_level=trust_eval.trust_level.value,
            is_whitelisted=is_whitelisted,
            whitelist_reason=whitelist_reason,
            url_features=features.to_dict(),
            rule_flags=rule_flags,
            rule_override=rule_override,
            threshold=self.threshold,
        )
    
    def predict_batch(self, urls: List[str]) -> List[EnsemblePrediction]:
        """
        Make ensemble predictions for multiple URLs.
        
        Args:
            urls: List of URLs to analyze
            
        Returns:
            List of EnsemblePrediction results
        """
        return [self.predict(url) for url in urls]
    
    def _get_model_probabilities(self, url: str) -> Dict[str, Optional[float]]:
        """Get probabilities from all loaded models"""
        probs = {
            'electra': None,
            'biformer': None,
            'lgbm': None,
        }
        
        if self._electra and self._electra.is_loaded():
            try:
                probs['electra'] = self._electra.get_phishing_probability(url)
            except Exception as e:
                logger.warning(f"ELECTRA prediction failed: {e}")
        
        if self._biformer and self._biformer.is_loaded():
            try:
                probs['biformer'] = self._biformer.get_phishing_probability(url)
            except Exception as e:
                logger.warning(f"Biformer prediction failed: {e}")
        
        if self._lgbm and self._lgbm.is_loaded():
            try:
                probs['lgbm'] = self._lgbm.get_phishing_probability(url)
            except Exception as e:
                logger.warning(f"LightGBM prediction failed: {e}")
        
        return probs
    
    def _calculate_ensemble_probability(
        self,
        model_probs: Dict[str, Optional[float]],
        trust_eval: TrustEvaluation,
        is_whitelisted: bool,
        rule_override: Optional[str],
    ) -> float:
        """Calculate weighted ensemble probability"""
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        # Add model contributions
        if model_probs['electra'] is not None:
            weighted_sum += model_probs['electra'] * self.electra_weight
            total_weight += self.electra_weight
        
        if model_probs['biformer'] is not None:
            weighted_sum += model_probs['biformer'] * self.biformer_weight
            total_weight += self.biformer_weight
        
        if model_probs['lgbm'] is not None:
            weighted_sum += model_probs['lgbm'] * self.lgbm_weight
            total_weight += self.lgbm_weight
        
        # Handle case where no models are available
        if total_weight == 0:
            # Fall back to inverse of trust score
            return 1.0 - trust_eval.trust_score
        
        # Normalize
        ensemble_prob = weighted_sum / total_weight
        
        # Apply trust adjustment
        if self.enable_trust_adjustment:
            # High trust reduces phishing probability
            trust_factor = 1.0 - (trust_eval.trust_score * 0.3)
            ensemble_prob *= trust_factor
            
            # Whitelisted domains get extra reduction
            if is_whitelisted:
                ensemble_prob *= 0.1
        
        # Apply suspicious pattern boost
        if trust_eval.suspicious_patterns:
            pattern_boost = min(len(trust_eval.suspicious_patterns) * 0.1, 0.3)
            ensemble_prob = ensemble_prob + (1 - ensemble_prob) * pattern_boost
        
        return max(0.0, min(1.0, ensemble_prob))
    
    def _apply_rules(
        self,
        url: str,
        features: URLFeatures,
        trust_eval: TrustEvaluation,
    ) -> Tuple[List[str], Optional[str]]:
        """Apply rule-based checks"""
        if not self.enable_rule_overrides:
            return [], None
        
        flags = []
        override = None
        
        # Rule 1: Whitelisted high-trust domains are safe
        if trust_eval.trust_level.value in ['highest', 'high']:
            if trust_eval.trust_score >= 0.85:
                flags.append('high_trust_domain')
                override = 'safe'
        
        # Rule 2: IP address URLs are suspicious
        if features.has_ip:
            flags.append('ip_address_url')
            if not override:
                override = 'phishing'
        
        # Rule 3: Extremely long URLs
        if features.length > 200:
            flags.append('extremely_long_url')
        
        # Rule 4: Many subdomains
        if features.num_subdomains > 4:
            flags.append('excessive_subdomains')
        
        # Rule 5: Suspicious TLD + suspicious patterns
        if trust_eval.trust_score < 0.2 and len(trust_eval.suspicious_patterns) > 2:
            flags.append('multiple_risk_indicators')
            if not override:
                override = 'phishing'
        
        # Rule 6: Government domains are safe
        if trust_eval.is_government:
            flags.append('government_domain')
            override = 'safe'
        
        # Rule 7: Brand in subdomain (potential impersonation)
        if 'brand-in-subdomain' in str(trust_eval.suspicious_patterns):
            flags.append('potential_brand_impersonation')
            if override == 'safe':
                override = None  # Remove safe override
        
        return flags, override
    
    def _calculate_confidence(
        self,
        ensemble_prob: float,
        model_probs: Dict[str, Optional[float]],
        trust_eval: TrustEvaluation,
    ) -> float:
        """Calculate prediction confidence based on model agreement"""
        valid_probs = [p for p in model_probs.values() if p is not None]
        
        if not valid_probs:
            return trust_eval.confidence
        
        # Base confidence from ensemble certainty
        base_confidence = abs(ensemble_prob - 0.5) * 2  # 0-1 scale
        
        # Model agreement factor
        if len(valid_probs) > 1:
            std_dev = np.std(valid_probs)
            agreement_factor = 1.0 - min(std_dev * 2, 0.5)
        else:
            agreement_factor = 0.8
        
        # Trust confidence contribution
        trust_factor = trust_eval.confidence * 0.3
        
        # Combined confidence
        confidence = (base_confidence * 0.5 + agreement_factor * 0.3 + trust_factor)
        
        return max(0.0, min(1.0, confidence))
    
    def _get_risk_level(self, probability: float, is_whitelisted: bool) -> str:
        """Determine risk level based on probability"""
        if is_whitelisted and probability < 0.1:
            return RiskLevel.VERY_LOW
        
        if probability < 0.1:
            return RiskLevel.VERY_LOW
        elif probability < 0.3:
            return RiskLevel.LOW
        elif probability < 0.6:
            return RiskLevel.MEDIUM
        elif probability < 0.85:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def get_quick_prediction(self, url: str) -> Tuple[bool, float]:
        """
        Quick prediction without detailed analysis.
        
        Returns:
            (is_phishing, probability)
        """
        prediction = self.predict(url)
        return prediction.is_phishing, prediction.phishing_probability


# Singleton instance
_ensemble_predictor: Optional[EnsemblePredictor] = None


def get_ensemble_predictor() -> EnsemblePredictor:
    """Get or create the ensemble predictor instance"""
    global _ensemble_predictor
    
    if _ensemble_predictor is None:
        _ensemble_predictor = EnsemblePredictor()
    
    if not _ensemble_predictor.is_loaded():
        _ensemble_predictor.load_models()
    
    return _ensemble_predictor
