import { Markdown } from '@/features/shared/Markdown';
import { formatCurrencyCompact } from '@/utils/formatters';
import { CompanyData } from '../api/types';

export const CompanyOverview = ({ company }: { company: CompanyData }) => {
  return (
    <>
      <div className="grid grid-cols-1 gap-4 text-sm text-gray-600 sm:grid-cols-2">
        <div>
          <p>📊 Sector: {company.sector || 'N/A'}</p>
          <p>🏭 Industry: {company.industry || 'N/A'}</p>
          <p>📅 IPO Date: {company.ipo_date || 'N/A'}</p>
          <p>🌍 Country: {company.country || 'N/A'}</p>
        </div>
        <div>
          <p>
            🌐 Website:{' '}
            {company.website ? (
              <a
                href={company.website}
                target="_blank"
                rel="noreferrer"
                className="text-blue-600 hover:underline"
              >
                {company.website}
              </a>
            ) : (
              'N/A'
            )}
          </p>
          {company.phone && <p>📞 Phone: {company.phone}</p>}
          {company.address && (
            <p>
              🏠 {company.address}, {company.city}, {company.state} {company.zip}
            </p>
          )}
        </div>
      </div>
      <div className="grid grid-cols-1 gap-4 border-t pt-4 text-sm text-gray-700 sm:grid-cols-2">
        <p>
          💰 Market Cap: {company.market_cap ? formatCurrencyCompact(company.market_cap) : 'N/A'}
        </p>
        <p>📈 Current Price: ${company.current_price?.toFixed(2) || 'N/A'}</p>
        <p>👥 Employees: {company.fulltime_employees?.toLocaleString() || 'N/A'}</p>
      </div>
      {company.summary && (
        <p className="line-clamp-5 overflow-auto text-gray-700">{company.summary}</p>
      )}

      {/* Insights */}
      {company.insights && (
        <div className="mt-6 max-h-[250px] overflow-auto rounded bg-gray-50 p-4 text-sm text-gray-800 shadow-inner">
          <Markdown result={company.insights} />
        </div>
      )}
    </>
  );
};
