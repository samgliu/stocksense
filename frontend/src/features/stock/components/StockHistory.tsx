import { useEffect, useState } from 'react';

import { StockAccordion } from './StockAccordion';

export interface HistoryItem {
  id: string;
  summary: string;
  created_at: string;
  source_type: string;
  model_used: string;
  text_input: string | null;
}

export const StockHistory = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/stock/history`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setHistory(data);
      } catch (err) {
        console.error('Failed to fetch history:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  if (loading) {
    return <div className="mt-10 text-center text-sm text-gray-500">Loading history...</div>;
  }

  if (!history.length) {
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
