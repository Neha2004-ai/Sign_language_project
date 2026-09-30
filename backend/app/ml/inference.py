import os
import math
import time
from collections import deque
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn

from app.ml.feature_extractor import LandmarkFeatureExtractor
from app.ml.isl_vocabulary import ISL_VOCABULARY, UNKNOWN_SIGN, NO_HAND_SIGN, CONFIDENCE_THRESHOLD
from app.core.config import settings

class DynamicGestureLSTM(nn.Module):
    """Bidirectional LSTM neural network matching saved checkpoint architecture."""
    def __init__(self, input_dim=206, hidden_dim=64, num_classes=13, num_layers=2):
        super(DynamicGestureLSTM, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True
        )
        self.fc1 = nn.Linear(hidden_dim * 2, 64)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(64, num_classes)
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_out = lstm_out[:, -1, :]
        out = self.fc1(last_out)
        out = self.relu(out)
        out = self.dropout(out)
        logits = self.fc2(out)
        return logits

class CustomGestureMatcher:
    """Matches user-trained custom gesture landmark templates."""
    def __init__(self):
        self.user_templates: Dict[int, List[Dict[str, Any]]] = {}

    def register_user_gesture(self, user_id: int, gesture_name: str, sample_vectors: List[np.ndarray]):
        if user_id not in self.user_templates:
            self.user_templates[user_id] = []
        mean_vector = np.mean(sample_vectors, axis=0)
        self.user_templates[user_id].append({
            "name": gesture_name,
            "vector": mean_vector,
            "samples_count": len(sample_vectors)
        })

    def match(self, user_id: int, current_feature_vector: np.ndarray, threshold: float = 0.82) -> Optional[Tuple[str, float]]:
        if user_id not in self.user_templates or not self.user_templates[user_id]:
            return None
        best_name = None
        best_sim = -1.0
        for template in self.user_templates[user_id]:
            vec = template["vector"]
            min_len = min(len(current_feature_vector), len(vec))
            v1 = current_feature_vector[:min_len]
            v2 = vec[:min_len]
            dot = np.dot(v1, v2)
            norm_a = np.linalg.norm(v1)
            norm_b = np.linalg.norm(v2)
            if norm_a * norm_b > 1e-6:
                sim = dot / (norm_a * norm_b)
                if sim > best_sim:
                    best_sim = sim
                    best_name = template["name"]
        if best_sim >= threshold and best_name:
            return best_name, float(best_sim)
        return None

class GeometricRuleDetector:
    """
    Precision Geometric Rule Analyzer for Indian Sign Language (ISL).
    Evaluates:
    - Hand shapes (finger extensions, curling, angles, pinches)
    - Single-hand ISL signs (HELLO, YES, NO, THANK YOU, SORRY, PLEASE, WATER, 1-5, I LOVE YOU, OK)
    - Dual-hand ISL signs (NAMASTE, HELP, BOOK, HOUSE, TIME, STOP, WORK, PEACE)
    - Distinguishes valid ISL signs from unrecognized random gestures.
    """

    @staticmethod
    def dist(p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

    @classmethod
    def analyze_hand_posture(cls, landmarks: Optional[List[Dict[str, float]]]) -> Optional[Dict[str, Any]]:
        if not landmarks or len(landmarks) < 21:
            return None
            
        pts = [(lm.get('x', 0.0), lm.get('y', 0.0), lm.get('z', 0.0)) for lm in landmarks[:21]]
        wrist = pts[0]
        
        # Extension: distance from tip to wrist vs PIP to wrist
        index_ext = cls.dist(pts[8], wrist) > cls.dist(pts[6], wrist) * 1.15
        middle_ext = cls.dist(pts[12], wrist) > cls.dist(pts[10], wrist) * 1.15
        ring_ext = cls.dist(pts[16], wrist) > cls.dist(pts[14], wrist) * 1.15
        pinky_ext = cls.dist(pts[20], wrist) > cls.dist(pts[18], wrist) * 1.15
        thumb_ext = cls.dist(pts[4], pts[17]) > cls.dist(pts[2], pts[17]) * 1.10
        
        # Distances
        thumb_index_dist = cls.dist(pts[4], pts[8])
        thumb_middle_dist = cls.dist(pts[4], pts[12])
        index_middle_dist = cls.dist(pts[8], pts[12])
        
        pointing_up = pts[8][1] < wrist[1] - 0.08
        pointing_down = pts[8][1] > wrist[1] + 0.08
        
        return {
            "thumb": thumb_ext,
            "index": index_ext,
            "middle": middle_ext,
            "ring": ring_ext,
            "pinky": pinky_ext,
            "thumb_index_dist": thumb_index_dist,
            "thumb_middle_dist": thumb_middle_dist,
            "index_middle_dist": index_middle_dist,
            "pointing_up": pointing_up,
            "pointing_down": pointing_down,
            "wrist": wrist,
            "pts": pts,
            "extended_count": sum([thumb_ext, index_ext, middle_ext, ring_ext, pinky_ext])
        }

    @classmethod
    def classify_single_hand(cls, p: Dict[str, Any]) -> Tuple[str, float]:
        t, i, m, r, pk = p["thumb"], p["index"], p["middle"], p["ring"], p["pinky"]
        count = p["extended_count"]
        ti_dist = p["thumb_index_dist"]
        
        # 1. HELLO / OPEN PALM (all 5 extended)
        if count == 5 and p["pointing_up"]:
            return "HELLO", 0.94
        # 2. I LOVE YOU (thumb, index, pinky extended)
        elif t and i and not m and not r and pk:
            return "I LOVE YOU", 0.96
        # 3. YES (fist nodding or thumb up)
        elif count == 0 or (count == 1 and t and not i):
            return "YES", 0.92
        # 4. Numbers 1 to 5 (precise finger check)
        elif count == 1 and i:
            return "1", 0.95
        elif count == 2 and i and m and not r and not pk:
            return "2", 0.93
        elif count == 3 and t and i and m and not r and not pk:
            return "3", 0.92
        elif count == 4 and not t and i and m and r and pk:
            return "4", 0.94
        elif count == 5:
            return "5", 0.92
        # 5. NO (index & middle extended, snapping or wagging)
        elif not t and i and m and not r and not pk:
            return "NO", 0.91
        # 6. THANK YOU / FLAT HAND (all 4 fingers extended, thumb curled across)
        elif not t and i and m and r and pk:
            return "THANK YOU", 0.92
        # 7. OK (pinch thumb & index, 3 fingers extended)
        elif ti_dist < 0.08 and m and r and pk:
            return "OK", 0.94
        # 8. PLEASE / FLAT PALM
        elif not t and i and m and r and not pk:
            return "PLEASE", 0.88
        # 9. SORRY (A-fist)
        elif t and not i and not m and not r and not pk:
            return "SORRY", 0.88
        # 10. WATER (W-hand / 3 fingers or thumb near mouth)
        elif i and m and r and not pk:
            return "WATER", 0.85
            
        return "UNKNOWN_GESTURE", 0.35

    @classmethod
    def classify_dual_hands(cls, lp: Dict[str, Any], rp: Dict[str, Any]) -> Tuple[str, float]:
        lw, rw = lp["wrist"], rp["wrist"]
        wrist_dist = cls.dist(lw, rw)
        
        l_pts, r_pts = lp["pts"], rp["pts"]
        l_tips = [l_pts[t] for t in [4, 8, 12, 16, 20]]
        r_tips = [r_pts[t] for t in [4, 8, 12, 16, 20]]
        tip_dists = [cls.dist(l_tips[idx], r_tips[idx]) for idx in range(5)]
        avg_tip_dist = sum(tip_dists) / 5.0
        
        # Cross distance: Right index tip to Left wrist & Left index tip to Right wrist
        r_index_to_l_wrist = cls.dist(r_pts[8], lw)
        l_index_to_r_wrist = cls.dist(l_pts[8], rw)
        
        # 1. TIME: One index finger touching/tapping opposite wrist
        if (r_index_to_l_wrist < 0.16) or (l_index_to_r_wrist < 0.16):
            return "TIME", 0.95

        # 2. HOUSE: Fingertips touching at roof apex, wrists wider apart
        index_tip_dist = cls.dist(l_pts[8], r_pts[8])
        if index_tip_dist < 0.12 and wrist_dist > 0.14 and lp["pointing_up"] and rp["pointing_up"] and wrist_dist > index_tip_dist * 1.3:
            return "HOUSE", 0.95
            
        # 3. NAMASTE (Anjali Mudra): Palms facing each other, wrists and fingertips touching, pointing up
        if lp["extended_count"] >= 4 and rp["extended_count"] >= 4:
            if wrist_dist < 0.18 and avg_tip_dist < 0.15 and lp["pointing_up"] and rp["pointing_up"]:
                return "NAMASTE", 0.96
                
        # 4. BOOK: Both hands flat, pinky edges together
        if lp["extended_count"] >= 4 and rp["extended_count"] >= 4:
            pinky_dist = cls.dist(l_pts[20], r_pts[20])
            if pinky_dist < 0.15 and wrist_dist < 0.25:
                return "BOOK", 0.93

        # 5. HELP: One flat base hand and other hand is a fist/thumb placed on top
        is_l_base = lp["extended_count"] >= 4
        is_r_base = rp["extended_count"] >= 4
        is_l_fist = lp["extended_count"] <= 1
        is_r_fist = rp["extended_count"] <= 1
        
        if (is_l_base and is_r_fist) or (is_r_base and is_l_fist):
            if wrist_dist < 0.28:
                return "HELP", 0.95
                
        # 6. STOP: Flat palm with perpendicular open hand descending
        if (is_l_base and rp["extended_count"] >= 4 and wrist_dist < 0.25) or \
           (is_r_base and lp["extended_count"] >= 4 and wrist_dist < 0.25):
            return "STOP", 0.93
            
        # 7. WORK: Both hands in fists, wrists touching or tapping
        if is_l_fist and is_r_fist and wrist_dist < 0.22:
            return "WORK", 0.92
            
        # 8. PEACE: Both hands showing V-sign
        if lp["index"] and lp["middle"] and not lp["ring"] and not lp["pinky"] and \
           rp["index"] and rp["middle"] and not rp["ring"] and not rp["pinky"]:
            return "PEACE", 0.93
            
        return "UNKNOWN_GESTURE", 0.40

    @classmethod
    def classify(
        cls,
        left_landmarks: Optional[List[Dict[str, float]]],
        right_landmarks: Optional[List[Dict[str, float]]]
    ) -> Tuple[str, float]:
        lp = cls.analyze_hand_posture(left_landmarks)
        rp = cls.analyze_hand_posture(right_landmarks)
        
        if lp is not None and rp is not None:
            return cls.classify_dual_hands(lp, rp)
        elif rp is not None:
            return cls.classify_single_hand(rp)
        elif lp is not None:
            return cls.classify_single_hand(lp)
        else:
            return "NO_HAND", 0.0

class SignStateMachine:
    """Debouncing and Sign Transition State Machine."""
    IDLE = "IDLE"
    SIGN_DETECTED = "SIGN_DETECTED"
    CONFIRMING = "CONFIRMING"
    OUTPUT = "OUTPUT"
    WAIT_FOR_NEXT_SIGN = "WAIT_FOR_NEXT_SIGN"
    
    def __init__(self, confirm_frames: int = 3, hold_frames: int = 12):
        self.state = self.IDLE
        self.candidate_sign = None
        self.confirmed_sign = None
        self.confirm_counter = 0
        self.hold_counter = 0
        self.confirm_frames = confirm_frames
        self.hold_frames = hold_frames
        self.emitted_this_cycle = False
        
    def update(self, raw_sign: str, confidence: float, threshold: float = 0.70) -> Tuple[str, str, bool]:
        is_valid = (raw_sign not in ["NO_HAND", "UNKNOWN_GESTURE"]) and (confidence >= threshold)
        new_output = False
        
        if not is_valid:
            if self.state == self.WAIT_FOR_NEXT_SIGN:
                self.hold_counter += 1
                if self.hold_counter > self.hold_frames:
                    self.state = self.IDLE
                    self.candidate_sign = None
                    self.emitted_this_cycle = False
            else:
                self.state = self.IDLE
                self.candidate_sign = None
                self.confirm_counter = 0
            return (raw_sign, self.state, False)
            
        if self.state == self.IDLE:
            self.state = self.SIGN_DETECTED
            self.candidate_sign = raw_sign
            self.confirm_counter = 1
        elif self.state == self.SIGN_DETECTED:
            if raw_sign == self.candidate_sign:
                self.state = self.CONFIRMING
                self.confirm_counter += 1
            else:
                self.candidate_sign = raw_sign
                self.confirm_counter = 1
        elif self.state == self.CONFIRMING:
            if raw_sign == self.candidate_sign:
                self.confirm_counter += 1
                if self.confirm_counter >= self.confirm_frames:
                    self.state = self.OUTPUT
                    self.confirmed_sign = raw_sign
                    new_output = True
                    self.emitted_this_cycle = True
            else:
                self.candidate_sign = raw_sign
                self.confirm_counter = 1
                self.state = self.SIGN_DETECTED
        elif self.state == self.OUTPUT:
            self.state = self.WAIT_FOR_NEXT_SIGN
            self.hold_counter = 1
        elif self.state == self.WAIT_FOR_NEXT_SIGN:
            if raw_sign != self.confirmed_sign:
                self.state = self.SIGN_DETECTED
                self.candidate_sign = raw_sign
                self.confirm_counter = 1
                self.emitted_this_cycle = False
            else:
                self.hold_counter += 1
                
        display = self.confirmed_sign if (self.state in [self.OUTPUT, self.WAIT_FOR_NEXT_SIGN] and self.confirmed_sign) else raw_sign
        return (display, self.state, new_output)

class InferenceEngine:
    """Production Dual-Hand ISL Real-Time Inference Engine."""
    def __init__(self):
        self.sequence_buffer = deque(maxlen=20)
        self.feature_sequence = deque(maxlen=20)
        self.recent_predictions = deque(maxlen=8)
        self.state_machine = SignStateMachine(confirm_frames=3, hold_frames=15)
        self.custom_matcher = CustomGestureMatcher()
        self.min_confidence = CONFIDENCE_THRESHOLD
        self.prev_centroid = None
        
        # 1. Load Static Random Forest model
        self.rf_model = None
        rf_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/static_gesture_model.pkl")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models/static_gesture_model.pkl"))
        ]
        for p in rf_paths:
            if os.path.exists(p):
                try:
                    import joblib
                    self.rf_model = joblib.load(p)
                    break
                except Exception:
                    pass

        # 2. Load Dynamic LSTM model
        self.lstm_model = None
        self.lstm_classes = []
        lstm_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/dynamic_gesture_lstm.pt")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models/dynamic_gesture_lstm.pt"))
        ]
        for p in lstm_paths:
            if os.path.exists(p):
                try:
                    ckpt = torch.load(p, map_location=torch.device('cpu'), weights_only=False)
                    self.lstm_classes = ckpt.get("classes", [])
                    model = DynamicGestureLSTM(
                        input_dim=ckpt.get("input_dim", 206),
                        hidden_dim=ckpt.get("hidden_dim", 64),
                        num_classes=len(self.lstm_classes),
                        num_layers=ckpt.get("num_layers", 2)
                    )
                    model.load_state_dict(ckpt["model_state_dict"])
                    model.eval()
                    self.lstm_model = model
                    break
                except Exception:
                    pass

    def compute_motion_magnitude(self, left_lms, right_lms) -> float:
        current_pts = []
        if left_lms: current_pts.extend([(lm['x'], lm['y']) for lm in left_lms[:21]])
        if right_lms: current_pts.extend([(lm['x'], lm['y']) for lm in right_lms[:21]])
        
        if not current_pts:
            self.prev_centroid = None
            return 0.0
            
        current_center = np.mean(current_pts, axis=0)
        if self.prev_centroid is None:
            self.prev_centroid = current_center
            return 0.0
            
        velocity = float(np.linalg.norm(current_center - self.prev_centroid))
        self.prev_centroid = current_center
        return velocity

    def process_frame(
        self,
        left_landmarks: Optional[List[Dict[str, float]]] = None,
        right_landmarks: Optional[List[Dict[str, float]]] = None,
        landmarks: Optional[List[Dict[str, float]]] = None,
        handedness: str = "Right",
        mirrored_camera: bool = True,
        user_id: Optional[int] = None,
        use_custom_gestures: bool = True
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        if left_landmarks is None and right_landmarks is None and landmarks:
            if handedness.lower() == "left":
                left_landmarks = landmarks
            else:
                right_landmarks = landmarks

        left_detected = left_landmarks is not None and len(left_landmarks) >= 21
        right_detected = right_landmarks is not None and len(right_landmarks) >= 21
        num_hands = int(left_detected) + int(right_detected)

        if num_hands == 0:
            self.sequence_buffer.clear()
            self.feature_sequence.clear()
            self.state_machine.update("NO_HAND", 0.0)
            return {
                "gesture": "NO_HAND",
                "confidence": 0.0,
                "text_en": NO_HAND_SIGN["text_en"],
                "text_hi": NO_HAND_SIGN["text_hi"],
                "text_bn": NO_HAND_SIGN["text_bn"],
                "category": "none",
                "is_dynamic": False,
                "status": "no_hand",
                "message": NO_HAND_SIGN["description"],
                "alternatives": [],
                "num_hands": 0,
                "left_detected": False,
                "right_detected": False,
                "recognition_mode": "IDLE",
                "sequence_len": 0,
                "state_machine_state": SignStateMachine.IDLE,
                "fps": 30.0,
                "latency_ms": 1.0,
                "model_status": "Dual-Hand Ready"
            }

        # 1. Feature Extraction (206 features)
        feature_vector = LandmarkFeatureExtractor.extract_dual_hand_features(left_landmarks, right_landmarks)
        self.feature_sequence.append(feature_vector)
        self.sequence_buffer.append({"left": left_landmarks, "right": right_landmarks})
        
        # 2. Check Custom User Gestures
        if use_custom_gestures and user_id:
            custom_res = self.custom_matcher.match(user_id, feature_vector)
            if custom_res:
                c_name, c_conf = custom_res
                latency = (time.time() - start_time) * 1000.0
                return {
                    "gesture": c_name,
                    "confidence": round(c_conf, 3),
                    "text_en": c_name,
                    "text_hi": c_name,
                    "text_bn": c_name,
                    "category": "custom",
                    "is_dynamic": False,
                    "status": "success",
                    "message": f"Recognized custom gesture '{c_name}'",
                    "alternatives": [],
                    "num_hands": num_hands,
                    "left_detected": left_detected,
                    "right_detected": right_detected,
                    "recognition_mode": "CUSTOM",
                    "sequence_len": len(self.feature_sequence),
                    "state_machine_state": SignStateMachine.OUTPUT,
                    "is_new_confirmed_output": True,
                    "fps": 30.0,
                    "latency_ms": round(latency, 1),
                    "model_status": "Custom Model"
                }

        # 3. Geometric Rule Analysis
        geo_sign, geo_conf = GeometricRuleDetector.classify(left_landmarks, right_landmarks)
        
        # 4. Static Random Forest Classifier
        rf_sign = "UNKNOWN_GESTURE"
        rf_conf = 0.0
        rf_alts = []
        if self.rf_model is not None:
            try:
                probs = self.rf_model.predict_proba([feature_vector])[0]
                classes = self.rf_model.classes_
                top_idx = np.argmax(probs)
                rf_sign = classes[top_idx]
                rf_conf = float(probs[top_idx])
                sorted_idx = np.argsort(probs)[::-1]
                rf_alts = [{"gesture": classes[i], "confidence": round(float(probs[i]), 2)} for i in sorted_idx[1:4]]
            except Exception:
                pass

        # 5. Dynamic Motion Analysis
        velocity = self.compute_motion_magnitude(left_landmarks, right_landmarks)
        is_dynamic_motion = velocity > 0.025 and len(self.feature_sequence) >= 10
        recognition_mode = "DYNAMIC" if is_dynamic_motion else "STATIC"
        
        lstm_sign = None
        lstm_conf = 0.0
        if is_dynamic_motion and self.lstm_model is not None and len(self.feature_sequence) >= 15:
            try:
                seq_arr = np.array(list(self.feature_sequence)[-20:], dtype=np.float32)
                while len(seq_arr) < 20:
                    seq_arr = np.insert(seq_arr, 0, seq_arr[0], axis=0)
                seq_tensor = torch.tensor(seq_arr).unsqueeze(0)
                with torch.no_grad():
                    logits = self.lstm_model(seq_tensor)
                    sm_probs = torch.softmax(logits, dim=1)[0].numpy()
                    top_l_idx = int(np.argmax(sm_probs))
                    lstm_sign = self.lstm_classes[top_l_idx]
                    lstm_conf = float(sm_probs[top_l_idx])
            except Exception:
                pass

        # 6. Ensemble Decision
        if is_dynamic_motion and lstm_sign and lstm_conf >= 0.70 and lstm_sign != "UNKNOWN_GESTURE":
            final_sign = lstm_sign
            final_conf = lstm_conf
        elif geo_sign != "UNKNOWN_GESTURE" and geo_conf >= 0.85:
            final_sign = geo_sign
            final_conf = geo_conf
            if rf_sign == geo_sign:
                final_conf = min(0.98, geo_conf * 0.7 + rf_conf * 0.3)
        elif rf_conf >= 0.88 and rf_sign != "UNKNOWN_GESTURE":
            final_sign = rf_sign
            final_conf = rf_conf
        elif geo_sign != "UNKNOWN_GESTURE":
            final_sign = geo_sign
            final_conf = geo_conf
        else:
            final_sign = "UNKNOWN_GESTURE"
            final_conf = max(geo_conf, rf_conf)

        # 7. State Machine Debouncing
        display_sign, sm_state, is_new_output = self.state_machine.update(
            raw_sign=final_sign,
            confidence=final_conf,
            threshold=self.min_confidence
        )

        is_confident = final_conf >= self.min_confidence and final_sign != "UNKNOWN_GESTURE"
        status = "success" if is_confident else "low_confidence"
        
        meta = ISL_VOCABULARY.get(display_sign, None)
        if meta and is_confident:
            text_en = meta["text_en"]
            text_hi = meta["text_hi"]
            text_bn = meta["text_bn"]
            category = meta.get("category", "words")
            is_dynamic_flag = meta.get("mode") == "dynamic"
            message = f"Recognized ISL {meta.get('hands', 'one_hand').replace('_', '-')} sign '{display_sign}'"
        else:
            text_en = UNKNOWN_SIGN["text_en"]
            text_hi = UNKNOWN_SIGN["text_hi"]
            text_bn = UNKNOWN_SIGN["text_bn"]
            category = "unrecognized"
            is_dynamic_flag = False
            message = UNKNOWN_SIGN["description"]

        latency = (time.time() - start_time) * 1000.0

        return {
            "gesture": display_sign if is_confident else "UNKNOWN_GESTURE",
            "confidence": round(final_conf, 3),
            "text_en": text_en,
            "text_hi": text_hi,
            "text_bn": text_bn,
            "category": category,
            "is_dynamic": is_dynamic_flag,
            "status": status,
            "message": message,
            "alternatives": rf_alts,
            "num_hands": num_hands,
            "left_detected": left_detected,
            "right_detected": right_detected,
            "recognition_mode": recognition_mode,
            "sequence_len": len(self.feature_sequence),
            "state_machine_state": sm_state,
            "is_new_confirmed_output": is_new_output,
            "fps": 30.0,
            "latency_ms": round(latency, 1),
            "model_status": "ML Ensemble (Dual-Hand RF + LSTM)"
        }

# Global inference engine instance
inference_engine = InferenceEngine()
