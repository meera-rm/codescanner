import { useEffect, useRef, useState, useCallback } from 'react';

interface WebSocketMessage {
  type: 'connected' | 'scan_complete' | 'dashboard_refresh' | 'scan_progress' | 'alert' | 'heartbeat' | 'echo';
  timestamp?: string;
  data?: any;
  [key: string]: any;
}

interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  maxReconnectDelay?: number;
}

export const useWebSocket = ({
  url,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
  autoReconnect = true,
  maxReconnectDelay = 30000,
}: UseWebSocketOptions) => {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const messageQueueRef = useRef<string[]>([]);
  const reconnectCountRef = useRef(0);
  const isMountedRef = useRef(true);
  const callbacksRef = useRef({ onMessage, onConnect, onDisconnect, onError });

  // Update callbacks without causing reconnection
  useEffect(() => {
    callbacksRef.current = { onMessage, onConnect, onDisconnect, onError };
  }, [onMessage, onConnect, onDisconnect, onError]);

  const connect = useCallback(() => {
    // Don't connect if component unmounted
    if (!isMountedRef.current) return;

    try {
      // Convert http to ws
      const wsUrl = url.replace('http://', 'ws://').replace('https://', 'wss://');
      const ws = new WebSocket(wsUrl);

      // Set a connection timeout
      const connectionTimeout = setTimeout(() => {
        if (ws.readyState === WebSocket.CONNECTING) {
          console.warn('WebSocket connection timeout');
          ws.close();
        }
      }, 5000);

      ws.onopen = () => {
        clearTimeout(connectionTimeout);
        if (!isMountedRef.current) return;

        console.log('✓ WebSocket connected:', wsUrl);
        reconnectCountRef.current = 0; // Reset reconnect counter on successful connection
        setIsConnected(true);
        callbacksRef.current.onConnect?.();

        // Flush message queue
        while (messageQueueRef.current.length > 0) {
          const msg = messageQueueRef.current.shift();
          if (msg && ws.readyState === WebSocket.OPEN) {
            ws.send(msg);
          }
        }
      };

      ws.onmessage = (event) => {
        if (!isMountedRef.current) return;
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          callbacksRef.current.onMessage?.(message);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onerror = (error) => {
        if (!isMountedRef.current) return;
        console.warn('WebSocket error:', error);
        callbacksRef.current.onError?.(error);
      };

      ws.onclose = () => {
        clearTimeout(connectionTimeout);
        if (!isMountedRef.current) return;

        console.log('WebSocket disconnected');
        setIsConnected(false);
        callbacksRef.current.onDisconnect?.();

        // Auto-reconnect with exponential backoff
        if (autoReconnect) {
          const delay = Math.min(
            1000 * Math.pow(2, reconnectCountRef.current),
            maxReconnectDelay
          );
          reconnectCountRef.current += 1;
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectCountRef.current})...`);

          reconnectTimeoutRef.current = setTimeout(() => {
            if (isMountedRef.current) {
              connect();
            }
          }, delay);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      if (autoReconnect && isMountedRef.current) {
        const delay = Math.min(
          1000 * Math.pow(2, reconnectCountRef.current),
          maxReconnectDelay
        );
        reconnectCountRef.current += 1;

        reconnectTimeoutRef.current = setTimeout(() => {
          if (isMountedRef.current) {
            connect();
          }
        }, delay);
      }
    }
  }, [url, autoReconnect, maxReconnectDelay]);

  const send = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      // Queue message if not connected
      messageQueueRef.current.push(JSON.stringify(message));
    }
  }, []);

  const disconnect = useCallback(() => {
    isMountedRef.current = false;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  useEffect(() => {
    isMountedRef.current = true;
    reconnectCountRef.current = 0;
    connect();

    return () => {
      disconnect();
    };
  }, [connect]);

  return {
    isConnected,
    send,
    disconnect,
  };
};

export default useWebSocket;
