import { useEffect, useRef, useState } from 'react';
import {
  useAnalyzeCompanyMutation,
  useAnalyzeCompanyStreamMutation,
  useGetCompanyAnalysisReportsQuery,
  useGetCompanyHistoricalPriceQuery,
  useGetCompanyNewsQuery,
  useGetJobStatusQuery,
} from '../api';

import { selectAuth } from '@/features/auth/store/selectors';
import { useAppSelector } from '@/hooks/useAppSelector';
import { useToast } from '@/hooks/useToast';
import { CompanyData } from '../api/types';
import { useStreamingAnalysis } from '../hooks/useStreamingAnalysis';

import { CompanyActionsPanel } from './CompanyActionPanel';
import { CompanyAnalysisSummary } from './CompanyAnalysisSummary';
import { CompanyCharts } from './CompanyCharts';
import { CompanyHeader } from './CompanyHeader';
import { CompanyNewsComponent } from './CompanyNews';
import { CompanyOverview } from './CompanyOverview';
import { CompanySubscriptionModal } from './CompanySubscriptionModal';
import { StreamedAnalysisOutput } from './StreamedAnalysisOutput';

export const CompanyDetails = ({
  company_id,
  company,
}: {
  company_id: string;
  company: CompanyData;
}) => {
  const [jobId, setJobId] = useState<string | undefined>();
  const [showStreamModal, setShowStreamModal] = useState(false);
  const [isButtonsDisabled, setIsButtonsDisabled] = useState(false);
  const [showAutoTradeModal, setShowAutoTradeModal] = useState(false);

  const toast = useToast();
  const userId = useAppSelector(selectAuth)?.id;
  const resultRef = useRef<HTMLDivElement>(null);
  const streamRef = useRef<HTMLDivElement>(null);

  const [analyzeCompany] = useAnalyzeCompanyMutation();
  const [analyzeCompanyStream, { data: streamData }] = useAnalyzeCompanyStreamMutation();

  const streamJobId = streamData?.job_id;
  const { dedupedProgressEvents, isFinal } = useStreamingAnalysis(streamJobId, showStreamModal);

  const { data: history } = useGetCompanyHistoricalPriceQuery({
    exchange: company.exchange!,
    ticker: company.ticker,
  });

  const { data: news, isLoading: isNewsLoading } = useGetCompanyNewsQuery({
    companyId: company_id,
    companyName: company.name,
  });

  const { data: reports } = useGetCompanyAnalysisReportsQuery(company_id);

  const {
    data: analysis,
    isLoading,
    refetch,
  } = useGetJobStatusQuery(jobId!, {
    skip: !jobId || showStreamModal,
    pollingInterval: 3000,
  });

  const isAnalyzing = !!jobId && analysis?.status !== 'done';

  if (showStreamModal && isFinal) {
    setShowStreamModal(false);
    setIsButtonsDisabled(false);
  }

  const handleAnalyze = async () => {
    try {
      const result = await analyzeCompany({ company_id, company, history, news }).unwrap();
      setJobId(result.job_id);
    } catch (err) {
      console.error('Analyze failed', err);
    }
  };

  const handleAnalyzeAndStream = async () => {
    setShowStreamModal(false);
    setTimeout(() => {
      setShowStreamModal(true);
      setIsButtonsDisabled(true);
    }, 0);

    try {
      await analyzeCompanyStream({ company_id, company, history, news });
    } catch (err) {
      console.error('Stream analyze failed', err);
    }
  };

  const scrollToRef = (ref: React.RefObject<HTMLDivElement>) => {
    if (ref.current) {
      ref.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  useEffect(() => {
    if (jobId && analysis?.status === 'done' && resultRef.current) {
      setJobId(undefined);
      toast.success('Company analysis completed!');
      scrollToRef(resultRef as React.RefObject<HTMLDivElement>);
    }
  }, [analysis?.status]);

  useEffect(() => {
    if (dedupedProgressEvents.length > 0) {
      scrollToRef(streamRef as React.RefObject<HTMLDivElement>);
    }
  }, [dedupedProgressEvents]);

  return (
    <div className="max-w-3xl space-y-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <CompanyHeader company={company} />
      <CompanyOverview company={company} />
      {news && <CompanyNewsComponent news={news} isLoading={isNewsLoading} />}
      {reports && <CompanyCharts reports={reports} analysis={analysis} />}
      <CompanyActionsPanel
        onAnalyze={handleAnalyze}
        onAnalyzeStream={handleAnalyzeAndStream}
        isAnalyzing={isAnalyzing}
        showStreamModal={showStreamModal}
        isButtonsDisabled={isLoading || isAnalyzing || showStreamModal || isButtonsDisabled}
        onAutoTrade={() => setShowAutoTradeModal(true)}
        userId={userId}
        companyExists={!!company}
      />
      {analysis?.result && (
        <div ref={resultRef}>
          <CompanyAnalysisSummary analysis={analysis} />
        </div>
      )}
      {dedupedProgressEvents.length > 0 && (
        <div ref={streamRef}>
          <StreamedAnalysisOutput events={dedupedProgressEvents} />
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
    </div>
  );
};
