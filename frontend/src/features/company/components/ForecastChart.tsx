import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

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

  // Build separate 90% and 70% bands, each as a rectangle (4 corners)
  const data90 = [
    { x: confidence['90%'].min, y: 1 },
    { x: confidence['90%'].max, y: 1 },
    { x: confidence['90%'].max, y: 0 },
    { x: confidence['90%'].min, y: 0 },
  ];

  const data70 = [
    { x: confidence['70%'].min, y: 1 },
    { x: confidence['70%'].max, y: 1 },
    { x: confidence['70%'].max, y: 0 },
    { x: confidence['70%'].min, y: 0 },
  ];

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-md">
      <h3 className="mb-4 text-lg font-semibold text-gray-800">📈 30-Day Price Forecast</h3>
      <ResponsiveContainer width="100%" height={140}>
        <AreaChart>
          <XAxis
            dataKey="x"
            type="number"
            domain={[min, max]}
            ticks={ticks}
            tickFormatter={(value) => labelMap.get(value) ?? ''}
            tick={{ fontSize: 12 }}
            axisLine={false}
          />
          <YAxis hide domain={[0, 1]} />

          <Tooltip
            labelFormatter={(label) => `$${label.toFixed(0)}`}
            formatter={() => null}
            contentStyle={{ display: 'none' }}
          />

          {/* Confidence bands */}
          <Area data={data90} dataKey="y" type="linear" stroke={"transparent"} fill="#bfdbfe" />
          <Area data={data70} dataKey="y" type="linear" stroke={"transparent"} fill="#60a5fa" />
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
