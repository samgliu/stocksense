import { CompanyData } from '../api/types';

export const CompanyHeader = ({ company }: { company: CompanyData }) => {
  return (
    <div className="flex items-center justify-between space-x-4">
      <div className="flex items-center space-x-4">
        <div className="flex h-16 w-16 items-center justify-center rounded border border-gray-200 bg-gray-700 shadow-sm">
          <img
            src={company.image}
            alt={`${company.name} logo`}
            className="h-12 w-12 object-contain"
          />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {company.name} <span className="text-sm text-gray-500">({company.ticker})</span>
          </h1>
          {company.ceo && <p className="text-sm text-gray-500">👤 CEO: {company.ceo}</p>}
          {company.exchange && <p className="text-xs text-gray-400">{company.exchange}</p>}
        </div>
      </div>
    </div>
  );
};
