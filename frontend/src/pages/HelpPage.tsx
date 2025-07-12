import React, { useState } from 'react';
import { FaQuestionCircle, FaBook, FaPhone, FaEnvelope, FaSearch, FaChevronDown, FaChevronRight } from 'react-icons/fa';

interface FAQItem {
  id: string;
  question: string;
  answer: string;
  category: string;
}

const HelpPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedFAQ, setExpandedFAQ] = useState<string | null>(null);

  const faqData: FAQItem[] = [
    {
      id: '1',
      question: 'How do I upload documents?',
      answer: 'To upload documents, navigate to the Documents page and either drag and drop files into the upload area or click the "Choose Files" button to select files from your computer. Supported formats include PDF, DOC, DOCX, XLS, XLSX, and common image formats.',
      category: 'documents'
    },
    {
      id: '2',
      question: 'What is a Letter of Authority (LOA)?',
      answer: 'A Letter of Authority (LOA) is a legal document that authorizes a customs broker to act on behalf of an importer or exporter. It grants the broker permission to handle customs clearance, pay duties and taxes, and communicate with customs authorities on your behalf.',
      category: 'loa'
    },
    {
      id: '3',
      question: 'How do I create a digital LOA?',
      answer: 'To create a digital LOA, go to the LOA page and click "Create New LOA". Fill out the required information including company details, authorization scope, and validity period. You can then digitally sign the document and submit it for processing.',
      category: 'loa'
    },
    {
      id: '4',
      question: 'What is EDI and how does it work?',
      answer: 'EDI (Electronic Data Interchange) is a standardized electronic communication method used for transmitting business documents between trading partners. In customs brokerage, EDI is used to submit customs declarations, receive status updates, and exchange other trade-related documents with customs authorities.',
      category: 'edi'
    },
    {
      id: '5',
      question: 'How can I track my EDI submissions?',
      answer: 'You can track your EDI submissions on the EDI page. Each submission shows its current status (pending, processing, completed, or failed), submission time, and any error messages. You will also receive notifications when the status changes.',
      category: 'edi'
    },
    {
      id: '6',
      question: 'What compliance requirements do I need to meet?',
      answer: 'Compliance requirements vary depending on your industry, the countries you trade with, and the types of goods you import/export. Common requirements include proper documentation, accurate classification of goods, payment of duties and taxes, and adherence to safety and security regulations.',
      category: 'compliance'
    },
    {
      id: '7',
      question: 'How do I update my account information?',
      answer: 'To update your account information, go to the Settings page where you can modify your profile details, contact information, notification preferences, and security settings. Remember to save your changes after making updates.',
      category: 'account'
    },
    {
      id: '8',
      question: 'What file formats are supported for document uploads?',
      answer: 'We support the following file formats: PDF, DOC, DOCX, XLS, XLSX, JPG, JPEG, PNG, GIF, and TXT. Maximum file size is 10MB per file. For best results, we recommend using PDF format for official documents.',
      category: 'documents'
    },
    {
      id: '9',
      question: 'How do I reset my password?',
      answer: 'If you forgot your password, click the "Forgot Password" link on the login page. Enter your email address and we will send you a password reset link. You can also change your password from the Security tab in Settings if you are already logged in.',
      category: 'account'
    },
    {
      id: '10',
      question: 'What should I do if my EDI submission fails?',
      answer: 'If your EDI submission fails, check the error message provided in the submission details. Common issues include missing required fields, invalid data formats, or connectivity problems. You can edit and resubmit the failed submission after correcting the errors.',
      category: 'edi'
    }
  ];

  const categories = [
    { id: 'all', label: 'All Categories' },
    { id: 'documents', label: 'Documents' },
    { id: 'loa', label: 'Letter of Authority' },
    { id: 'edi', label: 'EDI' },
    { id: 'compliance', label: 'Compliance' },
    { id: 'account', label: 'Account' }
  ];

  const filteredFAQs = faqData.filter(faq => {
    const matchesSearch = faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         faq.answer.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || faq.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const toggleFAQ = (id: string) => {
    setExpandedFAQ(expandedFAQ === id ? null : id);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="text-center">
            <FaQuestionCircle className="mx-auto h-12 w-12 text-blue-600" />
            <h1 className="mt-2 text-3xl font-bold text-gray-900">Help Center</h1>
            <p className="mt-2 text-lg text-gray-600">
              Find answers to common questions and get support for your customs brokerage needs
            </p>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="space-y-4">
            {/* Search Bar */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FaSearch className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search for help topics..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Category Filter */}
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {category.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>
          
          {filteredFAQs.length === 0 ? (
            <div className="text-center py-8">
              <FaQuestionCircle className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No results found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your search terms or category filter.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredFAQs.map((faq) => (
                <div key={faq.id} className="border border-gray-200 rounded-lg">
                  <button
                    onClick={() => toggleFAQ(faq.id)}
                    className="w-full px-4 py-4 text-left flex items-center justify-between hover:bg-gray-50 focus:outline-none focus:bg-gray-50"
                  >
                    <span className="font-medium text-gray-900">{faq.question}</span>
                    {expandedFAQ === faq.id ? (
                      <FaChevronDown className="h-5 w-5 text-gray-500" />
                    ) : (
                      <FaChevronRight className="h-5 w-5 text-gray-500" />
                    )}
                  </button>
                  {expandedFAQ === faq.id && (
                    <div className="px-4 pb-4">
                      <div className="text-gray-700 leading-relaxed">
                        {faq.answer}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6 text-center">
            <FaBook className="mx-auto h-8 w-8 text-blue-600" />
            <h3 className="mt-2 text-lg font-medium text-gray-900">User Guide</h3>
            <p className="mt-1 text-sm text-gray-500">
              Comprehensive documentation and tutorials
            </p>
            <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
              View Guide
            </button>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6 text-center">
            <FaPhone className="mx-auto h-8 w-8 text-green-600" />
            <h3 className="mt-2 text-lg font-medium text-gray-900">Phone Support</h3>
            <p className="mt-1 text-sm text-gray-500">
              Speak with our support team
            </p>
            <div className="mt-4">
              <p className="text-lg font-semibold text-gray-900">1-800-CUSTOMS</p>
              <p className="text-sm text-gray-500">Mon-Fri 8AM-6PM EST</p>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6 text-center">
            <FaEnvelope className="mx-auto h-8 w-8 text-purple-600" />
            <h3 className="mt-2 text-lg font-medium text-gray-900">Email Support</h3>
            <p className="mt-1 text-sm text-gray-500">
              Send us a detailed message
            </p>
            <button className="mt-4 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors">
              Contact Us
            </button>
          </div>
        </div>
      </div>

      {/* Additional Resources */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Additional Resources</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">System Status</h3>
              <p className="text-sm text-gray-600 mb-3">
                Check the current status of our services and any ongoing maintenance.
              </p>
              <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                View Status Page →
              </button>
            </div>
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">API Documentation</h3>
              <p className="text-sm text-gray-600 mb-3">
                Technical documentation for developers integrating with our API.
              </p>
              <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                View API Docs →
              </button>
            </div>
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">Training Videos</h3>
              <p className="text-sm text-gray-600 mb-3">
                Step-by-step video tutorials for using our platform effectively.
              </p>
              <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                Watch Videos →
              </button>
            </div>
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-2">Release Notes</h3>
              <p className="text-sm text-gray-600 mb-3">
                Stay updated with the latest features and improvements.
              </p>
              <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                View Updates →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HelpPage;