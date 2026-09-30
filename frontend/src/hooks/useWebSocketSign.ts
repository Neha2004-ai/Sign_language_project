import { useState, useEffect, useRef, useCallback } from 'react';
import { PredictionResult, LandmarkPoint, DualHandData } from '../types';

export const useWebSocketSign = (enabled = true) => {
  const [isConnected, setIsConnected] = useState(false);
  const [latestPrediction, setLatestPrediction] = useState<PredictionResult | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!enabled) return;
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/sign-recognition`;

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data: PredictionResult = JSON.parse(event.data);
          setLatestPrediction(data);
        } catch (err) {
          console.error('Failed to parse WS payload:', err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        if (enabled) {
          setTimeout(connect, 2000);
        }
      };

      ws.onerror = () => {
        setIsConnected(false);
      };

      socketRef.current = ws;
    } catch (err) {
      console.warn('WebSocket connection error:', err);
      setIsConnected(false);
    }
  }, [enabled]);

  useEffect(() => {
    connect();
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [connect]);

  const sendLandmarks = useCallback((landmarks: LandmarkPoint[], userId?: number) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        landmarks,
        user_id: userId,
        use_custom_gestures: true,
      }));
    }
  }, []);

  const sendDualHands = useCallback((data: DualHandData, mirrored: boolean = true, userId?: number) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        left_landmarks: data.left_hand,
        right_landmarks: data.right_hand,
        mirrored_camera: mirrored,
        user_id: userId,
        use_custom_gestures: true,
      }));
    }
  }, []);

  return {
    isConnected,
    latestPrediction,
    sendLandmarks,
    sendDualHands,
  };
};
