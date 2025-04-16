import { Dashboard } from '../dashboard/components/Dashboard';
import React from 'react';

export const Home = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="text-center">
        <h1 className="mb-4 text-5xl font-extrabold text-blue-600">StockSense</h1>
        <p className="mb-8 text-xl text-gray-600">
          Semantic Stock Search, Trading Agents, and AI Summaries
        </p>
      </div>

      {/* Dashboard Section */}
      <div className="container mx-auto px-4">
        <Dashboard />
      </div>
    </div>
  );
};
