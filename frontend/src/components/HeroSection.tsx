import { motion } from 'framer-motion'
import { Star, Chrome, Download, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

const HeroSection = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center pt-16 bg-dark-400 overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-dark-400 via-dark-300 to-dark-400" />
      
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-primary-400/10 rounded-full blur-3xl animate-pulse-slow animation-delay-1000" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {/* Main Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-6">
            <span className="text-primary-400">Welcome to NABIH</span>
            <span className="text-gray-400"> – Your First</span>
            <br />
            <span className="text-gray-500">Line of Defense Against</span>
            <br />
            <span className="text-gray-500">Malicious Links!</span>
          </h1>

          {/* Subtitle */}
          <p className="text-gray-400 text-lg md:text-xl max-w-3xl mx-auto mb-8">
            A next-generation link analysis platform that detects suspicious URLs,
            analyzes risk patterns, and protects your business from phishing, scams, and
            malicious activities — in real time.
          </p>

          {/* Social proof */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-10">
            {/* Users */}
            <div className="flex items-center">
              <div className="flex -space-x-2">
                <img
                  src="https://randomuser.me/api/portraits/women/44.jpg"
                  alt="User"
                  className="w-10 h-10 rounded-full border-2 border-dark-400"
                />
                <img
                  src="https://randomuser.me/api/portraits/men/32.jpg"
                  alt="User"
                  className="w-10 h-10 rounded-full border-2 border-dark-400"
                />
                <img
                  src="https://randomuser.me/api/portraits/women/68.jpg"
                  alt="User"
                  className="w-10 h-10 rounded-full border-2 border-dark-400"
                />
              </div>
              <span className="ml-3 text-gray-400">10,000+ designers</span>
            </div>

            {/* Rating */}
            <div className="flex items-center">
              <div className="flex">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                ))}
              </div>
              <span className="ml-2 text-gray-400">4.9/5 rating</span>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <motion.a
              href="#"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-2 bg-primary-500 hover:bg-primary-600 text-white font-semibold py-3 px-8 rounded-lg transition-all duration-300 shadow-lg shadow-primary-500/25"
            >
              <Chrome className="w-5 h-5" />
              <span>Add to Chrome</span>
            </motion.a>

            <motion.a
              href="#"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-2 bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-8 rounded-lg transition-all duration-300"
            >
              <Download className="w-5 h-5" />
              <span>Download Extension</span>
            </motion.a>

            <Link
              to="/scan"
              className="flex items-center space-x-2 bg-primary-500 hover:bg-primary-600 text-white font-semibold py-3 px-8 rounded-lg transition-all duration-300"
            >
              <span>Get Started</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default HeroSection
