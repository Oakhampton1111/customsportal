import React, { useState } from 'react';
import type { LOACreateRequest, LOAStatus } from '../../types/loa';

interface LOACreatorProps {
  onCreateLOA: (data: LOACreateRequest) => Promise<void>;
  loading?: boolean;
  error?: string;
}

export const LOACreator: React.FC<LOACreatorProps> = ({
  onCreateLOA,
  loading = false,
  error
}) => {
  const [formData, setFormData] = useState<LOACreateRequest>({
    company_name: '',
    company_abn: '',
    authorized_person_name: '',
    authorized_person_title: '',
    authorized_person_email: '',
    authorized_person_phone: '',
    customs_broker_license: '',
    authority_scope: '',
    reference_number: ''
  });

  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 3;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onCreateLOA(formData);
  };

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const isStepValid = (step: number) => {
    switch (step) {
      case 1:
        return formData.company_name && formData.company_abn && formData.customs_broker_license;
      case 2:
        return formData.authorized_person_name && formData.authorized_person_title && formData.authorized_person_email;
      case 3:
        return formData.authority_scope;
      default:
        return false;
    }
  };

  const renderStepIndicator = () => (
    <div className="mb-8">
      <div className="flex items-center justify-center">
        {[1, 2, 3].map((step) => (
          <React.Fragment key={step}>
            <div
              className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                step <= currentStep
                  ? 'bg-indigo-600 border-indigo-600 text-white'
                  : 'border-gray-300 text-gray-500'
              }`}
            >
              {step < currentStep ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              ) : (
                step
              )}
            </div>
            {step < 3 && (
              <div
                className={`w-16 h-0.5 ${
                  step < currentStep ? 'bg-indigo-600' : 'bg-gray-300'
                }`}
              />
            )}
          </React.Fragment>
        ))}
      </div>
      <div className="flex justify-between mt-2 text-sm">
        <span className={currentStep >= 1 ? 'text-indigo-600' : 'text-gray-500'}>
          Company Details
        </span>
        <span className={currentStep >= 2 ? 'text-indigo-600' : 'text-gray-500'}>
          Authorized Person
        </span>
        <span className={currentStep >= 3 ? 'text-indigo-600' : 'text-gray-500'}>
          Authority Scope
        </span>
      </div>
    </div>
  );

  const renderStep1 = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Company Information</h3>
      
      <div>
        <label htmlFor="company_name" className="block text-sm font-medium text-gray-700">
          Company Name *
        </label>
        <input
          type="text"
          id="company_name"
          name="company_name"
          required
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          value={formData.company_name}
          onChange={handleInputChange}
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="company_abn" className="block text-sm font-medium text-gray-700">
          Company ABN *
        </label>
        <input
          type="text"
          id="company_abn"
          name="company_abn"
          required
          pattern="[0-9]{11}"
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="12345678901"
          value={formData.company_abn}
          onChange={handleInputChange}
          disabled={loading}
        />
        <p className="mt-1 text-sm text-gray-500">11-digit Australian Business Number</p>
      </div>

      <div>
        <label htmlFor="customs_broker_license" className="block text-sm font-medium text-gray-700">
          Customs Broker License Number *
        </label>
        <input
          type="text"
          id="customs_broker_license"
          name="customs_broker_license"
          required
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          value={formData.customs_broker_license}
          onChange={handleInputChange}
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="reference_number" className="block text-sm font-medium text-gray-700">
          Reference Number (Optional)
        </label>
        <input
          type="text"
          id="reference_number"
          name="reference_number"
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="Internal reference number"
          value={formData.reference_number}
          onChange={handleInputChange}
          disabled={loading}
        />
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Authorized Person Details</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="authorized_person_name" className="block text-sm font-medium text-gray-700">
            Full Name *
          </label>
          <input
            type="text"
            id="authorized_person_name"
            name="authorized_person_name"
            required
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            value={formData.authorized_person_name}
            onChange={handleInputChange}
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="authorized_person_title" className="block text-sm font-medium text-gray-700">
            Job Title *
          </label>
          <input
            type="text"
            id="authorized_person_title"
            name="authorized_person_title"
            required
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            placeholder="e.g., Managing Director, Operations Manager"
            value={formData.authorized_person_title}
            onChange={handleInputChange}
            disabled={loading}
          />
        </div>
      </div>

      <div>
        <label htmlFor="authorized_person_email" className="block text-sm font-medium text-gray-700">
          Email Address *
        </label>
        <input
          type="email"
          id="authorized_person_email"
          name="authorized_person_email"
          required
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          value={formData.authorized_person_email}
          onChange={handleInputChange}
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="authorized_person_phone" className="block text-sm font-medium text-gray-700">
          Phone Number (Optional)
        </label>
        <input
          type="tel"
          id="authorized_person_phone"
          name="authorized_person_phone"
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="+61 2 1234 5678"
          value={formData.authorized_person_phone}
          onChange={handleInputChange}
          disabled={loading}
        />
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Authority Scope</h3>
      
      <div>
        <label htmlFor="authority_scope" className="block text-sm font-medium text-gray-700">
          Scope of Authority *
        </label>
        <textarea
          id="authority_scope"
          name="authority_scope"
          required
          rows={8}
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="Describe the specific authorities being granted to the customs broker..."
          value={formData.authority_scope}
          onChange={handleInputChange}
          disabled={loading}
        />
        <p className="mt-2 text-sm text-gray-500">
          Please specify the exact scope of authority you are granting to the customs broker. 
          This may include import/export clearance, duty payments, document submission, etc.
        </p>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Important Legal Notice
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>
                By creating this Letter of Authority, you are legally authorizing the specified 
                customs broker to act on behalf of your company. Please ensure all information 
                is accurate and the scope of authority is clearly defined.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Create Digital Letter of Authority</h2>
        <p className="mt-2 text-sm text-gray-600">
          Create a legally binding digital LOA to authorize customs broker services
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {renderStepIndicator()}

      <form onSubmit={handleSubmit}>
        {currentStep === 1 && renderStep1()}
        {currentStep === 2 && renderStep2()}
        {currentStep === 3 && renderStep3()}

        <div className="mt-8 flex justify-between">
          <button
            type="button"
            onClick={prevStep}
            disabled={currentStep === 1}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          {currentStep < totalSteps ? (
            <button
              type="button"
              onClick={nextStep}
              disabled={!isStepValid(currentStep)}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          ) : (
            <button
              type="submit"
              disabled={!isStepValid(currentStep) || loading}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating LOA...
                </>
              ) : (
                'Create LOA'
              )}
            </button>
          )}
        </div>
      </form>
    </div>
  );
};