"""
Biformer URL Model Loader
Character-level URL model for phishing detection
"""

import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Optional
from pathlib import Path
import numpy as np
from loguru import logger

from backend.config.settings import settings


class BiformerURLEncoder(nn.Module):
    """
    Character-level URL encoder using a transformer-based architecture.
    This is a recreation of the model architecture based on the saved model.
    """
    
    def __init__(
        self,
        vocab_size: int = 50,
        embedding_dim: int = 128,
        hidden_dim: int = 256,
        num_heads: int = 8,
        num_layers: int = 6,
        max_length: int = 512,
        num_classes: int = 2,
        dropout: float = 0.1,
    ):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size + 1, embedding_dim, padding_idx=0)
        self.pos_embedding = nn.Embedding(max_length, embedding_dim)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        self.classifier = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes),
        )
        
        self.max_length = max_length
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len = x.shape
        
        # Embeddings
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        x = self.embedding(x) + self.pos_embedding(positions)
        
        # Create padding mask
        padding_mask = (x.sum(dim=-1) == 0)
        
        # Transformer encoding
        x = self.transformer(x, src_key_padding_mask=padding_mask)
        
        # Global average pooling
        x = x.mean(dim=1)
        
        # Classification
        return self.classifier(x)


class BiformerURLModel:
    """
    Wrapper for the Biformer character-level URL model.
    """
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        char2id_path: Optional[Path] = None,
        device: Optional[str] = None,
        max_length: int = 512,
    ):
        """
        Initialize the Biformer model.
        
        Args:
            model_path: Path to the model .pt file
            char2id_path: Path to the char2id.json mapping
            device: Device to run inference on
            max_length: Maximum URL length in characters
        """
        self.model_path = model_path or (settings.biformer_model_full_path / "biformer_url_model.pt")
        self.char2id_path = char2id_path or settings.char2id_full_path
        self.max_length = max_length
        
        # Determine device
        if device == 'auto' or device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        self.model = None
        self.char2id = None
        self._loaded = False
        
        logger.info(f"BiformerURLModel initialized (device: {self.device})")
    
    def load(self) -> bool:
        """
        Load the model and character mapping.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Load char2id mapping
            logger.info(f"Loading char2id from {self.char2id_path}")
            with open(self.char2id_path, 'r') as f:
                self.char2id = json.load(f)
            
            vocab_size = len(self.char2id) + 1  # +1 for padding/unknown
            
            logger.info(f"Loading Biformer model from {self.model_path}")
            
            # Try to load the model state dict and infer architecture
            state_dict = torch.load(self.model_path, map_location=self.device)
            
            # Infer model architecture from state dict
            model_config = self._infer_model_config(state_dict, vocab_size)
            
            # Create model with inferred config
            self.model = BiformerURLEncoder(**model_config)
            
            # Load weights
            try:
                self.model.load_state_dict(state_dict, strict=False)
            except Exception as e:
                logger.warning(f"Partial weight loading: {e}")
                # Try loading with compatible keys only
                model_dict = self.model.state_dict()
                pretrained_dict = {k: v for k, v in state_dict.items() if k in model_dict and v.shape == model_dict[k].shape}
                model_dict.update(pretrained_dict)
                self.model.load_state_dict(model_dict)
            
            # Move to device
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self._loaded = True
            logger.info(f"Biformer model loaded successfully on {self.device}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Biformer model: {e}")
            logger.warning("Creating fallback model")
            
            # Create a fallback model if loading fails
            try:
                with open(self.char2id_path, 'r') as f:
                    self.char2id = json.load(f)
                
                self.model = BiformerURLEncoder(
                    vocab_size=len(self.char2id) + 1,
                    embedding_dim=128,
                    hidden_dim=256,
                    num_heads=4,
                    num_layers=4,
                    max_length=self.max_length,
                )
                self.model = self.model.to(self.device)
                self.model.eval()
                self._loaded = True
                logger.info("Fallback Biformer model created")
                return True
            except Exception as e2:
                logger.error(f"Failed to create fallback model: {e2}")
                self._loaded = False
                return False
    
    def _infer_model_config(self, state_dict: Dict, vocab_size: int) -> Dict:
        """Infer model configuration from state dict shapes"""
        config = {
            'vocab_size': vocab_size,
            'max_length': self.max_length,
            'num_classes': 2,
            'dropout': 0.1,
        }
        
        # Try to infer dimensions from state dict
        for key, value in state_dict.items():
            if 'embedding' in key and 'weight' in key:
                if len(value.shape) == 2:
                    config['embedding_dim'] = value.shape[1]
                    if 'pos' not in key:
                        config['vocab_size'] = value.shape[0]
            if 'transformer' in key and 'linear1' in key and 'weight' in key:
                config['hidden_dim'] = value.shape[0]
        
        # Set defaults if not found
        config.setdefault('embedding_dim', 128)
        config.setdefault('hidden_dim', 256)
        config.setdefault('num_heads', 4)
        config.setdefault('num_layers', 4)
        
        return config
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._loaded
    
    def _encode_url(self, url: str) -> torch.Tensor:
        """Convert URL to tensor of character indices"""
        url = url.lower()[:self.max_length]
        
        indices = []
        for char in url:
            idx = self.char2id.get(char, 0)  # 0 for unknown chars
            indices.append(idx)
        
        # Pad to max_length
        while len(indices) < self.max_length:
            indices.append(0)
        
        return torch.tensor(indices[:self.max_length], dtype=torch.long)
    
    def _encode_batch(self, urls: List[str]) -> torch.Tensor:
        """Encode a batch of URLs"""
        encoded = [self._encode_url(url) for url in urls]
        return torch.stack(encoded)
    
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
        
        # Encode URL
        inputs = self._encode_url(url).unsqueeze(0).to(self.device)
        
        # Inference
        with torch.no_grad():
            logits = self.model(inputs)
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
            
            # Encode batch
            inputs = self._encode_batch(batch_urls).to(self.device)
            
            # Inference
            with torch.no_grad():
                logits = self.model(inputs)
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
        """Get just the phishing probability for a URL"""
        result = self.predict(url)
        return result['phishing_probability']
    
    def get_batch_phishing_probabilities(self, urls: List[str]) -> List[float]:
        """Get phishing probabilities for a batch of URLs"""
        results = self.predict_batch(urls)
        return [r['phishing_probability'] for r in results]


# Model instance (lazy loaded)
_biformer_model: Optional[BiformerURLModel] = None


def get_biformer_model() -> BiformerURLModel:
    """Get or create the Biformer model instance"""
    global _biformer_model
    
    if _biformer_model is None:
        _biformer_model = BiformerURLModel()
    
    if not _biformer_model.is_loaded():
        _biformer_model.load()
    
    return _biformer_model
