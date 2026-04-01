"use client";

import { useEffect, useRef, useState, useCallback } from "react";

export type WsAlert = {
  id: number;
  type: string;
  item_id: number;
  name: string;
  sku?: string;
  quantity?: number;
  quantity_before?: number;
  quantity_after?: number;
  threshold?: number;
  location?: string;
  notes?: string;
  timestamp: number;
};

let alertIdCounter = 0;

export function useWebSocket() {
  const [alerts, setAlerts] = useState<WsAlert[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const dismissAlert = useCallback((id: number) => {
    setAlerts((prev) => prev.filter((a) => a.id !== id));
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const wsUrl = apiUrl.replace(/^http/, "ws") + "/api/v1/ws/inventory";

    let reconnectTimer: ReturnType<typeof setTimeout>;
    let ws: WebSocket;

    const connect = () => {
      ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (["low_stock_alert", "item_restocked", "item_withdrawn"].includes(data.type)) {
            const alert: WsAlert = {
              ...data,
              id: ++alertIdCounter,
              timestamp: Date.now(),
            };
            setAlerts((prev) => [alert, ...prev]);
          }
        } catch {
          // ignore non-JSON messages
        }
      };

      ws.onclose = () => {
        reconnectTimer = setTimeout(connect, 5000);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
      }
    };
  }, []);

  return { alerts, dismissAlert };
}
