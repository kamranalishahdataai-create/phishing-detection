import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Shield, 
  History, 
  Settings, 
  BarChart3, 
  Trash2,
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  Clock,
  ExternalLink
} from 'lucide-react'
import { useStore } from '../store'
import { checkHealth, HealthStatus } from '../api'

const DashboardPage = () => {
  const [activeTab, setActiveTab] = useState<'history' | 'stats' | 'settings'>('history')
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const { 
    scanHistory, 
    clearHistory, 
    autoScan, 
    setAutoScan,
    showNotifications,
    setShowNotifications,
    strictMode,
    setStrictMode
  } = useStore()

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const status = await checkHealth()
        setHealth(status)
      } catch (error) {
        console.error('Failed to fetch health:', error)
      }
    }
    fetchHealth()
  }, [])

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'safe':
        return <ShieldCheck className="w-5 h-5 text-green-500" />
      case 'low':
        return <Shield className="w-5 h-5 text-blue-500" />
      case 'medium':
        return <ShieldAlert className="w-5 h-5 text-yellow-500" />
      case 'high':
      case 'critical':
        return <ShieldX className="w-5 h-5 text-red-500" />
      default:
        return <Shield className="w-5 h-5 text-gray-500" />
    }
  }

  const stats = {
    totalScans: scanHistory.length,
    safeUrls: scanHistory.filter(s => s.result.risk_level === 'safe').length,
    riskyUrls: scanHistory.filter(s => ['high', 'critical', 'medium'].includes(s.result.risk_level)).length,
  }

  return (
    <div className="min-h-screen pt-24 pb-16 bg-dark-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
          <div className="flex items-center gap-2 text-gray-400">
            <div className={`w-2 h-2 rounded-full ${health?.models_loaded ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm">
              {health?.models_loaded ? 'AI Models Active' : 'Connecting...'}
            </span>
            {health && (
              <span className="text-sm">• v{health.version}</span>
            )}
          </div>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          <div className="glass rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-400">Total Scans</span>
              <BarChart3 className="w-5 h-5 text-primary-400" />
            </div>
            <p className="text-3xl font-bold text-white">{stats.totalScans}</p>
          </div>
          <div className="glass rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-400">Safe URLs</span>
              <ShieldCheck className="w-5 h-5 text-green-500" />
            </div>
            <p className="text-3xl font-bold text-green-400">{stats.safeUrls}</p>
          </div>
          <div className="glass rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-400">Risky URLs</span>
              <ShieldX className="w-5 h-5 text-red-500" />
            </div>
            <p className="text-3xl font-bold text-red-400">{stats.riskyUrls}</p>
          </div>
        </motion.div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-700">
          <button
            onClick={() => setActiveTab('history')}
            className={`flex items-center gap-2 pb-4 px-2 border-b-2 transition-colors ${
              activeTab === 'history'
                ? 'border-primary-500 text-white'
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            <History className="w-4 h-4" />
            Scan History
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`flex items-center gap-2 pb-4 px-2 border-b-2 transition-colors ${
              activeTab === 'settings'
                ? 'border-primary-500 text-white'
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'history' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass rounded-xl overflow-hidden"
          >
            {scanHistory.length === 0 ? (
              <div className="p-12 text-center">
                <History className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No scan history yet</p>
                <p className="text-gray-500 text-sm">Start scanning URLs to see your history</p>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between p-4 border-b border-gray-700">
                  <h3 className="text-white font-medium">Recent Scans</h3>
                  <button
                    onClick={clearHistory}
                    className="flex items-center gap-2 text-red-400 hover:text-red-300 text-sm"
                  >
                    <Trash2 className="w-4 h-4" />
                    Clear History
                  </button>
                </div>
                <div className="divide-y divide-gray-700">
                  {scanHistory.slice(0, 20).map((scan) => (
                    <div
                      key={scan.id}
                      className="p-4 hover:bg-dark-300 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        {getRiskIcon(scan.result.risk_level)}
                        <div className="flex-1 min-w-0">
                          <p className="text-white truncate">{scan.result.url}</p>
                          <div className="flex items-center gap-4 text-sm text-gray-400">
                            <span className="capitalize">{scan.result.risk_level}</span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {new Date(scan.timestamp).toLocaleString()}
                            </span>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-400">Risk Score</p>
                          <p className={`font-bold ${
                            scan.result.risk_score > 0.7 ? 'text-red-400' :
                            scan.result.risk_score > 0.3 ? 'text-yellow-400' :
                            'text-green-400'
                          }`}>
                            {(scan.result.risk_score * 100).toFixed(0)}%
                          </p>
                        </div>
                        <a
                          href={scan.result.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-2 text-gray-400 hover:text-white transition-colors"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </motion.div>
        )}

        {activeTab === 'settings' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass rounded-xl p-6"
          >
            <h3 className="text-white font-medium mb-6">Extension Settings</h3>
            
            <div className="space-y-6">
              {/* Auto Scan */}
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Auto Scan</p>
                  <p className="text-gray-400 text-sm">Automatically scan URLs as you browse</p>
                </div>
                <button
                  onClick={() => setAutoScan(!autoScan)}
                  className={`w-12 h-6 rounded-full transition-colors relative ${
                    autoScan ? 'bg-primary-500' : 'bg-dark-300'
                  }`}
                >
                  <div
                    className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                      autoScan ? 'left-7' : 'left-1'
                    }`}
                  />
                </button>
              </div>

              {/* Notifications */}
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Show Notifications</p>
                  <p className="text-gray-400 text-sm">Get alerts for dangerous URLs</p>
                </div>
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className={`w-12 h-6 rounded-full transition-colors relative ${
                    showNotifications ? 'bg-primary-500' : 'bg-dark-300'
                  }`}
                >
                  <div
                    className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                      showNotifications ? 'left-7' : 'left-1'
                    }`}
                  />
                </button>
              </div>

              {/* Strict Mode */}
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Strict Mode</p>
                  <p className="text-gray-400 text-sm">Block access to suspicious URLs</p>
                </div>
                <button
                  onClick={() => setStrictMode(!strictMode)}
                  className={`w-12 h-6 rounded-full transition-colors relative ${
                    strictMode ? 'bg-primary-500' : 'bg-dark-300'
                  }`}
                >
                  <div
                    className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                      strictMode ? 'left-7' : 'left-1'
                    }`}
                  />
                </button>
              </div>
            </div>

            {/* API Status */}
            <div className="mt-8 pt-6 border-t border-gray-700">
              <h4 className="text-white font-medium mb-4">API Status</h4>
              <div className="bg-dark-300 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400">Connection</span>
                  <span className={health ? 'text-green-400' : 'text-red-400'}>
                    {health ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400">Models Status</span>
                  <span className={health?.models_loaded ? 'text-green-400' : 'text-yellow-400'}>
                    {health?.models_loaded ? 'Loaded' : 'Loading...'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Version</span>
                  <span className="text-white">{health?.version || 'N/A'}</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default DashboardPage
