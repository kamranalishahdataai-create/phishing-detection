"""
Electra URL Model Loader
Loads and runs inference on the fine-tuned ELECTRA model for URL classification
"""

import torch
import torch.nn.functional as F
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
from loguru import logger

from transformers import (
    ElectraForSequenceClassification,
    ElectraTokenizer,
    AutoTokenizer,
    AutoModelForSequenceClassification,
)

from backend.config.settings import settings


class ElectraURLModel:
    """
    Wrapper for the fine-tuned ELECTRA model for URL phishing detection.
    
    The model classifies URLs as either legitimate (0) or phishing (1).
    """
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        device: Optional[str] = None,
        max_length: int = 512,
    ):
        """
        Initialize the ELECTRA model.
        
        Args:
            model_path: Path to the model directory
            device: Device to run inference on ('cuda', 'cpu', or 'auto')
            max_length: Maximum token length for URLs
        """
        self.model_path = model_path or settings.electra_model_full_path
        self.max_length = max_length
        
        # Determine device
        if device == 'auto' or device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        self.model = None
        self.tokenizer = None
        self._loaded = False
        
        logger.info(f"ElectraURLModel initialized (device: {self.device})")
    
    def load(self) -> bool:
        """
        Load the model and tokenizer.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading ELECTRA model from {self.model_path}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.model_path),
                local_files_only=True,
            )
            
            # Load model
            self.model = AutoModelForSequenceClassification.from_pretrained(
                str(self.model_path),
                local_files_only=True,
            )
            
            # Move to device
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self._loaded = True
            logger.info(f"ELECTRA model loaded successfully on {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load ELECTRA model: {e}")
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
        
        # Tokenize
        inputs = self.tokenizer(
            url,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt',
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=-1)
        
        # Extract results
        probs = probabilities.cpu().numpy()[0]
        predicted_class = int(np.argmax(probs))
        
        return {
            'url': url,
            'predicted_class': predicted_class,
            'phishing_probability': float(probs[1]) if len(probs) > 1 else float(probs[0]),
            'legitimate_probability': float(probs[0]),
            'confidence': float(np.max(probs)),
        }
    
    def predict_batch(self, urls: List[str], batch_size: int = 32) -> List[Dict]:
        """
        Predict phishing probability for a batch of URLs.
        
        Args:
            urls: List of URLs to classify
            batch_size: Batch size for inference
            
        Returns:
            List of prediction dictionaries
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        results = []
        
        for i in range(0, len(urls), batch_size):
            batch_urls = urls[i:i + batch_size]
            
            # Tokenize batch
            inputs = self.tokenizer(
                batch_urls,
                max_length=self.max_length,
                truncation=True,
                padding='max_length',
                return_tensors='pt',
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = F.softmax(logits, dim=-1)
            
            # Process results
            probs_batch = probabilities.cpu().numpy()
            
            for j, url in enumerate(batch_urls):
                probs = probs_batch[j]
                predicted_class = int(np.argmax(probs))
                
                results.append({
                    'url': url,
                    'predicted_class': predicted_class,
                    'phishing_probability': float(probs[1]) if len(probs) > 1 else float(probs[0]),
                    'legitimate_probability': float(probs[0]),
                    'confidence': float(np.max(probs)),
                })
        
        return results
    
    def get_phishing_probability(self, url: str) -> float:
        """
        Get just the phishing probability for a URL.
        
        Args:
            url: URL to classify
            
        Returns:
            Phishing probability (0.0 - 1.0)
        """
        result = self.predict(url)
        return result['phishing_probability']
    
    def get_batch_phishing_probabilities(self, urls: List[str]) -> List[float]:
        """
        Get phishing probabilities for a batch of URLs.
        
        Args:
            urls: List of URLs to classify
            
        Returns:
            List of phishing probabilities
        """
        results = self.predict_batch(urls)
        return [r['phishing_probability'] for r in results]


# Model instance (lazy loaded)
_electra_model: Optional[ElectraURLModel] = None


def get_electra_model() -> ElectraURLModel:
    """Get or create the ELECTRA model instance"""
    global _electra_model
    
    if _electra_model is None:
        _electra_model = ElectraURLModel()
    
    if not _electra_model.is_loaded():
        _electra_model.load()
    
    return _electra_model
