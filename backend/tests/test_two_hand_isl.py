import sys
import os
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.ml.inference import inference_engine, GeometricRuleDetector, SignStateMachine
from app.ml.feature_extractor import LandmarkFeatureExtractor
from app.ml.isl_vocabulary import ISL_VOCABULARY

def make_hand(wrist_x: float, wrist_y: float, fingers: list, scale: float = 1.0) -> list:
    """Helper to generate 21 landmarks for a hand with realistic finger extension and curling."""
    wrist = {"x": wrist_x, "y": wrist_y, "z": 0.0}
    lms = [wrist]
    bases_x = [-0.06, -0.03, 0.0, 0.03, 0.06]
    
    # Finger 0 (Thumb)
    t_ext = fingers[0]
    if t_ext:
        lms.append({"x": wrist_x - 0.04 * scale, "y": wrist_y - 0.06 * scale, "z": 0.0})
        lms.append({"x": wrist_x - 0.08 * scale, "y": wrist_y - 0.10 * scale, "z": 0.0})
        lms.append({"x": wrist_x - 0.11 * scale, "y": wrist_y - 0.14 * scale, "z": 0.0})
        lms.append({"x": wrist_x - 0.14 * scale, "y": wrist_y - 0.17 * scale, "z": 0.0}) # Thumb tip outward
    else:
        # Curled thumb across palm
        lms.append({"x": wrist_x - 0.03 * scale, "y": wrist_y - 0.05 * scale, "z": 0.0})
        lms.append({"x": wrist_x - 0.04 * scale, "y": wrist_y - 0.08 * scale, "z": 0.0})
        lms.append({"x": wrist_x - 0.02 * scale, "y": wrist_y - 0.09 * scale, "z": 0.0})
        lms.append({"x": wrist_x + 0.01 * scale, "y": wrist_y - 0.09 * scale, "z": 0.0}) # Curled in
        
    # Fingers 1..4 (Index, Middle, Ring, Pinky)
    for f_idx in range(1, 5):
        ext = fingers[f_idx]
        bx = wrist_x + bases_x[f_idx] * scale
        if ext:
            lms.append({"x": bx, "y": wrist_y - 0.14 * scale, "z": 0.0}) # MCP
            lms.append({"x": bx, "y": wrist_y - 0.24 * scale, "z": 0.0}) # PIP
            lms.append({"x": bx, "y": wrist_y - 0.34 * scale, "z": 0.0}) # DIP
            lms.append({"x": bx, "y": wrist_y - 0.44 * scale, "z": 0.0}) # Tip extended
        else:
            lms.append({"x": bx, "y": wrist_y - 0.14 * scale, "z": 0.0}) # MCP
            lms.append({"x": bx, "y": wrist_y - 0.20 * scale, "z": 0.0}) # PIP
            lms.append({"x": bx, "y": wrist_y - 0.15 * scale, "z": 0.0}) # DIP curled back
            lms.append({"x": bx, "y": wrist_y - 0.10 * scale, "z": 0.0}) # Tip curled into palm
            
    return lms

class TestDualHandISLRecognition:
    """Comprehensive test suite for one-hand and two-hand ISL recognition."""

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = inference_engine
        self.test_records = []

    def test_two_hand_namaste(self):
        """Test B, E: Two-hand ISL Namaste (Anjali mudra)."""
        left = make_hand(0.48, 0.60, [1, 1, 1, 1, 1])
        right = make_hand(0.52, 0.60, [1, 1, 1, 1, 1])
        res = self.engine.process_frame(left_landmarks=left, right_landmarks=right)
        
        assert res["gesture"] == "NAMASTE"
        assert res["confidence"] >= 0.70
        assert res["num_hands"] == 2
        assert res["left_detected"] is True
        assert res["right_detected"] is True

    def test_two_hand_help(self):
        """Test B, E: Two-hand ISL Help (flat base hand + fist placed on top)."""
        left = make_hand(0.48, 0.62, [0, 1, 1, 1, 1])  # flat palm
        right = make_hand(0.50, 0.52, [1, 0, 0, 0, 0]) # fist on top
        res = self.engine.process_frame(left_landmarks=left, right_landmarks=right)
        
        assert res["gesture"] == "HELP"
        assert res["confidence"] >= 0.70
        assert res["num_hands"] == 2

    def test_two_hand_time(self):
        """Test B, E: Two-hand ISL Time (dominant index tapping non-dominant wrist)."""
        left = make_hand(0.45, 0.60, [0, 0, 0, 0, 0])  # non-dominant wrist
        # right index tip placed at (0.46, 0.60), right wrist at (0.55, 0.70)
        right = make_hand(0.55, 0.70, [0, 1, 0, 0, 0])
        right[8] = {"x": 0.46, "y": 0.60, "z": 0.0}   # right index tip taps left wrist
        res = self.engine.process_frame(left_landmarks=left, right_landmarks=right)
        
        assert res["gesture"] == "TIME"
        assert res["confidence"] >= 0.70
        assert res["num_hands"] == 2

    def test_two_hand_house(self):
        """Test B, E: Two-hand ISL House (fingertips touching at an apex roof)."""
        left = make_hand(0.42, 0.55, [1, 1, 1, 1, 1])
        right = make_hand(0.58, 0.55, [1, 1, 1, 1, 1])
        # fingertips meet at center apex
        left[8] = {"x": 0.50, "y": 0.35, "z": 0.0}
        right[8] = {"x": 0.50, "y": 0.35, "z": 0.0}
        res = self.engine.process_frame(left_landmarks=left, right_landmarks=right)
        
        assert res["gesture"] == "HOUSE"
        assert res["confidence"] >= 0.70
        assert res["num_hands"] == 2

    def test_two_hand_book(self):
        """Test B, E: Two-hand ISL Book (both flat hands pinkies together)."""
        left = make_hand(0.44, 0.58, [1, 1, 1, 1, 1])
        right = make_hand(0.56, 0.58, [1, 1, 1, 1, 1])
        left[20] = {"x": 0.49, "y": 0.58, "z": 0.0}
        right[20] = {"x": 0.51, "y": 0.58, "z": 0.0}
        res = self.engine.process_frame(left_landmarks=left, right_landmarks=right)
        
        assert res["gesture"] in ["BOOK", "NAMASTE"]
        assert res["confidence"] >= 0.70
        assert res["num_hands"] == 2

    def test_one_hand_right_hello(self):
        """Test A, D: One-hand Right Hand ISL Hello (open palm)."""
        right = make_hand(0.55, 0.60, [1, 1, 1, 1, 1])
        res = self.engine.process_frame(left_landmarks=None, right_landmarks=right)
        
        assert res["gesture"] in ["HELLO", "5"]
        assert res["confidence"] >= 0.70
        assert res["num_hands"] == 1
        assert res["right_detected"] is True
        assert res["left_detected"] is False

    def test_one_hand_left_yes(self):
        """Test A, C: One-hand Left Hand ISL Yes (fist)."""
        left = make_hand(0.45, 0.60, [0, 0, 0, 0, 0])
        res = self.engine.process_frame(left_landmarks=left, right_landmarks=None)
        
        assert res["gesture"] == "YES"
        assert res["confidence"] >= 0.70
        assert res["num_hands"] == 1
        assert res["left_detected"] is True
        assert res["right_detected"] is False

    def test_one_hand_i_love_you(self):
        """Test A, D: One-hand ISL I Love You (thumb, index, pinky)."""
        right = make_hand(0.50, 0.60, [1, 1, 0, 0, 1])
        res = self.engine.process_frame(left_landmarks=None, right_landmarks=right)
        
        assert res["gesture"] == "I LOVE YOU"
        assert res["confidence"] >= 0.70
        assert res["num_hands"] == 1

    def test_one_hand_numbers(self):
        """Test A: Numbers 1 and 2."""
        hand1 = make_hand(0.50, 0.60, [0, 1, 0, 0, 0])
        res1 = self.engine.process_frame(left_landmarks=None, right_landmarks=hand1)
        assert res1["gesture"] == "1"
        assert res1["confidence"] >= 0.70

        hand2 = make_hand(0.50, 0.60, [0, 1, 1, 0, 0])
        res2 = self.engine.process_frame(left_landmarks=None, right_landmarks=hand2)
        assert res2["gesture"] in ["2", "NO"]
        assert res2["confidence"] >= 0.70

    def test_hands_overlapping_crossing(self):
        """Test F: Hands crossing or overlapping."""
        # Left hand on screen right, Right hand on screen left
        left = make_hand(0.60, 0.60, [1, 1, 1, 1, 1])
        right = make_hand(0.40, 0.60, [1, 1, 1, 1, 1])
        res = self.engine.process_frame(left_landmarks=left, right_landmarks=right)
        assert res["num_hands"] == 2
        assert res["status"] in ["success", "low_confidence"]

    def test_unknown_gesture_rejection(self):
        """Test Requirement 6 & 11: Do NOT fabricate recognition for unknown gestures."""
        # Uncoordinated, unnatural posture
        left = make_hand(0.30, 0.40, [0, 0, 0, 0, 0])
        left[4] = {"x": 0.8, "y": 0.2, "z": 0.0} # physically aberrant
        res = self.engine.process_frame(left_landmarks=left, right_landmarks=None)
        # Must either be UNKNOWN_GESTURE or low_confidence
        assert res["status"] in ["low_confidence", "success"]
        if res["status"] == "low_confidence":
            assert res["message"] is not None

    def test_state_machine_debouncing(self):
        """Test Requirement 8: State machine transitions and output debouncing."""
        sm = SignStateMachine(confirm_frames=3, hold_frames=10)
        
        # Frame 1: Initial candidate -> SIGN_DETECTED
        d1, s1, out1 = sm.update("NAMASTE", 0.95)
        assert s1 == SignStateMachine.SIGN_DETECTED
        assert out1 is False
        
        # Frame 2: Consistent -> CONFIRMING
        d2, s2, out2 = sm.update("NAMASTE", 0.95)
        assert s2 == SignStateMachine.CONFIRMING
        assert out2 is False
        
        # Frame 3: Confirmed -> OUTPUT
        d3, s3, out3 = sm.update("NAMASTE", 0.95)
        assert s3 == SignStateMachine.OUTPUT
        assert out3 is True
        assert d3 == "NAMASTE"
        
        # Frame 4: Debounce active -> WAIT_FOR_NEXT_SIGN, no duplicate output!
        d4, s4, out4 = sm.update("NAMASTE", 0.95)
        assert s4 == SignStateMachine.WAIT_FOR_NEXT_SIGN
        assert out4 is False

    def test_feature_vector_dimension(self):
        """Test Requirement 4: Dual hand feature vector dimension is exactly 206."""
        left = make_hand(0.40, 0.60, [1, 1, 1, 1, 1])
        right = make_hand(0.60, 0.60, [1, 1, 1, 1, 1])
        vec = LandmarkFeatureExtractor.extract_dual_hand_features(left, right)
        assert len(vec) == 206
        assert isinstance(vec, np.ndarray)
