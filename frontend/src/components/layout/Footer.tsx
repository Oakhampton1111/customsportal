import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="text-sm text-gray-600 mb-4 md:mb-0">
            © 2024 Customs Broker Portal. All rights reserved.
          </div>
          
          <div className="flex items-center space-x-6 text-sm text-gray-600">
            <span>Australian Customs & Trade Portal</span>
            <span>•</span>
            <span>Professional Duty Calculations</span>
            <span>•</span>
            <span>AI-Powered Classification</span>
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="text-xs text-gray-500 text-center">
            This portal provides duty calculations and tariff information for Australian customs.
            Always verify calculations with official ABF sources for final compliance.
          </div>
        </div>
      </div>
    </footer>
  );
};