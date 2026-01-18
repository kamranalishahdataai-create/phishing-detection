import { motion } from 'framer-motion'

const steps = [
  {
    number: 1,
    title: 'Install Extension',
    description: 'Add it to your browser in one click — no setup required.',
  },
  {
    number: 2,
    title: 'Browse Normally',
    description: 'The extension runs silently in the background.',
  },
  {
    number: 3,
    title: 'AI Scans',
    description: 'Checks domain reputation and threat indicators.',
  },
  {
    number: 4,
    title: 'Risk Score',
    description: 'Shows Safe, Medium, or High Risk badge.',
  },
  {
    number: 5,
    title: 'View Report',
    description: 'Click badge for detailed analysis.',
  },
  {
    number: 6,
    title: 'Take Action',
    description: 'Block, whitelist, or report in one click.',
  },
  {
    number: 7,
    title: 'Stay Protected',
    description: 'Continuous monitoring across all channels.',
  },
]

const HowItWorksSection = () => {
  return (
    <section id="how-it-works" className="py-20 bg-dark-300">
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
            How It Works
          </h2>
          <p className="text-gray-400 text-lg">
            Simple installation, powerful protection
          </p>
        </motion.div>

        {/* Steps */}
        <div className="flex flex-wrap justify-center items-start gap-4 md:gap-8">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="flex flex-col items-center text-center max-w-[140px]"
            >
              {/* Number Circle */}
              <div className="w-16 h-16 bg-primary-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mb-4 shadow-lg shadow-primary-500/30">
                {step.number}
              </div>
              
              {/* Title */}
              <h3 className="text-primary-400 font-semibold mb-2">
                {step.title}
              </h3>
              
              {/* Description */}
              <p className="text-gray-500 text-sm">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default HowItWorksSection
