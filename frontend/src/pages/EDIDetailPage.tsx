import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FaArrowLeft, FaEdit } from 'react-icons/fa';
import type { JobStatusResponse } from '../types/edi';
import { ediApi } from '../services/api';

const EDIDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadJobStatus(id);
    }
  }, [id]);

  const loadJobStatus = async (jobId: string) => {
    try {
      setLoading(true);
      const data = await ediApi.getJobStatus(jobId);
      setJobStatus(data);
    } catch (err) {
      setError('Failed to load job status');
      console.error('Error loading job status:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !jobStatus) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Job not found</h3>
        <p className="mt-2 text-sm text-gray-500">{error || 'The requested job could not be found.'}</p>
        <div className="mt-6">
          <Link
            to="/edi"
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <FaArrowLeft className="mr-2 h-4 w-4" />
            Back to Jobs
          </Link>
        </div>
      </div>
    );
  }

  const { job, messages, declarations } = jobStatus;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/edi"
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <FaArrowLeft className="mr-2 h-4 w-4" />
            Back to Jobs
          </Link>
        </div>
        <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
          <FaEdit className="mr-2 h-4 w-4" />
          Edit Job
        </button>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">Job #{job.job_number}</h1>
        </div>
        <div className="px-6 py-4">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Consignment Reference</dt>
              <dd className="mt-1 text-sm text-gray-900">{job.consignment_reference}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1 text-sm text-gray-900">{job.status.replace('_', ' ').toUpperCase()}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Cargo Description</dt>
              <dd className="mt-1 text-sm text-gray-900">{job.cargo_description}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Port of Discharge</dt>
              <dd className="mt-1 text-sm text-gray-900">{job.port_of_discharge}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Messages</h3>
          </div>
          <div className="px-6 py-4">
            {messages.length === 0 ? (
              <p className="text-gray-500">No messages found</p>
            ) : (
              <div className="space-y-4">
                {messages.map((message) => (
                  <div key={message.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{message.message_type}</p>
                        <p className="text-sm text-gray-500">{message.direction}</p>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(message.received_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Declarations</h3>
          </div>
          <div className="px-6 py-4">
            {declarations.length === 0 ? (
              <p className="text-gray-500">No declarations found</p>
            ) : (
              <div className="space-y-4">
                {declarations.map((declaration) => (
                  <div key={declaration.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{declaration.declaration_number}</p>
                        <p className="text-sm text-gray-500">{declaration.declaration_type}</p>
                      </div>
                      <span className="text-xs text-gray-500">
                        {declaration.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EDIDetailPage;