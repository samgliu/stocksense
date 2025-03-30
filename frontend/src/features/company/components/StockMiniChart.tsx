import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { CompanyHistoricalPrice } from '../api';

interface StockMiniChartProps {
  data: CompanyHistoricalPrice;
}

export const StockMiniChart = ({ data }: StockMiniChartProps) => {
  return (
    <div className="h-24 w-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="date" hide />
          <YAxis domain={['dataMin', 'dataMax']} hide />
          <Tooltip formatter={(v) => `$${v}`} />
          <Line type="monotone" dataKey="close" stroke="#3b82f6" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
