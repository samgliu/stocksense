import { useEffect, useRef, useState } from 'react';

export interface JobProgressEvent {
  job_id: string;
  node: string;
  output: any;
  state: any;
  timestamp: string;
  is_final: boolean;
}

export function useJobProgressWebSocket(jobId: string | undefined) {
  const [events, setEvents] = useState<JobProgressEvent[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!jobId) return;

    setEvents([]); // Reset state when jobId changes

    const ws = new WebSocket(
      `${import.meta.env.VITE_BACKEND_WS_URL}/api/v1/ws/job-progress/${jobId}`,
    );
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data: JobProgressEvent = JSON.parse(event.data);
        if (data.job_id === jobId) {
          setEvents((prev) => [...prev, data]);
        }
      } catch (e) {
        console.error('WebSocket parse error', e);
      }
    };

    ws.onerror = (e) => console.error('WebSocket error', e);

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [jobId]);

  return events;
}
