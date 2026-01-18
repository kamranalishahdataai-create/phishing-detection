import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronUp, ChevronDown } from 'lucide-react'

const faqs = [
  {
    question: '1. What is NABIH?',
    answer: 'NABIH is a browser-based security extension that protects you from malicious links in real time. It analyzes URLs instantly to detect phishing attempts, scams, malware, and suspicious redirects before you click.',
  },
  {
    question: '2. How does NABIH detect malicious links?',
    answer: 'NABIH uses advanced AI models including ELECTRA transformer, Biformer character-level analysis, and LightGBM ensemble to analyze URLs. It checks domain reputation, URL patterns, SSL certificates, and cross-references with known threat databases.',
  },
  {
    question: '3. Is my browsing data private?',
    answer: 'Yes, absolutely. NABIH processes URLs locally in your browser and only sends anonymized data to our servers for threat analysis. We never store your browsing history or personal information.',
  },
  {
    question: '4. Does NABIH slow down my browser?',
    answer: 'No, NABIH is designed to be lightweight and efficient. It runs in the background with minimal resource usage and analyzes links instantly without affecting your browsing speed.',
  },
  {
    question: '5. Is there a free version of NABIH?',
    answer: 'Yes! We offer a free tier that includes basic protection features. You can upgrade to our paid plans for advanced features like detailed reports, team management, and priority support.',
  },
  {
    question: '6. Who can benefit from NABIH?',
    answer: 'Everyone! Whether you\'re an individual user, small business, or enterprise, NABIH protects you from phishing attacks, scam websites, and malicious links that could compromise your security.',
  },
  {
    question: '7. How do I start using NABIH?',
    answer: 'Simply click "Add to Chrome" to install the extension. No account required to start! The extension will automatically begin protecting you as you browse.',
  },
]

const FAQSection = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  return (
    <section id="faq" className="py-20 bg-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
            General FAQs
          </h2>
        </motion.div>

        {/* FAQ Items */}
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.05 }}
              className="border-b border-gray-200 last:border-b-0"
            >
              <button
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                className="w-full flex items-center justify-between py-6 text-left"
              >
                <span className={`text-lg font-semibold ${
                  openIndex === index ? 'text-primary-500' : 'text-gray-900'
                }`}>
                  {faq.question}
                </span>
                {openIndex === index ? (
                  <ChevronUp className="w-5 h-5 text-gray-500" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-500" />
                )}
              </button>
              
              <AnimatePresence>
                {openIndex === index && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <p className="pb-6 text-gray-600 leading-relaxed">
                      {faq.answer}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default FAQSection
