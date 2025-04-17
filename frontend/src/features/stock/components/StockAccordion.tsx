import { useMemo, useState } from 'react';

import { HistoryItem } from '../api/types';
import { titleCase } from '@/features/autoTrade/components/helpers';

export const StockAccordion = ({ item }: { item: HistoryItem }) => {
  const [open, setOpen] = useState(false);

  const inputPreview =
    item.text_input && item.text_input.length > 100
      ? item.text_input.slice(0, 100) + '...'
      : (item.text_input ?? '(File upload)');

  const parsedSummary = useMemo(() => {
    try {
      return JSON.parse(item.summary);
    } catch {
      return null;
    }
  }, [item.summary]);

  const insights = parsedSummary?.insights ?? item.summary;
  const prediction = parsedSummary?.prediction;

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm transition hover:shadow-md">
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-blue-50"
      >
        <div className="flex flex-col">
          <span className="text-xs text-gray-500">
            {new Date(item.created_at).toLocaleString()} •{' '}
            <span className="uppercase">{item.model_used}</span> • {titleCase(item.source_type)}
          </span>
          <span className="mt-1 truncate text-sm font-medium text-blue-700">{inputPreview}</span>
        </div>
        <span className="ml-2 text-xs font-bold text-blue-500">{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className="space-y-4 border-t px-4 py-4 text-sm text-gray-700">
          <div>
            <h4 className="mb-1 font-semibold text-gray-800">Input:</h4>
            <p className="whitespace-pre-line text-gray-600">{item.text_input || '(File)'}</p>
          </div>

          <div>
            <h4 className="mb-1 font-semibold text-gray-800">Insights:</h4>
            <p className="whitespace-pre-line text-gray-700">{insights}</p>
          </div>

          {prediction && (
            <div>
              <h4 className="mb-1 font-semibold text-gray-800">Prediction:</h4>
              <div className="space-y-1 text-gray-700">
                <div className="flex flex-wrap items-center gap-x-4">
                  <span>📉 Min: ${prediction.min}</span>
                  <span>📈 Max: ${prediction.max}</span>
                  <span>📊 Avg: ${prediction.average}</span>
                </div>
                <div className="flex flex-wrap items-center gap-x-4">
                  {prediction.confidence?.['70%'] && (
                    <span>
                      🔷 70%: ${prediction.confidence['70%'].min}–$
                      {prediction.confidence['70%'].max}
                    </span>
                  )}
                  {prediction.confidence?.['90%'] && (
                    <span>
                      🟠 90%: ${prediction.confidence['90%'].min}–$
                      {prediction.confidence['90%'].max}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
