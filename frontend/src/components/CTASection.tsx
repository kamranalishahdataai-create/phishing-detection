import { motion } from 'framer-motion'
import { Chrome } from 'lucide-react'

const CTASection = () => {
  return (
    <section className="py-20 bg-gradient-to-b from-blue-50 to-blue-100">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <p className="text-gray-700 text-lg md:text-xl mb-8">
            Install the extension and get real-time protection against dangerous links.
          </p>

          <motion.a
            href="#"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="inline-flex items-center space-x-2 bg-primary-500 hover:bg-primary-600 text-white font-semibold py-4 px-10 rounded-xl transition-all duration-300 shadow-lg shadow-primary-500/30 text-lg"
          >
            <span>Install Extension Now</span>
          </motion.a>

          {/* Chrome badge */}
          <div className="flex items-center justify-center gap-2 mt-6 text-primary-600">
            <Chrome className="w-5 h-5" />
            <span className="font-medium">Chrome</span>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default CTASection
