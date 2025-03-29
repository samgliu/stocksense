import { selectStockError, selectStockLoading, selectStockResult } from '../store/selectors';

import { Markdown } from '@/features/shared/Markdown';
import { useAppSelector } from '@/hooks/useAppSelector';

export const StockResult = () => {
  const result = useAppSelector(selectStockResult);
  const loading = useAppSelector(selectStockLoading);
  const error = useAppSelector(selectStockError);

  if (loading) {
    return (
      <div className="mt-4 animate-pulse rounded-md bg-gray-100 p-4 text-gray-600">
        Analyzing stock data...
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-4 rounded-md border border-red-300 bg-red-100 p-4 text-red-700">
        ⚠️ Error: {error}
      </div>
    );
  }

  if (!result) return null;

  return (
    <div className="mt-4 rounded-md border border-gray-200 bg-white p-4 shadow-sm">
      <h2 className="mb-2 text-lg font-semibold text-gray-800">AI Analysis</h2>
      <Markdown result={result} />
    </div>
  );
};
