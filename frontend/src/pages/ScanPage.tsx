import { motion } from 'framer-motion'
import ScannerBox from '../components/ScannerBox'
import { Shield } from 'lucide-react'

const ScanPage = () => {
  return (
    <div className="min-h-screen pt-24 pb-16 bg-dark-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Shield className="w-10 h-10 text-primary-500" />
            <h1 className="text-3xl md:text-4xl font-bold text-white">
              URL Scanner
            </h1>
          </div>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Enter any URL to analyze it for phishing, scams, and malicious content.
            Our AI-powered system will provide a comprehensive security assessment.
          </p>
        </motion.div>

        {/* Scanner Component */}
        <ScannerBox />

        {/* Tips */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-12 glass rounded-2xl p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-4">Security Tips</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="text-primary-400 font-medium mb-2">Check Before You Click</h4>
              <p className="text-gray-400 text-sm">
                Always verify URLs in emails and messages before clicking, especially from unknown senders.
              </p>
            </div>
            <div>
              <h4 className="text-primary-400 font-medium mb-2">Look for HTTPS</h4>
              <p className="text-gray-400 text-sm">
                Secure websites use HTTPS. However, phishing sites can also use HTTPS, so check the domain carefully.
              </p>
            </div>
            <div>
              <h4 className="text-primary-400 font-medium mb-2">Watch for Typos</h4>
              <p className="text-gray-400 text-sm">
                Phishers often use domains that look similar to legitimate ones (e.g., g00gle.com instead of google.com).
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default ScanPage
