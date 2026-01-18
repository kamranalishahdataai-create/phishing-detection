import { useState } from 'react'
import { motion } from 'framer-motion'
import { Check } from 'lucide-react'

const plans = [
  {
    name: 'Free',
    monthlyPrice: 0,
    yearlyPrice: 0,
    features: ['Free for One Week', 'Basic components', 'HTML export'],
    featured: false,
  },
  {
    name: 'Monthly',
    monthlyPrice: 5,
    yearlyPrice: 5,
    features: ['Unlimited generations', 'All components', 'React & Vue export', 'Priority support'],
    featured: true,
    badge: 'Annual',
  },
  {
    name: 'Yearly',
    monthlyPrice: 15,
    yearlyPrice: 15,
    features: ['Everything in Pro', '5 team members', 'Shared workspace', 'Advanced analytics'],
    featured: false,
  },
]

const PricingSection = () => {
  const [isYearly, setIsYearly] = useState(false)

  return (
    <section id="pricing" className="py-20 bg-dark-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold gradient-text mb-4">
            Simple Pricing
          </h2>
          <p className="text-gray-400 text-lg mb-8">
            Choose the plan that works for you
          </p>

          {/* Toggle */}
          <div className="flex items-center justify-center gap-4">
            <span className="text-gray-400">Plans & Pricing</span>
            <div className="flex bg-dark-300 rounded-full p-1">
              <button
                onClick={() => setIsYearly(false)}
                className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${
                  !isYearly ? 'bg-primary-500 text-white' : 'text-gray-400'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setIsYearly(true)}
                className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${
                  isYearly ? 'bg-primary-500 text-white' : 'text-gray-400'
                }`}
              >
                Yearly
              </button>
            </div>
          </div>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={`relative rounded-2xl p-8 ${
                plan.featured
                  ? 'bg-primary-500 text-white transform scale-105 shadow-2xl shadow-primary-500/30'
                  : 'bg-dark-300 border border-gray-700'
              }`}
            >
              {/* Badge */}
              {plan.badge && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-primary-600 text-white text-sm px-4 py-1 rounded-full">
                    {plan.badge}
                  </span>
                </div>
              )}

              {/* Plan Name */}
              <h3 className={`text-xl font-bold mb-2 ${plan.featured ? 'text-white' : 'text-primary-400'}`}>
                {plan.name}
              </h3>

              {/* Price */}
              <div className="mb-6">
                <span className="text-4xl font-bold">
                  ${isYearly ? plan.yearlyPrice : plan.monthlyPrice}
                </span>
                <span className={plan.featured ? 'text-white/70' : 'text-gray-400'}>
                  /{plan.name === 'Yearly' ? 'Yearly' : 'mo'}
                </span>
              </div>

              {/* Features */}
              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <Check className={`w-5 h-5 ${plan.featured ? 'text-white' : 'text-primary-500'}`} />
                    <span className={plan.featured ? 'text-white/90' : 'text-gray-400'}>
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <button
                className={`w-full py-3 rounded-lg font-semibold transition-all ${
                  plan.featured
                    ? 'bg-primary-600 hover:bg-primary-700 text-white'
                    : 'bg-dark-400 hover:bg-dark-200 text-white border border-gray-600'
                }`}
              >
                Get Started
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default PricingSection
