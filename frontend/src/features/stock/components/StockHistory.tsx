import { useMemo, useState } from 'react';

import { StockAccordion } from './StockAccordion';
import { useGetHistoryQuery } from '../api';

const PAGE_SIZE_OPTIONS = [5, 10, 25, 50];

export const StockHistory = () => {
  const { data: history = [], isLoading, isError } = useGetHistoryQuery();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const totalPages = Math.ceil(history.length / pageSize);

  const currentPageItems = useMemo(() => {
    const start = (page - 1) * pageSize;
    return history.slice(start, start + pageSize);
  }, [history, page, pageSize]);

  const handlePrev = () => setPage((prev) => Math.max(prev - 1, 1));
  const handleNext = () => setPage((prev) => Math.min(prev + 1, totalPages));
  const handlePageSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setPageSize(Number(e.target.value));
    setPage(1);
  };

  if (isLoading) {
    return <div className="mt-10 text-center text-sm text-gray-500">Loading history...</div>;
  }

  if (isError || !history.length) {
    return (
      <div className="mt-10 text-center text-sm text-gray-500">
        No history yet. Start by analyzing some stock info.
      </div>
    );
  }

  return (
    <div className="mt-10 max-w-3xl space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-800">📜 Your Recent Analyses</h2>

        <div className="text-sm text-gray-600">
          Show:{' '}
          <select
            value={pageSize}
            onChange={handlePageSizeChange}
            className="rounded-md border border-gray-300 bg-white px-2 py-1 text-sm text-gray-700 shadow-sm focus:border-blue-500 focus:outline-none"
          >
            {PAGE_SIZE_OPTIONS.map((size) => (
              <option key={size} value={size}>
                {size} per page
              </option>
            ))}
          </select>
        </div>
      </div>

      {currentPageItems.map((item) => (
        <StockAccordion key={item.id} item={item} />
      ))}

      <div className="mt-6 flex flex-col items-center justify-between gap-2 text-sm text-gray-600 sm:flex-row">
        <div>
          Page <strong>{page}</strong> of {totalPages}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handlePrev}
            disabled={page === 1}
            className={`rounded-md border px-3 py-1 ${
              page === 1 ? 'cursor-not-allowed bg-gray-100' : 'hover:bg-gray-100'
            }`}
          >
            ← Prev
          </button>

          <button
            onClick={handleNext}
            disabled={page === totalPages}
            className={`rounded-md border px-3 py-1 ${
              page === totalPages ? 'cursor-not-allowed bg-gray-100' : 'hover:bg-gray-100'
            }`}
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  );
};
