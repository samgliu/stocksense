import { useSemanticSearchQuery } from '../api';
import { useState } from 'react';

export const SemanticSearch = () => {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const { data: results, isFetching } = useSemanticSearchQuery(submittedQuery, {
    skip: submittedQuery.length < 3,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim().length >= 3 && !isFetching) {
      setSubmittedQuery(query.trim());
    }
  };

  return (
    <div className="mx-auto max-w-3xl p-6">
      <h2 className="mb-4 text-2xl font-bold">🧪 Semantic Search</h2>

      <form onSubmit={handleSubmit} className="mb-4 flex gap-2">
        <input
          className="w-full rounded border p-2"
          placeholder="e.g. AI chip makers with strong growth"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          type="submit"
          className={`rounded px-4 py-2 text-white ${
            isFetching
              ? 'cursor-not-allowed bg-gray-400'
              : 'cursor-pointer bg-blue-600 hover:bg-blue-700'
          }`}
          disabled={isFetching || query.trim().length < 3}
        >
          {isFetching ? 'Searching...' : 'Search'}
        </button>
      </form>

      {isFetching && <p className="text-gray-500">Searching...</p>}

      <ul className="space-y-4">
        {results?.map((r) => (
          <li key={r.id} className="rounded border p-4 shadow-sm">
            <div className="flex justify-between">
              <span className="font-semibold">{r.name}</span>
              <span className="text-sm text-gray-600">{r.ticker}</span>
            </div>
            <p className="mt-2 text-sm text-gray-700">{r.summary}</p>
            <p className="mt-1 text-xs text-gray-400">Match Score: {r.score.toFixed(4)}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};
