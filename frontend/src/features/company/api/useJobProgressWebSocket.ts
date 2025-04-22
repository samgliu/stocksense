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
  const [progress, setProgress] = useState<JobProgressEvent[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!jobId) return;
    const ws = new WebSocket(
      `${import.meta.env.VITE_BACKEND_WS_URL}/api/v1/ws/job-progress/${jobId}`,
    );
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data: JobProgressEvent = JSON.parse(event.data);
        if (data.job_id !== jobId) return;
        setProgress((prev) => [...prev, data]);
      } catch (e) {
        console.error('Failed to parse WebSocket message', e);
      }
    };
    ws.onclose = () => {
      wsRef.current = null;
    };
    return () => {
      ws.close();
    };
  }, [jobId]);

  return progress;
}
