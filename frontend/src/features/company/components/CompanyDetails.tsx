import {
  CompanyData,
  useAnalyzeCompanyMutation,
  useGetCompanyHistoricalPriceQuery,
  useGetJobStatusQuery,
} from '../api';
import { useEffect, useMemo, useRef } from 'react';

import { ForecastChart } from './ForecastChart';
import { Markdown } from '@/features/shared/Markdown';
import { StockMiniChart } from './StockMiniChart';
import { useToast } from '@/hooks/useToast';

export const CompanyDetails = ({
  company_id,
  company,
}: {
  company_id: string;
  company: CompanyData;
}) => {
  const [analyzeCompany, { data: jobData }] = useAnalyzeCompanyMutation();
  const resultRef = useRef<HTMLDivElement | null>(null);
  const toast = useToast();

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

  const isAnalyzing = !!jobId && analysis?.status !== 'done';

  useEffect(() => {
    if (!jobId || analysis?.status === 'done') return;
    const interval = setInterval(() => refetch(), 3000);
    return () => clearInterval(interval);
  }, [jobId, analysis?.status, refetch]);

  useEffect(() => {
    if (analysis?.status === 'done') {
      toast.success('Company analysis completed!');
      resultRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [analysis?.status]);

  const handleAnalyze = async () => {
    try {
      await analyzeCompany({ company_id, company, history });
    } catch (err) {
      console.error('Failed to analyze company', err);
    }
  };

  const insights = useMemo(() => {
    if (!analysis?.result) return null;
    try {
      const parsed = JSON.parse(analysis.result);
      return parsed.insights;
    } catch {
      return analysis.result;
    }
  }, [analysis?.result]);

  const prediction = useMemo(() => {
    if (!analysis?.result) return null;
    try {
      const parsed = JSON.parse(analysis.result);
      return parsed.prediction;
    } catch {
      return null;
    }
  }, [analysis?.result]);

  // --- Job Status Label
  const jobStatusText = useMemo(() => {
    if (!jobId) return '';
    if (analysis?.status === 'done') return '✅ Analysis complete';
    if (analysis?.status === 'processing') return '🔄 Processing...';
    return '🕓 Queued...';
  }, [jobId, analysis?.status]);

  return (
    <div className="max-w-3xl space-y-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      {/* Header */}
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
              🏠 {company.address}, {company.city}, {company.state} {company.zip}
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

      {/* Summary */}
      {company.summary && (
        <p className="line-clamp-5 overflow-auto text-gray-700">{company.summary}</p>
      )}

      {/* Analyze Button + Status */}
      <div className="flex items-center space-x-4">
        <button
          onClick={handleAnalyze}
          disabled={isLoading || isAnalyzing}
          className={`rounded px-4 py-2 text-white ${
            isLoading || isAnalyzing
              ? 'cursor-not-allowed bg-gray-400'
              : 'cursor-pointer bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {isLoading || isAnalyzing ? 'Analyzing...' : '🔍 Analyze Company'}
        </button>
        {jobStatusText && <span className="text-sm text-gray-500">{jobStatusText}</span>}
      </div>

      {/* Result */}
      {prediction && (
        <div ref={resultRef}>
          <ForecastChart prediction={prediction} />
        </div>
      )}
      {insights && (
        <div className="mt-6 rounded bg-gray-50 p-4 text-sm text-gray-800 shadow-inner">
          <h3 className="mb-2 text-lg font-semibold">AI Analysis Result</h3>
          <Markdown result={insights} />
        </div>
      )}
    </div>
  );
};
