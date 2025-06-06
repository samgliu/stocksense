import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  useGetBuySellDailyQuery,
  useGetDailyAnalysisQuery,
  useGetHistorySummaryQuery,
  useGetMonthlySummaryQuery,
  useGetNewsSummaryQuery,
  useGetSnapshotsDailyQuery,
  useGetTopCompaniesQuery,
  useGetTopIndustriesQuery,
  useGetUsageCountQuery,
} from '../api';

import { Spinner } from '@/features/shared/Spinner';
import { formatCurrencyCompact } from '@/utils/formatters';
import { CustomTooltip } from './CustomTooltip';

const SnapshotLineChart = () => {
  const { data: snapshotData, isLoading } = useGetSnapshotsDailyQuery({});
  return (
    <SectionCard title="💹 Account Value Over Time">
      {isLoading ? (
        <Spinner />
      ) : (
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={snapshotData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tick={{
                fill: '#4B5563',
                fontSize: 11,
                fontWeight: 500,
              }}
            />
            <YAxis
              tickFormatter={(v) => formatCurrencyCompact(v)}
              tick={{
                fill: '#4B5563',
                fontSize: 11,
                fontWeight: 500,
              }}
            />
            <Tooltip formatter={(v: number) => formatCurrencyCompact(v)} />
            <Legend />
            <Line
              type="monotone"
              dataKey="total_value"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 6 }}
              name="Total Value"
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </SectionCard>
  );
};

export const Dashboard = () => {
  const { data: dailyData, isLoading: isDailyLoading } = useGetDailyAnalysisQuery({});
  const { data: monthlySummary, isLoading: isMonthlyLoading } = useGetMonthlySummaryQuery({});
  const { data: usageCount, isLoading: isUsageLoading } = useGetUsageCountQuery({});
  const { data: historySummary, isLoading: isHistoryLoading } = useGetHistorySummaryQuery({});
  const { data: topCompanies, isLoading: isTopCompaniesLoading } = useGetTopCompaniesQuery({});
  const { data: newsSummary, isLoading: isNewsSummaryLoading } = useGetNewsSummaryQuery({});
  const { data: topIndustries, isLoading: isTopIndustriesLoading } = useGetTopIndustriesQuery({});
  const { data: buySellDaily, isLoading: isBuySellDailyLoading } = useGetBuySellDailyQuery({});

  const COLORS = ['#60a5fa', '#818cf8', '#34d399', '#fbbf24', '#f87171'];

  interface CustomizedLabelProps {
    cx: number;
    cy: number;
    midAngle: number;
    outerRadius: number;
    percent: number;
    sector: string;
  }

  const renderCustomizedLabel = ({
    cx,
    cy,
    midAngle,
    outerRadius,
    percent,
    sector,
  }: CustomizedLabelProps) => {
    const RADIAN = Math.PI / 180;
    const radius = outerRadius + 20;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill="#333"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        fontSize={12}
      >
        {`${sector} (${(percent * 100).toFixed(0)}%)`}
      </text>
    );
  };

  return (
    <div className="space-y-4 px-2 py-6 sm:space-y-8 sm:px-6 md:space-y-12 lg:px-16">
      {/* KPI Cards */}
      <div className="grid gap-2 sm:grid-cols-2 sm:gap-4 md:gap-6 lg:grid-cols-4">
        <KPI
          title="📅 This Month"
          value={monthlySummary?.current_month_count}
          isLoading={isMonthlyLoading}
        />
        <KPI
          title="📆 Last Month"
          value={monthlySummary?.last_month_count}
          isLoading={isMonthlyLoading}
        />
        <KPI
          title="📂 Total Records"
          value={historySummary?.total_records}
          isLoading={isHistoryLoading}
        />
        <KPI
          title="👥 Total Users"
          value={historySummary?.total_users}
          isLoading={isHistoryLoading}
        />
      </div>

      {/* Account Value Over Time */}
      <SnapshotLineChart />

      {/* SmartTrade Buy/Sell */}
      <SectionCard
        title="📊 SmartTrade Daily Buy vs Sell"
        isEmpty={!isBuySellDailyLoading && !buySellDaily.length}
      >
        {isBuySellDailyLoading ? (
          <Spinner />
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={buySellDaily}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tick={{
                  fill: '#4B5563',
                  fontSize: 11,
                  fontWeight: 500,
                }}
              />
              <YAxis
                tickFormatter={(v) => formatCurrencyCompact(v)}
                tick={{
                  fill: '#4B5563',
                  fontSize: 11,
                  fontWeight: 500,
                }}
              />
              <Tooltip formatter={(v: number) => formatCurrencyCompact(v)} />
              <Legend />
              <Line
                type="monotone"
                dataKey="buy"
                stroke="#10b981"
                strokeWidth={2}
                name="Buy"
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
              <Line
                type="monotone"
                dataKey="sell"
                stroke="#ef4444"
                strokeWidth={2}
                name="Sell"
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </SectionCard>

      {/* Daily Analysis Chart */}
      <SectionCard title="📈 Daily Analysis (Last 30 Days)">
        {isDailyLoading ? (
          <Spinner />
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tick={{
                  fill: '#4B5563',
                  fontSize: 11,
                  fontWeight: 500,
                }}
              />
              <YAxis
                tick={{
                  fill: '#4B5563',
                  fontSize: 11,
                  fontWeight: 500,
                }}
              />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </SectionCard>

      {/* Usage Count */}
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 sm:gap-4">
        <KPI title="👩‍💼 Admin Usage" value={usageCount?.admin} isLoading={isUsageLoading} />
        <KPI
          title="🧑‍💻 User Usage"
          value={(usageCount?.user || 0) + (usageCount?.anonymous || 0)}
          isLoading={isUsageLoading}
        />
      </div>

      {/* Top Companies */}
      <SectionCard title="🏢 Top Queried Companies">
        {isTopCompaniesLoading ? (
          <Spinner />
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={topCompanies.slice(0, 10)}>
              <XAxis
                dataKey="ticker"
                angle={-35}
                textAnchor="end"
                height={60}
                tick={{
                  fill: '#4B5563',
                  fontSize: 11,
                  fontWeight: 500,
                }}
              />
              <YAxis
                tick={{
                  fill: '#4B5563',
                  fontSize: 11,
                  fontWeight: 500,
                }}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'transparent' }} />
              <Bar
                dataKey="count"
                fill="#3b82f6"
                radius={[4, 4, 0, 0]}
                activeBar={{
                  fill: 'rgba(59, 130, 246, 0.7)',
                }}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </SectionCard>

      {/* News Summary */}
      <SectionCard title="📰 News Coverage by Company">
        {isNewsSummaryLoading ? (
          <Spinner />
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={newsSummary.slice(0, 5)}>
              <XAxis
                dataKey="date"
                angle={-35}
                textAnchor="end"
                height={60}
                tick={{
                  fill: '#4B5563',
                  fontSize: 11,
                  fontWeight: 500,
                }}
              />
              <YAxis
                tick={{
                  fill: '#4B5563',
                  fontSize: 11,
                  fontWeight: 500,
                }}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'transparent' }} />
              <Bar
                dataKey="count"
                fill="#60a5fa"
                radius={[4, 4, 0, 0]}
                activeBar={{
                  fill: 'rgba(59, 130, 246, 0.7)',
                }}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </SectionCard>

      {/* Top Industries */}
      <SectionCard title="🏭 Most Analyzed Industries">
        {isTopIndustriesLoading ? (
          <Spinner />
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={topIndustries.slice(0, 5)}
                dataKey="count"
                nameKey="industry"
                cx="50%"
                cy="50%"
                outerRadius={100}
                labelLine={false}
                label={renderCustomizedLabel}
              >
                {topIndustries.slice(0, 5).map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        )}
      </SectionCard>
    </div>
  );
};

const KPI = ({ title, value, isLoading }: { title: string; value: number; isLoading: boolean }) => (
  <div className="rounded-2xl border border-gray-200 bg-white px-6 py-5 shadow-sm transition hover:shadow-md">
    <h4 className="text-sm text-gray-500">{title}</h4>
    <div className="mt-1 text-3xl font-bold text-blue-600">
      {isLoading ? <span className="text-sm text-gray-400">Loading...</span> : value}
    </div>
  </div>
);

const SectionCard = ({
  title,
  isEmpty = false,
  children,
}: {
  title: string;
  isEmpty?: boolean;
  children: React.ReactNode;
}) => {
  if (isEmpty) return <></>;
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 text-xl font-semibold text-gray-800">{title}</h3>
      {children}
    </div>
  );
};
