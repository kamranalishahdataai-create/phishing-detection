import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface ScanResult {
  url: string
  is_phishing: boolean
  confidence: number
  risk_level: 'safe' | 'low' | 'medium' | 'high' | 'critical'
  risk_score: number
  trust_level: string
  trust_score: number
  model_predictions: {
    electra: number
    biformer: number
    lgbm: number
  }
  features: {
    url_length: number
    has_ip: boolean
    has_suspicious_tld: boolean
    subdomain_count: number
    has_https: boolean
    entropy: number
  }
  warnings: string[]
  scan_time: number
  timestamp: string
}

export interface DomainTrust {
  domain: string
  trust_level: string
  trust_score: number
  is_known_safe: boolean
  is_government: boolean
  is_educational: boolean
  warnings: string[]
}

export interface HealthStatus {
  status: string
  models_loaded: boolean
  version: string
  timestamp: string
}

// Scan a single URL
export const scanUrl = async (url: string, includeFeatures: boolean = true): Promise<ScanResult> => {
  const response = await api.post('/api/v1/scan', {
    url,
    include_features: includeFeatures,
    use_trust_system: true,
    strict_mode: false,
  })
  return response.data
}

// Quick scan (faster, less details)
export const quickScan = async (url: string): Promise<ScanResult> => {
  const response = await api.post('/api/v1/scan/quick', { url })
  return response.data
}

// Batch scan multiple URLs
export const batchScan = async (urls: string[]): Promise<ScanResult[]> => {
  const response = await api.post('/api/v1/scan/batch', { urls })
  return response.data.results
}

// Get domain trust information
export const getDomainTrust = async (domain: string): Promise<DomainTrust> => {
  const response = await api.get(`/api/v1/domain/trust`, {
    params: { domain },
  })
  return response.data
}

// Get URL features
export const getUrlFeatures = async (url: string) => {
  const response = await api.get('/api/v1/url/features', {
    params: { url },
  })
  return response.data
}

// Health check
export const checkHealth = async (): Promise<HealthStatus> => {
  const response = await api.get('/health')
  return response.data
}

export default api
