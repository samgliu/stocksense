import { useMemo, useState } from 'react';

import { titleCase } from '@/features/autoTrade/components/helpers';
import { HistoryItem } from '../api/types';

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
    <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-md transition hover:border-blue-100 hover:shadow-lg">
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="flex w-full items-center justify-between bg-transparent p-0 text-left focus:outline-none"
      >
        <div className="flex flex-1 flex-col gap-1">
          <span className="mb-1 text-xs text-gray-400">
            {new Date(item.created_at).toLocaleString()} • {titleCase(item.source_type)} •{' '}
            <span className="uppercase">{item.model_used}</span>
          </span>
          <span className="truncate text-base font-semibold text-gray-800">{inputPreview}</span>
        </div>
        <span className="ml-4 flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-lg text-blue-500 transition-transform hover:bg-blue-50">
          {open ? <>&#x25B2;</> : <>&#x25BC;</>}
        </span>
      </button>

      {open && (
        <div className="mt-4 space-y-6 border-t pt-4 text-[15px] text-gray-700">
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
