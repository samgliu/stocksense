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

  const ticks = Array.from(
    new Set([
      confidence['70%'].min,
      confidence['70%'].max,
      confidence['90%'].min,
      confidence['90%'].max,
      average,
    ]),
  ).sort((a, b) => a - b);

  const labelMap = new Map<number, string>(ticks.map((value) => [value, `$${value.toFixed(2)}`]));

  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-2 sm:p-4 md:p-6 shadow-md">
      <h3 className="mb-4 text-lg font-semibold text-gray-800">📈 30-Day Price Forecast</h3>
      {/* Band Legends */}
      <div className="mt-2 mr-4 flex justify-center gap-4 text-sm text-gray-500">
        <div className="flex items-center gap-2">
          <span className="inline-block h-3 w-4 rounded-sm bg-blue-300" />
          <span>90% Confidence</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-block h-3 w-4 rounded-sm bg-blue-500" />
          <span>70% Confidence</span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={160}>
        <AreaChart data={dummyData} margin={{ top: 10, right: 20, left: 20, bottom: 30 }}>
          <XAxis
            dataKey="x"
            type="number"
            domain={[min, max]}
            ticks={ticks}
            interval={0}
            tickFormatter={(v) => labelMap.get(v) ?? ''}
            tick={{ fontSize: 12, dy: 10 }}
            axisLine={false}
          />
          <YAxis hide domain={[0, 1]} />
          <Tooltip
            formatter={(value: number, name: string, props) => [
              `$${props.payload.x.toFixed(2)}`,
              'Price',
            ]}
            labelFormatter={() => ''}
            contentStyle={{ fontSize: 12 }}
          />

          {/* 90% confidence band */}
          <ReferenceArea
            x1={confidence['90%'].min}
            x2={confidence['90%'].max}
            y1={0}
            y2={1}
            fill="#bfdbfe"
            strokeOpacity={0}
          />

          {/* 70% confidence band */}
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

      <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-gray-500">
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
