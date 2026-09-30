import time
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.ml.inference import inference_engine

router = APIRouter()

@router.websocket("/ws/sign-recognition")
async def websocket_sign_recognition(websocket: WebSocket):
    await websocket.accept()
    last_frame_time = time.time()
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            left_landmarks = payload.get("left_landmarks")
            right_landmarks = payload.get("right_landmarks")
            landmarks = payload.get("landmarks", [])
            handedness = payload.get("handedness", "Right")
            mirrored_camera = payload.get("mirrored_camera", True)
            user_id = payload.get("user_id")
            use_custom = payload.get("use_custom_gestures", True)
            
            # Compute FPS
            now = time.time()
            dt = now - last_frame_time
            fps = round(1.0 / dt, 1) if dt > 0 else 30.0
            last_frame_time = now
            
            # Perform real-time dual-hand inference
            result = inference_engine.process_frame(
                left_landmarks=left_landmarks,
                right_landmarks=right_landmarks,
                landmarks=landmarks,
                handedness=handedness,
                mirrored_camera=mirrored_camera,
                user_id=user_id,
                use_custom_gestures=use_custom
            )
            result["fps"] = fps
            result["timestamp"] = now
            
            await websocket.send_json(result)
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"status": "error", "message": str(e)})
        except Exception:
            pass
