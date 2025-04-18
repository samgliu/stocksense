import { SemanticSearchResult } from './SemanticSearchResult';
import { useSemanticSearchQuery } from '../api';
import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const PAGE_SIZES = [5, 10, 20];

export const SemanticSearch = () => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const initialQuery: string = params.get('q') || '';
  const pageParam = params.get('page');
  const initialPage: number = pageParam && !isNaN(Number(pageParam)) ? parseInt(pageParam, 10) : 10;
  const [query, setQuery] = useState(initialQuery);
  const [submittedQuery, setSubmittedQuery] = useState(initialQuery);
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(10);
  const navigate = useNavigate();

  const { data: results = [], isFetching } = useSemanticSearchQuery(submittedQuery, {
    skip: submittedQuery.length < 3,
  });

  const totalResults = results.length;
  const totalPages = Math.ceil(totalResults / pageSize);
  const pagedResults = results.slice((page - 1) * pageSize, page * pageSize);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim().length >= 3 && !isFetching) {
      setSubmittedQuery(query.trim());
      setPage(1);
      navigate(`/semantic-search?q=${encodeURIComponent(query.trim())}&page=1`);
    }
  };

  const handlePageChange = (newPage: number) => {
    setPage(Math.max(1, Math.min(newPage, totalPages)));
  };

  return (
    <div className="mx-auto max-w-3xl p-6">
      <h2 className="mb-2 text-xl font-semibold text-gray-800">🔍 Semantic Company Search</h2>

      <form onSubmit={handleSubmit} className="mb-6 flex flex-col gap-2 sm:flex-row">
        <input
          className="flex-1 rounded border border-gray-300 p-3 text-sm shadow-sm focus:border-blue-500 focus:outline-none"
          placeholder="e.g. Cloud security companies with high growth potential"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          type="submit"
          className={`rounded px-5 py-2 text-sm font-medium text-white ${
            isFetching
              ? 'cursor-not-allowed bg-gray-400'
              : 'cursor-pointer bg-blue-600 hover:bg-blue-700'
          }`}
          disabled={isFetching || query.trim().length < 3}
        >
          {isFetching ? 'Searching...' : 'Search'}
        </button>
      </form>

      {results.length > 0 && (
        <div className="mb-4 flex flex-col items-start justify-between gap-2 text-sm text-gray-600 sm:flex-row sm:items-center">
          <div>
            Showing {pagedResults.length} of {totalResults} results
          </div>
          <div className="flex items-center gap-2">
            <label htmlFor="pageSize" className="text-sm">
              Results per page:
            </label>
            <select
              id="pageSize"
              className="rounded border border-gray-300 p-1 text-sm"
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setPage(1);
              }}
            >
              {PAGE_SIZES.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {!isFetching && submittedQuery && pagedResults.length === 0 && (
        <div className="text-sm text-gray-500">No matching companies found.</div>
      )}

      <div className="space-y-4">
        {pagedResults.map((r) => (
          <SemanticSearchResult key={r.id} result={r} />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-between text-sm text-gray-600">
          <button
            onClick={() => handlePageChange(page - 1)}
            disabled={page === 1}
            className={`rounded px-3 py-1 ${
              page === 1 ? 'cursor-not-allowed bg-gray-200' : 'bg-blue-100 hover:bg-blue-200'
            }`}
          >
            ← Previous
          </button>

          <span>
            Page {page} of {totalPages}
          </span>

          <button
            onClick={() => handlePageChange(page + 1)}
            disabled={page === totalPages}
            className={`rounded px-3 py-1 ${
              page === totalPages
                ? 'cursor-not-allowed bg-gray-200'
                : 'bg-blue-100 hover:bg-blue-200'
            }`}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
};
