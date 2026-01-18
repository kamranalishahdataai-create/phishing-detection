import { motion } from 'framer-motion'
import { 
  Search, 
  Shield, 
  Zap, 
  Castle, 
  ListChecks, 
  History 
} from 'lucide-react'

const features = [
  {
    icon: Search,
    title: 'Real-Time Link Analysis',
    description: 'Automatically scans URLs for malicious patterns, redirects, cloaking, and phishing attempts.',
    color: 'bg-blue-500',
    bgColor: 'bg-blue-100',
  },
  {
    icon: Shield,
    title: 'Fraud Detection Engine',
    description: 'AI-powered system identifies scam behavior, fake landing pages, blacklisted domains, and suspicious link structures.',
    color: 'bg-red-500',
    bgColor: 'bg-red-100',
  },
  {
    icon: Zap,
    title: 'Instant Risk Score Preview',
    description: 'Every link gets a Security Score (Safe / Medium / High Risk), shown directly in your browser.',
    color: 'bg-yellow-500',
    bgColor: 'bg-yellow-100',
  },
  {
    icon: Castle,
    title: 'Phishing & Scam Detection',
    description: 'Detects impersonation attacks, fake brand pages, misleading CTAs, and fraudulent funnels.',
    color: 'bg-purple-500',
    bgColor: 'bg-purple-100',
  },
  {
    icon: ListChecks,
    title: 'Blacklist & Whitelist Management',
    description: 'Block harmful domains or allow trusted ones — fully customizable for your team.',
    color: 'bg-green-500',
    bgColor: 'bg-green-100',
  },
  {
    icon: History,
    title: 'Link Reputation History',
    description: "See a domain's age, traffic legitimacy, past blacklist records, and security status in one click.",
    color: 'bg-indigo-500',
    bgColor: 'bg-indigo-100',
  },
]

const FeaturesSection = () => {
  return (
    <section id="features" className="py-20 bg-dark-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold gradient-text mb-4">
            Core Security Features
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Comprehensive protection powered by advanced AI and real-time threat intelligence
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="feature-card bg-white rounded-2xl p-6 hover:shadow-xl transition-all duration-300"
            >
              <div className={`w-14 h-14 ${feature.bgColor} rounded-xl flex items-center justify-center mb-4`}>
                <feature.icon className={`w-7 h-7 ${feature.color.replace('bg-', 'text-')}`} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default FeaturesSection
