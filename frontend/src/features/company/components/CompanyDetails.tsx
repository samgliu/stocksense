import { useEffect, useMemo, useRef, useState } from 'react';
import {
  useAnalyzeCompanyMutation,
  useAnalyzeCompanyStreamMutation,
  useGetCompanyAnalysisReportsQuery,
  useGetCompanyHistoricalPriceQuery,
  useGetCompanyNewsQuery,
  useGetJobStatusQuery,
} from '../api';

import { selectAuth } from '@/features/auth/store/selectors';
import { Markdown } from '@/features/shared/Markdown';
import { useAppSelector } from '@/hooks/useAppSelector';
import { useToast } from '@/hooks/useToast';
import { formatCurrencyCompact } from '@/utils/formatters';
import { CompanyData } from '../api/types';
import { useJobProgressWebSocket } from '../api/useJobProgressWebSocket';
import { CompanyNewsComponent } from './CompanyNews';
import { CompanyPredictionHistoryChart } from './CompanyPredictionHistoryChart';
import { CompanySubscriptionModal } from './CompanySubscriptionModal';
import { ForecastChart } from './ForecastChart';
import { StockMiniChart } from './StockMiniChart';

export const CompanyDetails = ({
  company_id,
  company,
}: {
  company_id: string;
  company: CompanyData;
}) => {
  const [analyzeCompany, { data: jobData }] = useAnalyzeCompanyMutation();
  const [analyzeCompanyStream, { data: streamData }] = useAnalyzeCompanyStreamMutation();
  const [showAutoTradeModal, setShowAutoTradeModal] = useState(false);
  const [showStreamModal, setShowStreamModal] = useState(false);
  const [isButtonsDisabled, setIsButtonsDisabled] = useState(false);
  const userId = useAppSelector(selectAuth)?.id;
  const resultRef = useRef<HTMLDivElement | null>(null);
  const streamResultRef = useRef<HTMLDivElement | null>(null);
  const toast = useToast();

  const jobId = jobData?.job_id;
  const streamJobId = streamData?.job_id;
  const [progressEvents, setProgressEvents] = useState<any[]>([]);

  useEffect(() => {
    setProgressEvents([]);
  }, [streamJobId]);

  const progressEventsFromWebSocket = useJobProgressWebSocket(
    showStreamModal && streamJobId ? streamJobId : undefined,
  );

  useEffect(() => {
    setProgressEvents((prevProgressEvents) => [
      ...prevProgressEvents,
      ...progressEventsFromWebSocket,
    ]);
  }, [progressEventsFromWebSocket]);

  // Handler for Stream & Analyze button
  const handleAnalyzeAndStream = async () => {
    setShowStreamModal(true);
    setIsButtonsDisabled(true);
    try {
      await analyzeCompanyStream({ company_id, company, history, news });
    } catch (err) {
      console.error('Failed to analyze company', err);
    }
  };

  // Get historical data
  const { data: history } = useGetCompanyHistoricalPriceQuery({
    exchange: company.exchange!,
    ticker: company.ticker,
  });

  // Company News
  const { data: news, isLoading: isNewsLoading } = useGetCompanyNewsQuery({
    companyId: company_id,
    companyName: company.name,
  });

  // Historical Reports
  const { data: reports } = useGetCompanyAnalysisReportsQuery(company_id);

  const {
    data: analysis,
    isLoading,
    refetch,
  } = useGetJobStatusQuery(jobId!, {
    skip: !jobId || showStreamModal,
    pollingInterval: 0,
  });

  const isAnalyzing = !!jobId && analysis?.status !== 'done';

  useEffect(() => {
    if (!jobId || analysis?.status === 'done' || showStreamModal) return;
    const interval = setInterval(() => refetch(), 3000);
    return () => clearInterval(interval);
  }, [jobId, analysis?.status, refetch, showStreamModal]);

  useEffect(() => {
    if (analysis?.status === 'done') {
      toast.success('Company analysis completed!');
      resultRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [analysis?.status]);

  const handleAnalyze = async () => {
    try {
      await analyzeCompany({ company_id, company, history, news });
    } catch (err) {
      console.error('Failed to analyze company', err);
    }
  };

  const extractRelevantOutput = (event: any) => {
    switch (event.node) {
      case 'gcs_data':
        return { gcs_snippets: event.output?.gcs_snippets ?? [] };
      case 'run_sentiment_analysis':
        return { sentiment_analysis: event.output?.sentiment_analysis ?? null };
      case 'analyze': {
        let result = event.output?.result;
        if (typeof result === 'string') {
          try {
            result = JSON.parse(result);
          } catch {
            // fallback: keep as string
          }
        }
        return { insights: result?.insights ?? result, prediction: result?.prediction };
      }
      case 'scrape_domain':
        return { company: event.output?.payload?.company ?? null };
      default:
        return {};
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

  const filteredProgressEvents = useMemo(
    () =>
      progressEvents.map((event: any) => ({
        ...event,
        filteredOutput: extractRelevantOutput(event),
      })),
    [progressEvents],
  );

  const dedupedProgressEvents = useMemo(() => {
    const nodeMap = new Map();
    for (const event of filteredProgressEvents) {
      nodeMap.set(event.node, event);
    }
    return Array.from(nodeMap.values());
  }, [filteredProgressEvents]);

  useEffect(() => {
    if (dedupedProgressEvents.length > 0 && streamResultRef.current) {
      setTimeout(() => {
        streamResultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 0);
    }
  }, [dedupedProgressEvents]);

  useEffect(() => {
    if (showStreamModal && dedupedProgressEvents.some((ev) => ev.is_final)) {
      setShowStreamModal(false);
      setIsButtonsDisabled(false);
    }
    if (!showStreamModal && analysis?.status === 'done') {
      setIsButtonsDisabled(false);
    }
  }, [dedupedProgressEvents, analysis?.status, showStreamModal]);

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
        <p>
          💰 Market Cap: {company.market_cap ? formatCurrencyCompact(company.market_cap) : 'N/A'}
        </p>
        <p>📈 Current Price: ${company.current_price?.toFixed(2) || 'N/A'}</p>
        <p>👥 Employees: {company.fulltime_employees?.toLocaleString() || 'N/A'}</p>
      </div>

      {/* Summary */}
      {company.summary && (
        <p className="line-clamp-5 overflow-auto text-gray-700">{company.summary}</p>
      )}

      {/* Insights */}
      {company.insights && (
        <div className="mt-6 max-h-[250px] overflow-auto rounded bg-gray-50 p-4 text-sm text-gray-800 shadow-inner">
          <Markdown result={company.insights} />
        </div>
      )}

      {/* Latest News */}
      <div className="mt-4 min-h-[150px]">
        <h3 className="mb-2 text-lg font-semibold text-gray-800">📰 Recent News</h3>
        {isNewsLoading ? (
          <div className="animate-pulse space-y-3">
            <div className="h-4 w-3/4 rounded bg-gray-200" />
            <div className="h-4 w-5/6 rounded bg-gray-200" />
            <div className="h-4 w-2/3 rounded bg-gray-200" />
          </div>
        ) : news && news.length > 0 ? (
          <CompanyNewsComponent news={news} isLoading={isNewsLoading} />
        ) : (
          <p className="text-sm text-gray-500">No recent news found.</p>
        )}
      </div>

      {/* Analyze Button + Auto-Trade + Status */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Left side: Analyze button + status + Stream button */}
        <div className="flex items-center gap-4">
          <button
            onClick={handleAnalyze}
            disabled={isLoading || isAnalyzing || showStreamModal || isButtonsDisabled}
            className={`rounded px-4 py-2 text-white ${
              isLoading || isAnalyzing || showStreamModal || isButtonsDisabled
                ? 'cursor-not-allowed bg-gray-400'
                : 'cursor-pointer bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isLoading || isAnalyzing || showStreamModal ? 'Analyzing...' : '🔍 Analyze Company'}
          </button>

          {/* Stream & Analyze Button */}
          <button
            onClick={handleAnalyzeAndStream}
            disabled={isLoading || isAnalyzing || showStreamModal || isButtonsDisabled}
            className={`rounded px-4 py-2 text-white ${isLoading || isAnalyzing || showStreamModal || isButtonsDisabled ? 'cursor-not-allowed bg-gray-400' : 'cursor-pointer bg-purple-600 hover:bg-purple-700'}`}
          >
            {isLoading || isAnalyzing || showStreamModal
              ? 'Analyzing & Streaming...'
              : '📡 Stream & Analyze'}
          </button>
        </div>

        {/* Right side: Auto-Trade button */}
        <button
          onClick={() => setShowAutoTradeModal(true)}
          className="cursor-pointer rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700"
          disabled={!userId || !company}
        >
          📈 Auto-Trade
        </button>
      </div>

      {/* Historical Report Chart */}
      {reports && reports.length > 0 && <CompanyPredictionHistoryChart data={reports} />}

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
      {showAutoTradeModal && userId && (
        <CompanySubscriptionModal
          company_id={company_id}
          ticker={company.ticker}
          onClose={() => setShowAutoTradeModal(false)}
          user_id={userId}
        />
      )}

      <div ref={streamResultRef} />
      {dedupedProgressEvents.map((e, idx) => {
        // Scraped Text
        if (e.filteredOutput.scraped_text) {
          return (
            <div
              key="scraped_text"
              className="mt-4 mb-4 rounded border border-gray-200 bg-white px-5 py-4 shadow-sm"
            >
              <h4 className="mb-2 font-semibold">Scraped Text</h4>
              <div className="max-h-48 overflow-auto text-sm whitespace-pre-wrap text-gray-800">
                {e.filteredOutput.scraped_text}
              </div>
            </div>
          );
        }
        // Snippets
        if (e.node === 'gcs_data' && e.filteredOutput.gcs_snippets?.length) {
          return (
            <div
              key="gcs_data"
              className="mt-4 mb-4 rounded border border-gray-200 bg-white px-5 py-4 shadow-sm"
            >
              <h4 className="mb-2 font-semibold">Snippets</h4>
              <ul className="ml-5 max-h-40 list-disc overflow-y-auto text-sm text-gray-800">
                {e.filteredOutput.gcs_snippets.map((snippet: string, i: number) => (
                  <li key={i} className="mb-1">
                    {snippet}
                  </li>
                ))}
              </ul>
            </div>
          );
        }
        // Sentiment Analysis
        if (e.node === 'run_sentiment_analysis' && e.filteredOutput.sentiment_analysis) {
          const sentiment = e.filteredOutput.sentiment_analysis;
          return (
            <div
              key="sentiment"
              className="mt-4 mb-4 rounded border border-gray-200 bg-white px-5 py-4 shadow-sm"
            >
              <h4 className="mb-2 font-semibold">Sentiment Analysis</h4>
              <div className="mb-1 flex flex-wrap gap-4 text-sm text-gray-900">
                <div>
                  <span className="font-medium">Sentiment:</span>{' '}
                  <span className="capitalize">{sentiment.sentiment}</span>
                </div>
                <div>
                  <span className="font-medium">Score:</span>{' '}
                  <span className="font-mono">{sentiment.score.toFixed(2)}</span>
                </div>
              </div>
              <div className="text-sm text-gray-700">{sentiment.summary}</div>
            </div>
          );
        }
        // LLM Output
        if (e.node === 'analyze' && e.filteredOutput.insights) {
          return (
            <div
              key="analyze"
              className="mt-4 mb-4 rounded border border-gray-200 bg-white px-5 py-4 shadow-sm"
            >
              <h4 className="mb-2 font-semibold">Streamed LLM Output</h4>
              <div className="text-sm text-gray-800">
                <Markdown result={e.filteredOutput.insights} />
              </div>
            </div>
          );
        }
        return null;
      })}
    </div>
  );
};
