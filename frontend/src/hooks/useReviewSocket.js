import { useState, useEffect, useRef, useCallback } from 'react';

const WS_BASE = 'ws://localhost:8000';

export default function useReviewSocket(reviewId) {
  const [state, setState] = useState(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const retriesRef = useRef(0);

  const connect = useCallback(() => {
    if (!reviewId) return;

    const ws = new WebSocket(`${WS_BASE}/ws/reviews/${reviewId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      retriesRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setState(data);
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = (event) => {
      setConnected(false);
      wsRef.current = null;

      if (state?.status === 'completed' || state?.status === 'failed') return;

      if (retriesRef.current < 5) {
        retriesRef.current += 1;
        const delay = Math.min(1000 * Math.pow(2, retriesRef.current), 10000);
        setTimeout(connect, delay);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [reviewId]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  return { state, connected };
}
