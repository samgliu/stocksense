import { StockAccordion } from './StockAccordion';
import { useGetHistoryQuery } from '../api';

export const StockHistory = () => {
  const { data: history = [], isLoading, isError } = useGetHistoryQuery();

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
      <h2 className="mb-4 text-xl font-semibold text-gray-800">📜 Your Recent Analyses</h2>
      {history.map((item) => (
        <StockAccordion key={item.id} item={item} />
      ))}
    </div>
  );
};
