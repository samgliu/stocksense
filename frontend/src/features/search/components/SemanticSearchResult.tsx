import { Link } from 'react-router-dom';
import { SemanticResult } from '../api';

export const SemanticSearchResult = ({ result }: { result: SemanticResult }) => {
  return (
    <div className="rounded-lg border border-gray-200 p-4 shadow-sm transition hover:shadow-md">
      {/* Header */}
      <div className="mb-2 flex items-center justify-between">
        <div className="text-lg font-semibold text-gray-900">{result.name}</div>
        <div className="text-sm text-gray-600">{result.ticker}</div>
      </div>

      {/* Summary */}
      <p className="mb-3 line-clamp-4 overflow-auto text-sm text-gray-700">
        {result.summary || 'No summary available.'}
      </p>

      {/* Footer: meta on left, action on right */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex flex-wrap gap-3">
          {result.sector && <span>📊 {result.sector}</span>}
          {result.industry && <span>🏭 {result.industry}</span>}
          {result.domain && <span>🔗 {result.domain}</span>}
          <span>🎯 Score: {(result.score * 100).toFixed(2)}%</span>
        </div>

        <Link
          to={`/company/${result.id}/${result.ticker}`}
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          View Analysis →
        </Link>
      </div>
    </div>
  );
};
