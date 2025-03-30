import { Link } from 'react-router-dom';
import { SemanticResult } from '../api';

export const SemanticSearchResult = ({ result }: { result: SemanticResult }) => {
  return (
    <li className="rounded-lg border border-gray-200 p-4 shadow-sm transition hover:bg-gray-50">
      <div className="mb-1 flex items-center justify-between">
        <h3 className="text-lg font-medium">
          <Link
            to={`/company/${result.id}/${result.ticker}`}
            className="text-blue-600 hover:underline"
          >
            {result.name}
          </Link>
        </h3>
        <span className="text-sm text-gray-600">{result.ticker}</span>
      </div>
      <p className="mb-2 line-clamp-4 overflow-auto text-sm text-gray-700">
        {result.summary || 'No summary available.'}
      </p>
      <div className="flex flex-wrap gap-2 text-xs text-gray-500">
        {result.sector && <span>📊 {result.sector}</span>}
        {result.industry && <span>🏭 {result.industry}</span>}
        {result.domain && <span>🔗 {result.domain}</span>}
        <span>🎯 Score: {result.score.toFixed(4)}</span>
      </div>
    </li>
  );
};
