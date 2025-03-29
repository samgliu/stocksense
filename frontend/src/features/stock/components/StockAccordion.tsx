import { HistoryItem } from '../api/types';
import { useState } from 'react';

export const StockAccordion = ({ item }: { item: HistoryItem }) => {
  const [open, setOpen] = useState(false);

  const inputPreview =
    item.text_input && item.text_input.length > 100
      ? item.text_input.slice(0, 100) + '...'
      : (item.text_input ?? '(File upload)');

  return (
    <div className="rounded-lg border border-gray-200 bg-white shadow-sm transition hover:shadow-md">
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="flex w-full flex-col items-start px-4 py-3 text-left hover:bg-blue-50"
      >
        <div className="mb-1 text-sm text-gray-600">
          {new Date(item.created_at).toLocaleString()} • {item.model_used.toUpperCase()} •{' '}
          {item.source_type}
        </div>
        <div className="flex w-full items-center justify-between text-sm font-medium text-blue-700">
          <span className="truncate">{inputPreview}</span>
          <span className="ml-2 text-xs font-normal text-blue-500">{open ? '▲' : '▼'}</span>
        </div>
      </button>

      {open && (
        <div className="border-t px-4 py-3 text-sm text-gray-700">
          <div className="mb-2">
            <span className="font-medium text-gray-800">Input:</span>
            <p className="whitespace-pre-line text-gray-600">{item.text_input || '(File)'}</p>
          </div>
          <div>
            <span className="font-medium text-gray-800">Summary:</span>
            <p className="whitespace-pre-line text-gray-700">{item.summary}</p>
          </div>
        </div>
      )}
    </div>
  );
};
