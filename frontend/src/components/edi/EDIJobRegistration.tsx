import React, { useState } from 'react';
import type { JobRegistrationRequest, JobStatus } from '../../types/edi';

interface EDIJobRegistrationProps {
  onRegisterJob: (data: JobRegistrationRequest) => Promise<void>;
  loading?: boolean;
  error?: string;
}

export const EDIJobRegistration: React.FC<EDIJobRegistrationProps> = ({
  onRegisterJob,
  loading = false,
  error
}) => {
  const [formData, setFormData] = useState<JobRegistrationRequest>({
    job_type: '',
    consignment_reference: '',
    cargo_description: '',
    port_of_discharge: '',
    estimated_arrival: '',
    vessel_voyage: '',
    port_of_loading: '',
    total_packages: undefined,
    total_weight_kg: '',
    total_value_aud: '',
    clearance_deadline: '',
    priority: 'normal'
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? (value ? parseInt(value) : undefined) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onRegisterJob(formData);
  };

  const resetForm = () => {
    setFormData({
      job_type: '',
      consignment_reference: '',
      cargo_description: '',
      port_of_discharge: '',
      estimated_arrival: '',
      vessel_voyage: '',
      port_of_loading: '',
      total_packages: undefined,
      total_weight_kg: '',
      total_value_aud: '',
      clearance_deadline: '',
      priority: 'normal'
    });
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Register EDI Job</h2>
        <p className="mt-2 text-sm text-gray-600">
          Register a new Electronic Data Interchange job for customs processing
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="job_type" className="block text-sm font-medium text-gray-700">
                Job Type *
              </label>
              <select
                id="job_type"
                name="job_type"
                required
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={formData.job_type}
                onChange={handleInputChange}
                disabled={loading}
              >
                <option value="">Select job type</option>
                <option value="import">Import</option>
                <option value="export">Export</option>
                <option value="transit">Transit</option>
                <option value="warehouse">Warehouse</option>
              </select>
            </div>

            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
                Priority
              </label>
              <select
                id="priority"
                name="priority"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={formData.priority}
                onChange={handleInputChange}
                disabled={loading}
              >
                <option value="low">Low</option>
                <option value="normal">Normal</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>

            <div>
              <label htmlFor="consignment_reference" className="block text-sm font-medium text-gray-700">
                Consignment Reference *
              </label>
              <input
                type="text"
                id="consignment_reference"
                name="consignment_reference"
                required
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="e.g., CONS-2024-001"
                value={formData.consignment_reference}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="clearance_deadline" className="block text-sm font-medium text-gray-700">
                Clearance Deadline
              </label>
              <input
                type="datetime-local"
                id="clearance_deadline"
                name="clearance_deadline"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={formData.clearance_deadline}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>
          </div>

          <div className="mt-6">
            <label htmlFor="cargo_description" className="block text-sm font-medium text-gray-700">
              Cargo Description *
            </label>
            <textarea
              id="cargo_description"
              name="cargo_description"
              required
              rows={3}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Detailed description of the cargo being shipped..."
              value={formData.cargo_description}
              onChange={handleInputChange}
              disabled={loading}
            />
          </div>
        </div>

        {/* Shipping Details */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Shipping Details</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="port_of_loading" className="block text-sm font-medium text-gray-700">
                Port of Loading
              </label>
              <input
                type="text"
                id="port_of_loading"
                name="port_of_loading"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="e.g., Shanghai, China"
                value={formData.port_of_loading}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="port_of_discharge" className="block text-sm font-medium text-gray-700">
                Port of Discharge *
              </label>
              <input
                type="text"
                id="port_of_discharge"
                name="port_of_discharge"
                required
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="e.g., Sydney, Australia"
                value={formData.port_of_discharge}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="vessel_voyage" className="block text-sm font-medium text-gray-700">
                Vessel/Voyage
              </label>
              <input
                type="text"
                id="vessel_voyage"
                name="vessel_voyage"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="e.g., MSC OSCAR / 001E"
                value={formData.vessel_voyage}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="estimated_arrival" className="block text-sm font-medium text-gray-700">
                Estimated Arrival
              </label>
              <input
                type="datetime-local"
                id="estimated_arrival"
                name="estimated_arrival"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                value={formData.estimated_arrival}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>
          </div>
        </div>

        {/* Cargo Details */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Cargo Details</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label htmlFor="total_packages" className="block text-sm font-medium text-gray-700">
                Total Packages
              </label>
              <input
                type="number"
                id="total_packages"
                name="total_packages"
                min="1"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="e.g., 50"
                value={formData.total_packages || ''}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="total_weight_kg" className="block text-sm font-medium text-gray-700">
                Total Weight (kg)
              </label>
              <input
                type="text"
                id="total_weight_kg"
                name="total_weight_kg"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="e.g., 1500.50"
                value={formData.total_weight_kg}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="total_value_aud" className="block text-sm font-medium text-gray-700">
                Total Value (AUD)
              </label>
              <input
                type="text"
                id="total_value_aud"
                name="total_value_aud"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="e.g., 25000.00"
                value={formData.total_value_aud}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>
          </div>
        </div>

        {/* Information Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">
                EDI Processing Information
              </h3>
              <div className="mt-2 text-sm text-blue-700">
                <p>
                  Once registered, this job will be processed through our Electronic Data Interchange system. 
                  You will receive real-time updates on the processing status and any required actions.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Form Actions */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={resetForm}
            disabled={loading}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Reset
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Registering Job...
              </>
            ) : (
              'Register EDI Job'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};