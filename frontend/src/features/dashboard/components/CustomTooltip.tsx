import { TooltipProps } from 'recharts';

export const CustomTooltip = ({ active, payload }: TooltipProps<any, any>) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="rounded border bg-white px-4 py-2 shadow">
        <p className="text-sm font-semibold">
          {data.company_name} ({data.ticker || data.sector || data.date})
        </p>
        <p className="text-sm text-gray-600">Queries: {data.count}</p>
      </div>
    );
  }
  return null;
};
