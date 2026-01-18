import { Link } from 'react-router-dom'
import { Instagram, Globe } from 'lucide-react'

const Footer = () => {
  return (
    <footer className="bg-dark-400 border-t border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-1">
            <div className="flex items-center space-x-1 mb-4">
              <div className="flex space-x-0.5">
                <div className="w-1 h-8 bg-gray-400 rounded"></div>
                <div className="w-1 h-6 bg-gray-400 rounded mt-1"></div>
                <div className="w-1 h-8 bg-gray-400 rounded"></div>
                <div className="w-1 h-6 bg-gray-400 rounded mt-1"></div>
              </div>
            </div>
            <p className="text-gray-400 text-sm mb-4">
              The All-in-One Chrome Extension Hub — Turn Ideas Into Extensions, Fast.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-white transition-colors p-2 rounded-full border border-gray-700 hover:border-gray-500">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors p-2 rounded-full border border-gray-700 hover:border-gray-500">
                <Globe className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Company */}
          <div>
            <h3 className="text-primary-400 font-semibold mb-4">Company</h3>
            <ul className="space-y-3">
              <li><Link to="#" className="text-gray-400 hover:text-white transition-colors">Contact</Link></li>
              <li><Link to="#" className="text-gray-400 hover:text-white transition-colors">Help Center</Link></li>
              <li><Link to="#" className="text-gray-400 hover:text-white transition-colors">Terms</Link></li>
              <li><Link to="#" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</Link></li>
            </ul>
          </div>

          {/* About us */}
          <div>
            <h3 className="text-primary-400 font-semibold mb-4">About us</h3>
            <ul className="space-y-3">
              <li><Link to="#" className="text-gray-400 hover:text-white transition-colors">Pricing</Link></li>
              <li><Link to="#" className="text-gray-400 hover:text-white transition-colors">Terms and condition</Link></li>
            </ul>
          </div>

          {/* Contact Us */}
          <div>
            <h3 className="text-primary-400 font-semibold mb-4">Contact Us</h3>
            <ul className="space-y-3">
              <li className="text-gray-400">+966 XX XXX XXXX</li>
              <li className="text-gray-400">Email: info@nabih.com</li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-gray-800 mt-12 pt-8">
          <p className="text-center text-gray-500 text-sm">
            © 2025 Innhee.com. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
