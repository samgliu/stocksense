import { useMemo } from 'react';
import { CompanyPredictionHistoryChart } from './CompanyPredictionHistoryChart';
import { ForecastChart } from './ForecastChart';

export const CompanyCharts = ({ reports, analysis }: { reports: any[]; analysis: any }) => {
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
