import React from 'react';
import { FaGithub, FaLinkedin, FaTwitter, FaEnvelope } from 'react-icons/fa';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Company Info */}
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center mb-4">
                <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">CB</span>
                </div>
                <span className="ml-2 text-lg font-semibold text-gray-900">
                  Customs Broker Portal
                </span>
              </div>
              <p className="text-gray-600 text-sm mb-4 max-w-md">
                Streamlining customs brokerage operations with digital solutions for 
                document management, compliance tracking, and EDI processing.
              </p>
              <div className="flex space-x-4">
                <a
                  href="#"
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label="GitHub"
                >
                  <FaGithub className="h-5 w-5" />
                </a>
                <a
                  href="#"
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label="LinkedIn"
                >
                  <FaLinkedin className="h-5 w-5" />
                </a>
                <a
                  href="#"
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label="Twitter"
                >
                  <FaTwitter className="h-5 w-5" />
                </a>
                <a
                  href="mailto:support@customsbrokerportal.com"
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label="Email"
                >
                  <FaEnvelope className="h-5 w-5" />
                </a>
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 tracking-wider uppercase mb-4">
                Quick Links
              </h3>
              <ul className="space-y-2">
                <li>
                  <a href="/dashboard" className="text-gray-600 hover:text-gray-900 text-sm">
                    Dashboard
                  </a>
                </li>
                <li>
                  <a href="/documents" className="text-gray-600 hover:text-gray-900 text-sm">
                    Documents
                  </a>
                </li>
                <li>
                  <a href="/loa" className="text-gray-600 hover:text-gray-900 text-sm">
                    Letter of Authority
                  </a>
                </li>
                <li>
                  <a href="/edi" className="text-gray-600 hover:text-gray-900 text-sm">
                    EDI Jobs
                  </a>
                </li>
                <li>
                  <a href="/compliance" className="text-gray-600 hover:text-gray-900 text-sm">
                    Compliance
                  </a>
                </li>
              </ul>
            </div>

            {/* Support */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 tracking-wider uppercase mb-4">
                Support
              </h3>
              <ul className="space-y-2">
                <li>
                  <a href="/help" className="text-gray-600 hover:text-gray-900 text-sm">
                    Help Center
                  </a>
                </li>
                <li>
                  <a href="/help/documentation" className="text-gray-600 hover:text-gray-900 text-sm">
                    Documentation
                  </a>
                </li>
                <li>
                  <a href="/help/api" className="text-gray-600 hover:text-gray-900 text-sm">
                    API Reference
                  </a>
                </li>
                <li>
                  <a href="/contact" className="text-gray-600 hover:text-gray-900 text-sm">
                    Contact Support
                  </a>
                </li>
                <li>
                  <a href="/status" className="text-gray-600 hover:text-gray-900 text-sm">
                    System Status
                  </a>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom section */}
          <div className="mt-8 pt-8 border-t border-gray-200">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <div className="flex flex-col md:flex-row items-center space-y-2 md:space-y-0 md:space-x-6">
                <p className="text-gray-500 text-sm">
                  © {currentYear} Customs Broker Portal. All rights reserved.
                </p>
                <div className="flex space-x-6">
                  <a href="/privacy" className="text-gray-500 hover:text-gray-900 text-sm">
                    Privacy Policy
                  </a>
                  <a href="/terms" className="text-gray-500 hover:text-gray-900 text-sm">
                    Terms of Service
                  </a>
                  <a href="/security" className="text-gray-500 hover:text-gray-900 text-sm">
                    Security
                  </a>
                </div>
              </div>
              
              <div className="mt-4 md:mt-0">
                <p className="text-gray-500 text-sm">
                  Built with ❤️ for customs professionals
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;