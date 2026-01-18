import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, 
  Shield, 
  ShieldCheck, 
  ShieldAlert, 
  ShieldX,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Loader2,
  ExternalLink,
  Info
} from 'lucide-react'
import { scanUrl, ScanResult } from '../api'
import { useStore } from '../store'

const ScannerBox = () => {
  const [url, setUrl] = useState('')
  const [isScanning, setIsScanning] = useState(false)
  const [result, setResult] = useState<ScanResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const { addScan } = useStore()

  const handleScan = async () => {
    if (!url.trim()) {
      setError('Please enter a URL to scan')
      return
    }

    // Add protocol if missing
    let urlToScan = url.trim()
    if (!urlToScan.startsWith('http://') && !urlToScan.startsWith('https://')) {
      urlToScan = 'https://' + urlToScan
    }

    setIsScanning(true)
    setError(null)
    setResult(null)

    try {
      const scanResult = await scanUrl(urlToScan)
      setResult(scanResult)
      addScan(scanResult)
    } catch (err) {
      console.error('Scan error:', err)
      setError('Failed to scan URL. Please check if the backend server is running.')
    } finally {
      setIsScanning(false)
    }
  }

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'safe':
        return <ShieldCheck className="w-16 h-16 text-green-500" />
      case 'low':
        return <Shield className="w-16 h-16 text-blue-500" />
      case 'medium':
        return <ShieldAlert className="w-16 h-16 text-yellow-500" />
      case 'high':
      case 'critical':
        return <ShieldX className="w-16 h-16 text-red-500" />
      default:
        return <Shield className="w-16 h-16 text-gray-500" />
    }
  }

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'safe':
        return 'bg-green-500/10 border-green-500/30 text-green-500'
      case 'low':
        return 'bg-blue-500/10 border-blue-500/30 text-blue-500'
      case 'medium':
        return 'bg-yellow-500/10 border-yellow-500/30 text-yellow-500'
      case 'high':
      case 'critical':
        return 'bg-red-500/10 border-red-500/30 text-red-500'
      default:
        return 'bg-gray-500/10 border-gray-500/30 text-gray-500'
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Scanner Input */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-6 mb-6"
      >
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleScan()}
              placeholder="Enter URL to scan (e.g., example.com)"
              className="w-full bg-dark-300 border border-gray-700 rounded-xl py-4 pl-12 pr-4 text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 transition-colors"
            />
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleScan}
            disabled={isScanning}
            className="bg-primary-500 hover:bg-primary-600 disabled:bg-primary-500/50 text-white font-semibold py-4 px-8 rounded-xl transition-all flex items-center justify-center gap-2"
          >
            {isScanning ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Scanning...
              </>
            ) : (
              <>
                <Shield className="w-5 h-5" />
                Scan URL
              </>
            )}
          </motion.button>
        </div>

        {/* Error message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-3 text-red-400"
          >
            <XCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </motion.div>
        )}
      </motion.div>

      {/* Scan Result */}
      <AnimatePresence mode="wait">
        {result && (
          <motion.div
            key="result"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass rounded-2xl p-6"
          >
            {/* Result Header */}
            <div className="flex items-center gap-6 mb-6">
              <div className={`p-4 rounded-2xl ${getRiskColor(result.risk_level)}`}>
                {getRiskIcon(result.risk_level)}
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-white mb-1 capitalize">
                  {result.risk_level === 'safe' ? 'Safe Website' : `${result.risk_level} Risk Detected`}
                </h3>
                <p className="text-gray-400 text-sm break-all">{result.url}</p>
              </div>
            </div>

            {/* Risk Score */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-dark-300 rounded-xl p-4">
                <p className="text-gray-400 text-sm mb-1">Risk Score</p>
                <p className="text-2xl font-bold text-white">{(result.risk_score * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-dark-300 rounded-xl p-4">
                <p className="text-gray-400 text-sm mb-1">Confidence</p>
                <p className="text-2xl font-bold text-white">{(result.confidence * 100).toFixed(1)}%</p>
              </div>
              <div className="bg-dark-300 rounded-xl p-4">
                <p className="text-gray-400 text-sm mb-1">Trust Level</p>
                <p className="text-xl font-bold text-white capitalize">{result.trust_level}</p>
              </div>
              <div className="bg-dark-300 rounded-xl p-4">
                <p className="text-gray-400 text-sm mb-1">Scan Time</p>
                <p className="text-xl font-bold text-white">{result.scan_time?.toFixed(2) || 0}s</p>
              </div>
            </div>

            {/* Model Predictions */}
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Info className="w-5 h-5 text-primary-400" />
                AI Model Analysis
              </h4>
              <div className="grid grid-cols-3 gap-4">
                {result.model_predictions && Object.entries(result.model_predictions).map(([model, score]) => (
                  <div key={model} className="bg-dark-300 rounded-xl p-4">
                    <p className="text-gray-400 text-sm capitalize mb-2">{model}</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-dark-400 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            score > 0.7 ? 'bg-red-500' : score > 0.3 ? 'bg-yellow-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${score * 100}%` }}
                        />
                      </div>
                      <span className="text-white text-sm font-medium">
                        {(score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Warnings */}
            {result.warnings && result.warnings.length > 0 && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-yellow-400" />
                  Warnings
                </h4>
                <div className="space-y-2">
                  {result.warnings.map((warning, index) => (
                    <div
                      key={index}
                      className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg px-4 py-3 text-yellow-400 text-sm"
                    >
                      {warning}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Features */}
            {result.features && (
              <div>
                <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-primary-400" />
                  URL Features
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  <div className="bg-dark-300 rounded-lg px-4 py-3">
                    <span className="text-gray-400 text-sm">URL Length</span>
                    <p className="text-white font-medium">{result.features.url_length}</p>
                  </div>
                  <div className="bg-dark-300 rounded-lg px-4 py-3">
                    <span className="text-gray-400 text-sm">Has HTTPS</span>
                    <p className={`font-medium ${result.features.has_https ? 'text-green-400' : 'text-red-400'}`}>
                      {result.features.has_https ? 'Yes' : 'No'}
                    </p>
                  </div>
                  <div className="bg-dark-300 rounded-lg px-4 py-3">
                    <span className="text-gray-400 text-sm">Has IP Address</span>
                    <p className={`font-medium ${result.features.has_ip ? 'text-red-400' : 'text-green-400'}`}>
                      {result.features.has_ip ? 'Yes' : 'No'}
                    </p>
                  </div>
                  <div className="bg-dark-300 rounded-lg px-4 py-3">
                    <span className="text-gray-400 text-sm">Subdomains</span>
                    <p className="text-white font-medium">{result.features.subdomain_count}</p>
                  </div>
                  <div className="bg-dark-300 rounded-lg px-4 py-3">
                    <span className="text-gray-400 text-sm">Suspicious TLD</span>
                    <p className={`font-medium ${result.features.has_suspicious_tld ? 'text-red-400' : 'text-green-400'}`}>
                      {result.features.has_suspicious_tld ? 'Yes' : 'No'}
                    </p>
                  </div>
                  <div className="bg-dark-300 rounded-lg px-4 py-3">
                    <span className="text-gray-400 text-sm">Entropy</span>
                    <p className="text-white font-medium">{result.features.entropy?.toFixed(2) || 'N/A'}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4 mt-6">
              <a
                href={result.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 bg-dark-300 hover:bg-dark-200 text-white font-medium py-3 px-6 rounded-xl transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                Visit Site
              </a>
              <button
                onClick={() => setResult(null)}
                className="flex-1 bg-primary-500 hover:bg-primary-600 text-white font-medium py-3 px-6 rounded-xl transition-colors"
              >
                Scan Another
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default ScannerBox
