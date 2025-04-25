import { Link } from 'react-router';
import { SemanticResult } from '../api';

export const SemanticSearchResult = ({ result }: { result: SemanticResult }) => {
  return (
    <div className="rounded-lg border border-gray-200 p-4 shadow-sm transition hover:shadow-md">
      {/* Header */}
      <div className="mb-2 flex items-center justify-between">
        <h3 className="text-lg font-medium">
          <Link
            to={`/company/profile/${result.id}/${result.ticker}`}
            className="text-blue-600 hover:underline"
          >
            {result.name}
          </Link>
        </h3>
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
          to={`/company/profile/${result.id}/${result.ticker}`}
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          Start Analysis →
        </Link>
      </div>
    </div>
  );
};
