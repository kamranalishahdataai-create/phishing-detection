# Phishing Detection Backend

A real-time phishing detection API powered by ensemble machine learning models.

## 🚀 Features

- **Multi-Model Ensemble**: Combines ELECTRA, Biformer (character-level), and LightGBM
- **Domain Trust System**: Multi-level trust evaluation (high/medium/low)
- **Keyword Detection**: Smart keyword-based trust scoring
- **Rule-Based Overrides**: Additional safety rules for edge cases
- **External Services**: Google Safe Browsing, WHOIS, DNS checks
- **RESTful API**: FastAPI with automatic OpenAPI documentation
- **Caching**: Built-in result caching with SQLite/PostgreSQL

## 📁 Project Structure

```
backend/
├── api/
│   ├── routes.py          # API endpoints
│   └── schemas.py         # Pydantic models
├── config/
│   ├── settings.py        # Configuration management
│   └── constants.py       # Trusted domains, keywords, etc.
├── models/
│   ├── electra_model.py   # ELECTRA transformer model
│   ├── biformer_model.py  # Character-level model
│   └── lgbm_model.py      # LightGBM feature model
├── services/
│   ├── ensemble_predictor.py  # Ensemble logic
│   ├── domain_trust.py        # Trust evaluation
│   ├── feature_extractor.py   # URL feature extraction
│   └── external_services.py   # External APIs
├── database/
│   └── models.py          # SQLAlchemy models
├── main.py                # FastAPI application
├── run.py                 # Startup script
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
└── docker-compose.yml    # Docker Compose setup
```

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- CUDA (optional, for GPU acceleration)

### Local Setup

1. **Create virtual environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run the server**:
```bash
python run.py
```

### Docker Setup

```bash
docker-compose up -d
```

## 📚 API Documentation

After starting the server, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/scan` | POST | Scan single URL with details |
| `/api/v1/scan/quick` | GET | Quick URL scan |
| `/api/v1/scan/batch` | POST | Scan multiple URLs |
| `/api/v1/domain/trust` | GET | Domain trust analysis |
| `/api/v1/url/features` | GET | URL feature extraction |
| `/health` | GET | Health check |

### Example: Scan URL

```bash
curl -X POST "http://localhost:8000/api/v1/scan" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "include_details": true}'
```

Response:
```json
{
  "url": "https://example.com",
  "is_phishing": false,
  "phishing_probability": 0.023,
  "confidence": 0.89,
  "risk_level": "very_low",
  "status": "safe",
  "recommendation": "This URL appears safe. Normal caution advised."
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | false | Enable debug mode |
| `PORT` | 8000 | Server port |
| `MODEL_DEVICE` | auto | ML device (cuda/cpu/auto) |
| `PHISHING_THRESHOLD` | 0.0863 | Classification threshold |
| `ELECTRA_WEIGHT` | 0.40 | ELECTRA model weight |
| `BIFORMER_WEIGHT` | 0.35 | Biformer model weight |
| `LGBM_WEIGHT` | 0.25 | LightGBM model weight |

### Trust System

The domain trust system uses multiple levels:

1. **Highest Trust** (0.85-1.0): Top global sites (Google, Microsoft, etc.)
2. **High Trust** (0.70-0.85): Known trusted domains
3. **Medium Trust** (0.50-0.70): Popular domains
4. **Low Trust** (0.30-0.50): Unknown domains
5. **Suspicious** (0.15-0.30): Shows suspicious patterns
6. **Dangerous** (0-0.15): Matches phishing patterns

## 🔒 Security Features

- **IP-based URL detection**: Automatic flagging
- **Punycode detection**: Homograph attack protection
- **Brand impersonation**: Subdomain analysis
- **Excessive subdomain detection**
- **Suspicious TLD flagging**

## 📊 Model Details

| Model | Type | Input | Weight |
|-------|------|-------|--------|
| ELECTRA | Transformer | Full URL | 40% |
| Biformer | Character CNN | URL chars | 35% |
| LightGBM | Gradient Boosting | URL features | 25% |

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=backend --cov-report=html
```

## 📈 Performance

- Average response time: ~50ms (CPU), ~20ms (GPU)
- Throughput: ~100 requests/second (single worker)
- Model loading time: ~10s (first request)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details.
