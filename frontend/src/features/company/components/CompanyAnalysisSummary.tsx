import { Markdown } from '@/features/shared/Markdown';
import { useMemo } from 'react';

interface AnalysisSummaryProps {
  analysis: { job_id?: string | undefined; status: string; result?: string | undefined };
}

export const CompanyAnalysisSummary = ({ analysis }: AnalysisSummaryProps) => {
  if (!analysis?.result) return null;
  const insights = useMemo(() => {
    if (!analysis?.result) return null;
    try {
      const parsed = JSON.parse(analysis.result);
      return parsed.insights;
    } catch {
      return analysis.result;
    }
  }, [analysis?.result]);
  return (
    <div className="mt-6 rounded bg-gray-50 p-4 text-sm text-gray-800 shadow-inner">
      <h3 className="mb-2 text-lg font-semibold">AI Analysis Result</h3>
      <Markdown result={insights} />
    </div>
  );
};
