import { useEffect, useMemo, useState } from 'react';
import { useJobProgressWebSocket } from './useJobProgressWebSocket';

import type { JobProgressEvent } from './useJobProgressWebSocket';

export function useStreamingAnalysis(streamJobId?: string, showStreamModal?: boolean) {
  const [progressEvents, setProgressEvents] = useState<JobProgressEvent[]>([]);

  const rawEvents = useJobProgressWebSocket(
    showStreamModal && streamJobId ? streamJobId : undefined,
  );

  // Reset events completely when a new job ID starts
  useEffect(() => {
    setProgressEvents([]);
  }, [streamJobId]);

  // Add new events
  useEffect(() => {
    if (rawEvents.length > 0) {
      setProgressEvents((prev) => {
        const seen = new Set(prev.map((e) => e.timestamp));
        const newEvents = rawEvents.filter((e) => !seen.has(e.timestamp));
        return [...prev, ...newEvents];
      });
    }
  }, [rawEvents]);

  const filteredProgressEvents = useMemo(
    () =>
      progressEvents.map((event) => ({
        ...event,
        filteredOutput: extractRelevantOutput(event),
      })),
    [progressEvents],
  );

  const dedupedProgressEvents = useMemo(() => {
    const map = new Map<string, JobProgressEvent & { filteredOutput: any }>();
    for (const event of filteredProgressEvents) {
      map.set(event.node, event);
    }
    return Array.from(map.values());
  }, [filteredProgressEvents]);

  const isFinal = dedupedProgressEvents.some((e) => e.is_final);

  return { dedupedProgressEvents, isFinal };
}

function extractRelevantOutput(event: any) {
  switch (event.node) {
    case 'scrape_domain':
      return { scraped_text: event.output?.scraped_text ?? null };
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
          // keep as string if parsing fails
        }
      }
      return { result };
    }
    default:
      return {};
  }
}
