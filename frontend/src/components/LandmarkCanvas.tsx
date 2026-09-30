import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Camera, CameraOff, RefreshCw, Eye, EyeOff, AlertCircle, FlipHorizontal } from 'lucide-react';
import { LandmarkPoint, DualHandData } from '../types';

interface LandmarkCanvasProps {
  onLandmarksDetected?: (landmarks: LandmarkPoint[]) => void;
  onDualHandsDetected?: (data: DualHandData) => void;
  isActive: boolean;
  mirrored?: boolean;
  onToggleMirrored?: () => void;
  onToggleActive?: () => void;
}

// Connections between 21 MediaPipe hand landmarks
const HAND_CONNECTIONS = [
  // Thumb
  [0, 1], [1, 2], [2, 3], [3, 4],
  // Index
  [0, 5], [5, 6], [6, 7], [7, 8],
  // Middle
  [0, 9], [9, 10], [10, 11], [11, 12],
  // Ring
  [0, 13], [13, 14], [14, 15], [15, 16],
  // Pinky
  [0, 17], [17, 18], [18, 19], [19, 20],
  // Palm Base
  [5, 9], [9, 13], [13, 17]
];

export const LandmarkCanvas: React.FC<LandmarkCanvasProps> = ({
  onLandmarksDetected,
  onDualHandsDetected,
  isActive,
  mirrored = true,
  onToggleMirrored,
  onToggleActive,
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [showLandmarks, setShowLandmarks] = useState(true);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [streamStarted, setStreamStarted] = useState(false);
  const [detectedHandsCount, setDetectedHandsCount] = useState<number>(0);
  const [handLabels, setHandLabels] = useState<string[]>([]);
  const handsInstanceRef = useRef<any>(null);
  const cameraInstanceRef = useRef<any>(null);
  const animFrameIdRef = useRef<number | null>(null);

  // Initialize camera and MediaPipe
  const startCamera = useCallback(async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play();
          setStreamStarted(true);
        };
      }

      // Initialize MediaPipe Hands if available in window
      const HandsClass = (window as any).Hands;
      const CameraClass = (window as any).Camera;

      if (HandsClass && videoRef.current) {
        const hands = new HandsClass({
          locateFile: (file: string) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
        });

        hands.setOptions({
          maxNumHands: 2,
          modelComplexity: 1,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        hands.onResults((results: any) => {
          drawResults(results);
        });

        handsInstanceRef.current = hands;

        if (CameraClass) {
          const cam = new CameraClass(videoRef.current, {
            onFrame: async () => {
              if (handsInstanceRef.current && videoRef.current && isActive) {
                await handsInstanceRef.current.send({ image: videoRef.current });
              }
            },
            width: 640,
            height: 480,
          });
          cam.start();
          cameraInstanceRef.current = cam;
        }
      } else {
        // Fallback animation loop for drawing/mocking
        runFallbackLoop();
      }
    } catch (err: any) {
      console.warn('Camera stream error:', err);
      setCameraError('Camera access denied or unavailable. Please grant camera permission.');
      runFallbackLoop();
    }
  }, [isActive]);

  const stopCamera = useCallback(() => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    if (cameraInstanceRef.current) {
      try { cameraInstanceRef.current.stop(); } catch {}
    }
    if (animFrameIdRef.current) {
      cancelAnimationFrame(animFrameIdRef.current);
    }
    setStreamStarted(false);
    setDetectedHandsCount(0);
    setHandLabels([]);
  }, []);

  const drawResults = (results: any) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;

    ctx.save();
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      const rawCount = results.multiHandLandmarks.length;
      setDetectedHandsCount(rawCount);

      let leftHand: LandmarkPoint[] | null = null;
      let rightHand: LandmarkPoint[] | null = null;
      const detectedLabels: string[] = [];

      for (let i = 0; i < rawCount; i++) {
        const rawLms = results.multiHandLandmarks[i];
        const handednessObj = results.multiHandedness && results.multiHandedness[i];
        const mpLabel = handednessObj?.label || (i === 0 ? 'Right' : 'Left');

        const formatted: LandmarkPoint[] = rawLms.map((lm: any) => ({
          x: lm.x,
          y: lm.y,
          z: lm.z || 0.0,
        }));

        // In mirrored camera: MediaPipe 'Right' corresponds to physical Left Hand
        let isLeft = mirrored ? mpLabel === 'Right' : mpLabel === 'Left';

        // Disambiguate if MediaPipe labeled both hands the same
        if (isLeft && leftHand && !rightHand) {
          isLeft = false;
        } else if (!isLeft && rightHand && !leftHand) {
          isLeft = true;
        }

        if (isLeft) {
          leftHand = formatted;
          detectedLabels.push('Left Hand');
        } else {
          rightHand = formatted;
          detectedLabels.push('Right Hand');
        }
      }

      setHandLabels(detectedLabels);

      // Emit dual-hand data to parent
      if (onDualHandsDetected) {
        onDualHandsDetected({
          left_hand: leftHand,
          right_hand: rightHand,
          num_hands: (leftHand ? 1 : 0) + (rightHand ? 1 : 0)
        });
      }

      // Backward compatibility for single hand listener
      if (onLandmarksDetected) {
        onLandmarksDetected(rightHand || leftHand || []);
      }

      if (showLandmarks) {
        // Draw Left Hand (Cyan #06b6d4)
        if (leftHand) {
          drawHand(ctx, leftHand, canvas.width, canvas.height, '#06b6d4', '#22d3ee', 'Left Hand', mirrored);
        }

        // Draw Right Hand (Purple #a855f7)
        if (rightHand) {
          drawHand(ctx, rightHand, canvas.width, canvas.height, '#a855f7', '#c084fc', 'Right Hand', mirrored);
        }

        // If both hands detected, draw inter-hand interaction bridge line between wrists
        if (leftHand && rightHand) {
          const lw = leftHand[0];
          const rw = rightHand[0];
          const lx = (mirrored ? (1 - lw.x) : lw.x) * canvas.width;
          const ly = lw.y * canvas.height;
          const rx = (mirrored ? (1 - rw.x) : rw.x) * canvas.width;
          const ry = rw.y * canvas.height;

          ctx.beginPath();
          ctx.setLineDash([4, 4]);
          ctx.strokeStyle = '#f59e0b'; // Amber interaction bridge
          ctx.lineWidth = 2;
          ctx.moveTo(lx, ly);
          ctx.lineTo(rx, ry);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      }
    } else {
      setDetectedHandsCount(0);
      setHandLabels([]);
      if (onDualHandsDetected) {
        onDualHandsDetected({ left_hand: null, right_hand: null, num_hands: 0 });
      }
      if (onLandmarksDetected) {
        onLandmarksDetected([]);
      }
    }

    ctx.restore();
  };

  const drawHand = (
    ctx: CanvasRenderingContext2D,
    landmarks: LandmarkPoint[],
    width: number,
    height: number,
    strokeColor: string,
    jointColor: string,
    label: string,
    isMirrored: boolean
  ) => {
    // 1. Draw connections
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = 3;
    for (const [startIdx, endIdx] of HAND_CONNECTIONS) {
      const p1 = landmarks[startIdx];
      const p2 = landmarks[endIdx];
      if (p1 && p2) {
        const x1 = (isMirrored ? (1 - p1.x) : p1.x) * width;
        const y1 = p1.y * height;
        const x2 = (isMirrored ? (1 - p2.x) : p2.x) * width;
        const y2 = p2.y * height;

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      }
    }

    // 2. Draw landmarks joints
    for (let i = 0; i < landmarks.length; i++) {
      const lm = landmarks[i];
      const x = (isMirrored ? (1 - lm.x) : lm.x) * width;
      const y = lm.y * height;

      ctx.beginPath();
      ctx.arc(x, y, i % 4 === 0 ? 5 : 3.5, 0, 2 * Math.PI);
      ctx.fillStyle = jointColor;
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    // 3. Draw Hand Label near wrist
    const wrist = landmarks[0];
    const wx = (isMirrored ? (1 - wrist.x) : wrist.x) * width;
    const wy = wrist.y * height;
    ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
    ctx.fillRect(wx - 35, wy + 8, 70, 20);
    ctx.fillStyle = jointColor;
    ctx.font = 'bold 10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(label, wx, wy + 22);
  };

  // Fallback demo simulator when camera or WebGL MediaPipe isn't responding
  const runFallbackLoop = () => {
    let t = 0;
    const loop = () => {
      if (!isActive) return;
      t += 0.04;
      const canvas = canvasRef.current;
      if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) {
          canvas.width = canvas.clientWidth;
          canvas.height = canvas.clientHeight;
          ctx.clearRect(0, 0, canvas.width, canvas.height);

          // Simulated Right Hand (waving)
          const simRight: LandmarkPoint[] = [];
          const cx = 0.55 + Math.sin(t) * 0.06;
          const cy = 0.60;
          simRight.push({ x: cx, y: cy, z: 0.0 });
          for (let f = 0; f < 5; f++) {
            const bx = cx - 0.06 + f * 0.03;
            simRight.push({ x: bx, y: cy - 0.08, z: 0.0 });
            simRight.push({ x: bx, y: cy - 0.15, z: 0.0 });
            simRight.push({ x: bx, y: cy - 0.22, z: 0.0 });
            simRight.push({ x: bx + Math.sin(t * 2 + f) * 0.015, y: cy - 0.28, z: 0.0 });
          }

          // Simulated Left Hand (Namaste interaction)
          const simLeft: LandmarkPoint[] = [];
          const lx = 0.45 - Math.sin(t) * 0.06;
          const ly = 0.60;
          simLeft.push({ x: lx, y: ly, z: 0.0 });
          for (let f = 0; f < 5; f++) {
            const bx = lx + 0.06 - f * 0.03;
            simLeft.push({ x: bx, y: ly - 0.08, z: 0.0 });
            simLeft.push({ x: bx, y: ly - 0.15, z: 0.0 });
            simLeft.push({ x: bx, y: ly - 0.22, z: 0.0 });
            simLeft.push({ x: bx - Math.sin(t * 2 + f) * 0.015, y: ly - 0.28, z: 0.0 });
          }

          setDetectedHandsCount(2);
          setHandLabels(['Left Hand', 'Right Hand']);

          if (onDualHandsDetected) {
            onDualHandsDetected({
              left_hand: simLeft,
              right_hand: simRight,
              num_hands: 2
            });
          }
          if (onLandmarksDetected) {
            onLandmarksDetected(simRight);
          }

          if (showLandmarks) {
            drawHand(ctx, simLeft, canvas.width, canvas.height, '#06b6d4', '#22d3ee', 'Left Hand', mirrored);
            drawHand(ctx, simRight, canvas.width, canvas.height, '#a855f7', '#c084fc', 'Right Hand', mirrored);
          }
        }
      }
      animFrameIdRef.current = requestAnimationFrame(loop);
    };
    animFrameIdRef.current = requestAnimationFrame(loop);
  };

  useEffect(() => {
    if (isActive) {
      startCamera();
    } else {
      stopCamera();
    }
    return () => {
      stopCamera();
    };
  }, [isActive, startCamera, stopCamera]);

  return (
    <div className="relative w-full aspect-video bg-slate-950 rounded-2xl overflow-hidden shadow-lg border border-slate-800">
      {/* Video Feed */}
      <video
        ref={videoRef}
        className={`w-full h-full object-cover ${mirrored ? 'transform -scale-x-100' : ''}`}
        playsInline
        muted
      />

      {/* Landmark Overlay Canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none"
      />

      {/* Overlay Status Badges */}
      <div className="absolute top-3 left-3 flex flex-wrap items-center gap-2">
        <div className={`px-2.5 py-1 rounded-full text-xs font-semibold backdrop-blur-md flex items-center gap-1.5 ${
          detectedHandsCount > 0 ? 'bg-emerald-500/80 text-white' : 'bg-slate-800/80 text-slate-300'
        }`}>
          <span className={`w-2 h-2 rounded-full ${detectedHandsCount > 0 ? 'bg-white animate-pulse' : 'bg-slate-400'}`} />
          {detectedHandsCount === 2
            ? 'Dual Hands Active (ISL 2-Hand Ready)'
            : detectedHandsCount === 1
            ? `1 Hand Active (${handLabels.join(', ') || 'Tracked'})`
            : 'Searching for Hands...'}
        </div>

        {detectedHandsCount > 0 && (
          <div className="hidden sm:flex items-center gap-1.5 text-[11px] font-medium text-white px-2 py-0.5 rounded-md bg-slate-900/80 border border-slate-700/60">
            <span className="w-2 h-2 rounded-full bg-cyan-400" /> Left
            <span className="w-2 h-2 rounded-full bg-purple-400 ml-1.5" /> Right
          </div>
        )}
      </div>

      {/* Controls Overlay */}
      <div className="absolute bottom-3 right-3 flex items-center space-x-2">
        {onToggleMirrored && (
          <button
            onClick={onToggleMirrored}
            title={mirrored ? 'Camera Mirrored (Selfie)' : 'Camera Normal'}
            className={`p-2 rounded-xl backdrop-blur-md transition-colors border ${
              mirrored ? 'bg-slate-900/80 text-teal-400 border-slate-700/50' : 'bg-slate-800/80 text-slate-400 border-slate-700/50'
            }`}
          >
            <FlipHorizontal className="w-4 h-4" />
          </button>
        )}
        <button
          onClick={() => setShowLandmarks(!showLandmarks)}
          title={showLandmarks ? 'Hide Landmarks' : 'Show Landmarks'}
          className="p-2 rounded-xl bg-slate-900/80 backdrop-blur-md text-white hover:bg-slate-800 transition-colors border border-slate-700/50"
        >
          {showLandmarks ? <Eye className="w-4 h-4 text-teal-400" /> : <EyeOff className="w-4 h-4 text-slate-400" />}
        </button>
        {onToggleActive && (
          <button
            onClick={onToggleActive}
            className={`px-3 py-1.5 rounded-xl font-medium text-xs backdrop-blur-md flex items-center gap-1.5 transition-colors border ${
              isActive
                ? 'bg-rose-500/80 text-white border-rose-400/50 hover:bg-rose-600'
                : 'bg-emerald-500/80 text-white border-emerald-400/50 hover:bg-emerald-600'
            }`}
          >
            {isActive ? <CameraOff className="w-3.5 h-3.5" /> : <Camera className="w-3.5 h-3.5" />}
            {isActive ? 'Pause' : 'Start Camera'}
          </button>
        )}
      </div>

      {cameraError && (
        <div className="absolute inset-0 bg-slate-950/90 backdrop-blur-sm flex flex-col items-center justify-center p-6 text-center">
          <AlertCircle className="w-10 h-10 text-amber-400 mb-3" />
          <h4 className="text-white font-bold text-base mb-1">Camera Stream Notice</h4>
          <p className="text-slate-400 text-xs max-w-sm mb-4">{cameraError}</p>
          <button
            onClick={startCamera}
            className="px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-xl text-xs font-semibold flex items-center gap-2 shadow-sm"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry Camera Access
          </button>
        </div>
      )}
    </div>
  );
};
