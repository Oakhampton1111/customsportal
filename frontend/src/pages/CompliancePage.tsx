import React, { useState, useEffect } from 'react';
import { FaShieldAlt, FaChartLine, FaExclamationTriangle } from 'react-icons/fa';
import type { ComplianceMetrics } from '../types/compliance';
import { complianceApi } from '../services/api';

const CompliancePage: React.FC = () => {
  const [metrics, setMetrics] = useState<ComplianceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadComplianceData();
  }, []);

  const loadComplianceData = async () => {
    try {
      setLoading(true);
      const data = await complianceApi.getComplianceScore();
      // Transform the API response to match our ComplianceMetrics type
      const transformedData: ComplianceMetrics = {
        overall_score: data.overall,
        category_scores: data.categories,
        trend_data: data.trends.map(trend => ({
          ...trend,
          category_scores: data.categories
        })),
        violation_counts: {},
        audit_frequency: {},
        improvement_rate: 0,
        risk_level: 'medium'
      };
      setMetrics(transformedData);
    } catch (err) {
      setError('Failed to load compliance data');
      console.error('Error loading compliance data:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 90) return 'bg-green-100';
    if (score >= 70) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Compliance Overview</h1>
        <p className="text-gray-600">Monitor your compliance status and requirements</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {metrics && (
        <>
          {/* Overall Score */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className={`p-3 rounded-full ${getScoreBgColor(metrics.overall_score)}`}>
                <FaShieldAlt className={`h-8 w-8 ${getScoreColor(metrics.overall_score)}`} />
              </div>
              <div className="ml-4">
                <h2 className="text-lg font-medium text-gray-900">Overall Compliance Score</h2>
                <p className={`text-3xl font-bold ${getScoreColor(metrics.overall_score)}`}>
                  {metrics.overall_score}%
                </p>
              </div>
            </div>
          </div>

          {/* Category Scores */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Compliance by Category</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(metrics.category_scores).map(([category, score]) => (
                  <div key={category} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-gray-900 capitalize">
                        {category.replace('_', ' ')}
                      </h4>
                      <span className={`text-lg font-bold ${getScoreColor(score)}`}>
                        {score}%
                      </span>
                    </div>
                    <div className="mt-2">
                      <div className="bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            score >= 90 ? 'bg-green-500' : 
                            score >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${score}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Trend Chart */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Compliance Trend</h3>
            </div>
            <div className="p-6">
              <div className="text-center py-12">
                <FaChartLine className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Trend Chart</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Compliance trend visualization would be displayed here
                </p>
              </div>
            </div>
          </div>

          {/* Violations Summary */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Violations</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(metrics.violation_counts).map(([type, count]) => (
                  <div key={type} className="border rounded-lg p-4">
                    <div className="flex items-center">
                      <FaExclamationTriangle className="h-5 w-5 text-red-500 mr-2" />
                      <div>
                        <p className="text-sm font-medium text-gray-900 capitalize">
                          {type.replace('_', ' ')}
                        </p>
                        <p className="text-2xl font-bold text-red-600">{count}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default CompliancePage;