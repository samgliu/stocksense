import { Dashboard } from '../dashboard/components/Dashboard';

export const Home = () => {
  return (
    <div className="flex min-h-screen flex-col items-center bg-gray-50 py-16">
      <div className="mx-auto mb-12 w-full max-w-2xl text-center">
        <h1 className="mb-2 text-2xl font-semibold tracking-tight text-blue-600">StockSense</h1>
        <p className="mb-0 text-lg font-medium text-gray-500">
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
