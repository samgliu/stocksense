import { Dashboard } from '../dashboard/components/Dashboard';

export const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 via-white to-white py-16">
      <div className="mx-auto mb-12 max-w-2xl text-center">
        <div className="flex flex-col items-center gap-2">
          <h1 className="mb-2 text-2xl font-semibold tracking-tight text-blue-600">StockSense</h1>
        </div>
        <p className="mb-10 text-lg font-medium text-gray-500">
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
