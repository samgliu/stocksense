import {
  CompanyData,
  useAnalyzeCompanyMutation,
  useGetCompanyHistoricalPriceQuery,
  useGetJobStatusQuery,
} from '../api';
import { useEffect, useMemo } from 'react';

import { ForecastChart } from './ForecastChart';
import { Markdown } from '@/features/shared/Markdown';
import { StockMiniChart } from './StockMiniChart';

export const CompanyDetails = ({ company }: { company: CompanyData }) => {
  const [analyzeCompany, { data: jobData }] = useAnalyzeCompanyMutation();
  // Get historical data
  const { data: history } = useGetCompanyHistoricalPriceQuery({
    exchange: company.exchange!,
    ticker: company.ticker,
  });
  const jobId = jobData?.job_id;

  const {
    data: analysis,
    isLoading,
    refetch,
  } = useGetJobStatusQuery(jobId!, {
    skip: !jobId,
    pollingInterval: 0,
  });
  const hasJob = !!jobId;
  const isAnalyzing = hasJob && analysis?.status !== 'done';

  useEffect(() => {
    if (!jobId || analysis?.status === 'done') return;

    const interval = setInterval(() => {
      refetch();
    }, 3000);

    return () => clearInterval(interval);
  }, [jobId, analysis?.status, refetch]);

  const handleAnalyze = async () => {
    try {
      await analyzeCompany({ company, history });
    } catch (err) {
      console.error('Failed to analyze company', err);
    }
  };

  const insights = useMemo(() => {
    if (!analysis?.result) return null;
    const parsedAnalysis = JSON.parse(analysis.result);
    return parsedAnalysis.insights;
  }, [analysis?.result]);

  const prediction = useMemo(() => {
    if (!analysis?.result) return null;
    const parsedAnalysis = JSON.parse(analysis.result);
    return parsedAnalysis.prediction;
  }, [analysis?.result]);

  return (
    <div className="max-w-3xl space-y-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between space-x-4">
        <div className="flex items-center space-x-4">
          {company.image && (
            <img
              src={company.image}
              alt={`${company.name} logo`}
              className="h-16 w-16 rounded border border-gray-200 bg-gray-800 p-2 shadow-sm"
            />
          )}
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {company.name} <span className="text-sm text-gray-500">({company.ticker})</span>
            </h1>
            {company.ceo && <p className="text-sm text-gray-500">👤 CEO: {company.ceo}</p>}
            {company.exchange && <p className="text-xs text-gray-400">{company.exchange}</p>}
          </div>
        </div>

        {history && <StockMiniChart data={history} />}
      </div>
      {/* Company Info */}
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
              🏠 Address: {company.address}, {company.city}, {company.state} {company.zip}
            </p>
          )}
        </div>
      </div>

      {/* Financials */}
      <div className="grid grid-cols-1 gap-4 border-t pt-4 text-sm text-gray-700 sm:grid-cols-2">
        <p>💰 Market Cap: ${company.market_cap?.toLocaleString() || 'N/A'}</p>
        <p>📈 Current Price: ${company.current_price?.toFixed(2) || 'N/A'}</p>
        <p>👥 Employees: {company.fulltime_employees?.toLocaleString() || 'N/A'}</p>
      </div>

      {/* Summary (clamped to 3 lines) */}
      {company.summary && (
        <p className="line-clamp-5 overflow-auto text-gray-700">{company.summary}</p>
      )}
      <button
        onClick={handleAnalyze}
        disabled={isLoading || isAnalyzing}
        className={`mt-6 rounded px-4 py-2 text-white ${
          isLoading || isAnalyzing
            ? 'cursor-not-allowed bg-gray-400'
            : 'cursor-pointer bg-blue-600 hover:bg-blue-700'
        }`}
      >
        {isLoading || isAnalyzing ? 'Analyzing...' : '🔍 Analyze Company'}
      </button>
      {prediction && <ForecastChart prediction={prediction} />}
      {insights && (
        <div className="mt-6 rounded bg-gray-50 p-4 text-sm text-gray-800 shadow-inner">
          <h3 className="mb-2 text-lg font-semibold">AI Analysis Result</h3>
          <Markdown result={insights} />
        </div>
      )}
    </div>
  );
};
