import { useMemo } from 'react';
import { CompanyPredictionHistoryChart } from './CompanyPredictionHistoryChart';
import { ForecastChart } from './ForecastChart';

import type { AnalysisReport } from '../api/types';

interface CompanyChartsProps {
  reports: AnalysisReport[];
  analysis: { result: string };
}

export const CompanyCharts = ({ reports, analysis }: CompanyChartsProps) => {
  const prediction = useMemo(() => {
    try {
      const parsed = JSON.parse(analysis.result);
      return parsed.prediction;
    } catch {
      return null;
    }
  }, [analysis?.result]);
  return (
    <>
      {reports && reports.length > 0 && <CompanyPredictionHistoryChart data={reports} />}
      {prediction && <ForecastChart prediction={prediction} />}
    </>
  );
};
