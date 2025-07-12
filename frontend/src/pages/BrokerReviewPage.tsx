import React from 'react';
import { BrokerReviewDashboard } from '../components/broker-review';

export const BrokerReviewPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <BrokerReviewDashboard />
      </div>
    </div>
  );
};

export default BrokerReviewPage;