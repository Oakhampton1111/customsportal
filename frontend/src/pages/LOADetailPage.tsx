import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FaArrowLeft, FaDownload, FaEdit, FaFileContract } from 'react-icons/fa';
import type { DigitalLOA } from '../types/loa';
import { loaApi } from '../services/api';

const LOADetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [loa, setLoa] = useState<DigitalLOA | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadLOA(id);
    }
  }, [id]);

  const loadLOA = async (loaId: string) => {
    try {
      setLoading(true);
      const data = await loaApi.getLOA(loaId);
      setLoa(data);
    } catch (err) {
      setError('Failed to load LOA');
      console.error('Error loading LOA:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'signed': return 'bg-blue-100 text-blue-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'revoked': return 'bg-red-100 text-red-800';
      case 'expired': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !loa) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">LOA not found</h3>
        <p className="mt-2 text-sm text-gray-500">{error || 'The requested LOA could not be found.'}</p>
        <div className="mt-6">
          <Link
            to="/loa"
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <FaArrowLeft className="mr-2 h-4 w-4" />
            Back to LOAs
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/loa"
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
          >
            <FaArrowLeft className="mr-2 h-4 w-4" />
            Back to LOAs
          </Link>
        </div>
        <div className="flex space-x-3">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <FaDownload className="mr-2 h-4 w-4" />
            Download
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
            <FaEdit className="mr-2 h-4 w-4" />
            Edit
          </button>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">LOA #{loa.loa_number}</h1>
            <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(loa.status)}`}>
              {loa.status.toUpperCase()}
            </span>
          </div>
        </div>

        <div className="px-6 py-4">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Company Name</dt>
              <dd className="mt-1 text-sm text-gray-900">{loa.company_name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Company ABN</dt>
              <dd className="mt-1 text-sm text-gray-900">{loa.company_abn}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Authorized Person</dt>
              <dd className="mt-1 text-sm text-gray-900">{loa.authorized_person_name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Title</dt>
              <dd className="mt-1 text-sm text-gray-900">{loa.authorized_person_title}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              <dd className="mt-1 text-sm text-gray-900">{loa.authorized_person_email}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Phone</dt>
              <dd className="mt-1 text-sm text-gray-900">{loa.authorized_person_phone || 'N/A'}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Customs Broker License</dt>
              <dd className="mt-1 text-sm text-gray-900">{loa.customs_broker_license}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Authority Scope</dt>
              <dd className="mt-1 text-sm text-gray-900">{loa.authority_scope}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created Date</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(loa.created_at).toLocaleString()}
              </dd>
            </div>
            {loa.signed_at && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Signed Date</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(loa.signed_at).toLocaleString()}
                </dd>
              </div>
            )}
            {loa.expires_at && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Expires</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(loa.expires_at).toLocaleString()}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">LOA Content</h3>
        </div>
        <div className="px-6 py-4">
          <div className="prose max-w-none">
            <div className="whitespace-pre-wrap text-sm text-gray-900">
              {loa.loa_content}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LOADetailPage;