import React from 'react';
import { Link } from 'react-router-dom';
import { FaHome, FaArrowLeft, FaExclamationTriangle } from 'react-icons/fa';

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="text-center">
            {/* 404 Icon */}
            <div className="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-red-100 mb-6">
              <FaExclamationTriangle className="h-12 w-12 text-red-600" />
            </div>

            {/* 404 Text */}
            <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Page Not Found</h2>
            
            <p className="text-gray-600 mb-8">
              Sorry, we couldn't find the page you're looking for. The page may have been moved, 
              deleted, or you may have entered an incorrect URL.
            </p>

            {/* Action Buttons */}
            <div className="space-y-4">
              <Link
                to="/"
                className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                <FaHome className="w-4 h-4 mr-2" />
                Go to Dashboard
              </Link>
              
              <button
                onClick={() => window.history.back()}
                className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                <FaArrowLeft className="w-4 h-4 mr-2" />
                Go Back
              </button>
            </div>

            {/* Quick Links */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-500 mb-4">Or try one of these pages:</p>
              <div className="space-y-2">
                <Link
                  to="/documents"
                  className="block text-sm text-blue-600 hover:text-blue-800 transition-colors"
                >
                  Documents
                </Link>
                <Link
                  to="/loa"
                  className="block text-sm text-blue-600 hover:text-blue-800 transition-colors"
                >
                  Letter of Authority
                </Link>
                <Link
                  to="/edi"
                  className="block text-sm text-blue-600 hover:text-blue-800 transition-colors"
                >
                  EDI Management
                </Link>
                <Link
                  to="/compliance"
                  className="block text-sm text-blue-600 hover:text-blue-800 transition-colors"
                >
                  Compliance
                </Link>
                <Link
                  to="/help"
                  className="block text-sm text-blue-600 hover:text-blue-800 transition-colors"
                >
                  Help Center
                </Link>
              </div>
            </div>

            {/* Contact Support */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-500 mb-2">Still need help?</p>
              <Link
                to="/help"
                className="text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors"
              >
                Contact Support
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Info */}
      <div className="mt-8 text-center">
        <p className="text-xs text-gray-400">
          Error Code: 404 | Page Not Found
        </p>
      </div>
    </div>
  );
};

export default NotFoundPage;