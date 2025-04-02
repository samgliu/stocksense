import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

type Report = {
  created_at: string;
  min_price: number;
  max_price: number;
  avg_price: number;
  current_price: number;
};

export const CompanyPredictionHistoryChart = ({ data }: { data: Report[] }) => {
  const chartData = data.map((report) => {
    const dateObj = new Date(report.created_at);
    const date = `${dateObj.getMonth() + 1}/${dateObj.getDate()} ${dateObj.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    })}`;

    return {
      date,
      min: report.min_price,
      max: report.max_price,
      avg: report.avg_price,
      current: report.current_price,
    };
  });

  return (
    <div className="rounded-md border border-gray-200 bg-white p-4">
      <h3 className="mb-3 text-sm font-medium text-gray-900">Historical Forecast Overview</h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12, fill: '#9ca3af' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 12, fill: '#9ca3af' }}
            axisLine={false}
            tickLine={false}
            domain={['auto', 'auto']}
          />
          <Tooltip
            contentStyle={{ borderRadius: 8, fontSize: 13 }}
            labelStyle={{ color: '#6b7280', fontWeight: 500 }}
          />
          <Line
            type="monotone"
            dataKey="min"
            stroke="rgba(99, 102, 241, 0.2)" // Indigo @ 20%
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="avg"
            stroke="rgba(99, 102, 241, 0.5)" // Indigo @ 50%
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="max"
            stroke="rgba(99, 102, 241, 0.35)" // Indigo @ 35%
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="current"
            stroke="#6366F1" // Full opacity
            strokeWidth={2}
            dot={false}
            strokeDasharray="5 3"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
