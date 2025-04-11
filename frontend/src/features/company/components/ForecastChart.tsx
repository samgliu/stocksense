import { AreaChart, ReferenceArea, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

interface ForecastProps {
  prediction: {
    min: number;
    max: number;
    average: number;
    confidence: {
      '70%': { min: number; max: number };
      '90%': { min: number; max: number };
    };
  };
}

export const ForecastChart = ({ prediction }: ForecastProps) => {
  const { min, max, average, confidence } = prediction;

  const dummyData = [
    { x: min, y: 0 },
    { x: max, y: 0 },
  ];

  const ticks = [
    confidence['70%'].min,
    confidence['70%'].max,
    confidence['90%'].min,
    confidence['90%'].max,
  ];

  const labelMap = new Map<number, string>([
    [confidence['70%'].min, `$${confidence['70%'].min}`],
    [confidence['70%'].max, `$${confidence['70%'].max}`],
    [confidence['90%'].min, `$${confidence['90%'].min}`],
    [confidence['90%'].max, `$${confidence['90%'].max}`],
  ]);

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-md">
      <h3 className="mb-4 text-lg font-semibold text-gray-800">📈 30-Day Price Forecast</h3>
      <ResponsiveContainer width="100%" height={140}>
        <AreaChart data={dummyData}>
          <XAxis
            dataKey="x"
            type="number"
            domain={[min, max]}
            ticks={ticks}
            tickFormatter={(v) => labelMap.get(v) ?? ''}
            tick={{ fontSize: 12 }}
            axisLine={false}
          />
          <YAxis hide domain={[0, 1]} />
          <Tooltip contentStyle={{ display: 'none' }} />

          {/* 90% confidence band (lighter) */}
          <ReferenceArea
            x1={confidence['90%'].min}
            x2={confidence['90%'].max}
            y1={0}
            y2={1}
            fill="#bfdbfe"
            strokeOpacity={0}
          />

          {/* 70% confidence band (darker, on top) */}
          <ReferenceArea
            x1={confidence['70%'].min}
            x2={confidence['70%'].max}
            y1={0}
            y2={1}
            fill="#60a5fa"
            strokeOpacity={0}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Bottom labels */}
      <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-gray-500">
        <div className="flex items-center gap-1">
          <span className="text-lg text-blue-600">🔵</span>
          <span>
            Avg: <span className="font-semibold text-gray-800">${average}</span>
          </span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-lg text-red-500">🔻</span>
          <span>
            Min: <span className="font-medium text-gray-800">${min}</span>
          </span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-lg text-red-500">🔺</span>
          <span>
            Max: <span className="font-medium text-gray-800">${max}</span>
          </span>
        </div>
      </div>
    </div>
  );
};
