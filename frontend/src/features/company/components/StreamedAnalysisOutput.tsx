import { Markdown } from '@/features/shared/Markdown';
import { ForecastChart } from './ForecastChart';

import type { JobProgressEvent } from '../hooks/useJobProgressWebSocket';

interface StreamedAnalysisOutputProps {
  events: (JobProgressEvent & { filteredOutput: any })[];
}

export const StreamedAnalysisOutput = ({ events }: StreamedAnalysisOutputProps) => {
  return (
    <div>
      {events.map((e) => {
        const output = e.filteredOutput;

        if (output.scraped_text) {
          return (
            <Section key="scraped_text" title="Scraped Text">
              <div className="max-h-48 overflow-auto text-sm whitespace-pre-wrap text-gray-800">
                {output.scraped_text}
              </div>
            </Section>
          );
        }

        if (e.node === 'gcs_data' && output.gcs_snippets?.length) {
          return (
            <Section key="gcs_data" title="Snippets">
              <ul className="ml-5 max-h-40 list-disc overflow-y-auto text-sm text-gray-800">
                {output.gcs_snippets.map((snippet: string, i: number) => (
                  <li key={i} className="mb-1">
                    {snippet}
                  </li>
                ))}
              </ul>
            </Section>
          );
        }

        if (e.node === 'run_sentiment_analysis' && output.sentiment_analysis) {
          const sentiment = output.sentiment_analysis;
          return (
            <Section key="sentiment_analysis" title="Sentiment Analysis">
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
            </Section>
          );
        }

        if (e.node === 'analyze' && output.result) {
          return (
            <Section key="analyze" title="Streamed LLM Output">
              {output.result.prediction && (
                <div className="px-2 pt-2 pb-1 text-sm text-gray-800">
                  <ForecastChart
                    prediction={output.result.prediction}
                    className="bg-white p-2 sm:p-3 md:p-4"
                  />
                </div>
              )}
              {output.result.prediction && output.result.insights && (
                <hr className="my-2 border-gray-100" />
              )}
              {output.result.insights && (
                <div className="mx-2 mb-2 rounded-xl bg-white p-2 text-sm text-gray-800 sm:p-3 md:p-4">
                  <Markdown result={output.result.insights} />
                </div>
              )}
            </Section>
          );
        }

        return null;
      })}
    </div>
  );
};

const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <div className="mt-4 mb-4 rounded border border-gray-200 bg-white px-5 py-4 shadow-sm">
    <h4 className="mb-2 font-semibold">{title}</h4>
    {children}
  </div>
);
