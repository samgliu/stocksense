import { useLocation, useNavigate } from 'react-router';

import { useState } from 'react';
import { useSemanticSearchQuery } from '../api';
import { SemanticSearchResult } from './SemanticSearchResult';

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
      <div className="rounded-2xl border border-gray-100 bg-white/95 p-10 shadow-md">
        <h1 className="mb-4 flex items-center gap-2 text-2xl font-semibold tracking-tight text-blue-600">
          Semantic Search
        </h1>

        <form onSubmit={handleSubmit} className="mb-8 flex flex-col items-center gap-3 sm:flex-row">
          <input
            className="flex-1 rounded-full border border-gray-300 p-4 text-base shadow transition focus:border-blue-500 focus:outline-none"
            placeholder="e.g. Cloud security companies with high growth potential"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            type="submit"
            className={`rounded-full px-7 py-3 text-base font-semibold shadow transition ${
              isFetching
                ? 'cursor-not-allowed bg-gray-300 text-gray-500'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            } `}
            disabled={isFetching || query.trim().length < 3}
          >
            {isFetching ? 'Searching...' : 'Search'}
          </button>
        </form>

        {results.length > 0 && (
          <div className="mb-4 flex flex-col justify-between gap-3 rounded-lg bg-blue-50/60 p-3 text-sm text-gray-700 shadow sm:flex-row sm:items-center">
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
          <div className="mt-8 flex items-center justify-between text-base">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
              className={`rounded-full px-5 py-2 font-medium shadow transition ${page === 1 ? 'cursor-not-allowed bg-gray-200' : 'bg-blue-100 hover:bg-blue-200'} `}
            >
              ← Previous
            </button>

            <span className="font-semibold text-blue-700">
              Page {page} of {totalPages}
            </span>

            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page === totalPages}
              className={`rounded-full px-5 py-2 font-medium shadow transition ${page === totalPages ? 'cursor-not-allowed bg-gray-200' : 'bg-blue-100 hover:bg-blue-200'} `}
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
