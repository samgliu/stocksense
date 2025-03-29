import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  useGetDailyAnalysisQuery,
  useGetHistorySummaryQuery,
  useGetMonthlySummaryQuery,
  useGetUsageCountQuery,
} from '../api';

import { Spinner } from '@/features/shared/Spinner';

export const Dashboard = () => {
  const { data: dailyData, isLoading: isDailyLoading } = useGetDailyAnalysisQuery({});
  const { data: monthlySummary, isLoading: isMonthlyLoading } = useGetMonthlySummaryQuery({});
  const { data: usageCount, isLoading: isUsageLoading } = useGetUsageCountQuery({});
  const { data: historySummary, isLoading: isHistoryLoading } = useGetHistorySummaryQuery({});

  if (isDailyLoading || isMonthlyLoading || isUsageLoading || isHistoryLoading) {
    return <Spinner />;
  }

  return (
    <div className="space-y-8 p-6">
      {/* Title */}
      <h2 className="text-3xl font-bold text-gray-900">Dashboard Overview</h2>

      {/* Daily Analysis Chart */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-lg">
        <h3 className="mb-4 text-xl font-semibold text-gray-800">Daily Analysis</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={dailyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Monthly Summary */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-lg">
          <h4 className="mb-3 text-lg font-semibold text-gray-800">Current Month</h4>
          <div className="text-2xl font-semibold text-blue-600">
            {monthlySummary.current_month_count}
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-lg">
          <h4 className="mb-2 text-lg font-semibold text-gray-800">Last Month</h4>
          <div className="text-2xl font-semibold text-blue-600">
            {monthlySummary.last_month_count}
          </div>
        </div>
      </div>

      {/* History Summary */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-lg">
        <h3 className="mb-4 text-xl font-semibold text-gray-800">History Summary</h3>
        <div className="text-lg text-gray-700">
          <div className="mb-2">Total Records: {historySummary.total_records}</div>
          <div>Total Users: {historySummary.total_users}</div>
        </div>
      </div>

      {/* Usage Count */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-lg">
          <h4 className="mb-2 text-lg font-semibold text-gray-800">Admins</h4>
          <div className="text-2xl font-semibold text-blue-600">{usageCount.admin}</div>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-lg">
          <h4 className="mb-2 text-lg font-semibold text-gray-800">Users</h4>
          <div className="text-2xl font-semibold text-blue-600">{usageCount.user}</div>
        </div>
      </div>
    </div>
  );
};
