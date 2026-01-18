"""
LightGBM Model Loader
Loads the LightGBM model for URL feature-based classification
"""

import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
from loguru import logger

import lightgbm as lgb

from backend.config.settings import settings
from backend.services.feature_extractor import url_feature_extractor


class LGBMURLModel:
    """
    Wrapper for the LightGBM URL classification model.
    
    This model uses extracted URL features (length, entropy, etc.)
    to predict phishing probability.
    """
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
    ):
        """
        Initialize the LightGBM model.
        
        Args:
            model_path: Path to the model file (.txt)
        """
        self.model_path = model_path or settings.lgbm_model_full_path
        self.model = None
        self._loaded = False
        
        logger.info(f"LGBMURLModel initialized")
    
    def load(self) -> bool:
        """
        Load the LightGBM model.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading LightGBM model from {self.model_path}")
            
            # Load the model
            self.model = lgb.Booster(model_file=str(self.model_path))
            
            self._loaded = True
            logger.info("LightGBM model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load LightGBM model: {e}")
            self._loaded = False
            return False
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._loaded
    
    def predict(self, url: str) -> Dict:
        """
        Predict phishing probability for a single URL.
        
        Args:
            url: URL to classify
            
        Returns:
            Dictionary with prediction results
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        # Extract features
        features = url_feature_extractor.extract_lgbm_features(url)
        features_array = np.array([features])
        
        # Predict (LightGBM returns raw scores, apply sigmoid for probability)
        raw_score = self.model.predict(features_array)[0]
        probability = 1 / (1 + np.exp(-raw_score))  # Sigmoid
        
        predicted_class = 1 if probability > 0.5 else 0
        
        return {
            'url': url,
            'predicted_class': predicted_class,
            'phishing_probability': float(probability),
            'legitimate_probability': float(1 - probability),
            'confidence': float(max(probability, 1 - probability)),
            'raw_score': float(raw_score),
        }
    
    def predict_batch(self, urls: List[str]) -> List[Dict]:
        """
        Predict phishing probability for a batch of URLs.
        
        Args:
            urls: List of URLs to classify
            
        Returns:
            List of prediction dictionaries
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        # Extract features for all URLs
        features_list = url_feature_extractor.extract_batch_lgbm_features(urls)
        features_array = np.array(features_list)
        
        # Predict
        raw_scores = self.model.predict(features_array)
        probabilities = 1 / (1 + np.exp(-raw_scores))  # Sigmoid
        
        results = []
        for i, url in enumerate(urls):
            prob = probabilities[i]
            predicted_class = 1 if prob > 0.5 else 0
            
            results.append({
                'url': url,
                'predicted_class': predicted_class,
                'phishing_probability': float(prob),
                'legitimate_probability': float(1 - prob),
                'confidence': float(max(prob, 1 - prob)),
                'raw_score': float(raw_scores[i]),
            })
        
        return results
    
    def get_phishing_probability(self, url: str) -> float:
        """Get just the phishing probability for a URL"""
        result = self.predict(url)
        return result['phishing_probability']
    
    def get_batch_phishing_probabilities(self, urls: List[str]) -> List[float]:
        """Get phishing probabilities for a batch of URLs"""
        results = self.predict_batch(urls)
        return [r['phishing_probability'] for r in results]


# Model instance (lazy loaded)
_lgbm_model: Optional[LGBMURLModel] = None


def get_lgbm_model() -> LGBMURLModel:
    """Get or create the LightGBM model instance"""
    global _lgbm_model
    
    if _lgbm_model is None:
        _lgbm_model = LGBMURLModel()
    
    if not _lgbm_model.is_loaded():
        _lgbm_model.load()
    
    return _lgbm_model
