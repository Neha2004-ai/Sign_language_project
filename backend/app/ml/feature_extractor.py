import math
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

class LandmarkFeatureExtractor:
    """
    Production Feature Extractor for Indian Sign Language (ISL).
    Extracts invariant geometric, angular, and spatial features for:
    - Single Left Hand (93 dims)
    - Single Right Hand (93 dims)
    - Dual Hand Interaction & Relative Spatial Dynamics (20 dims)
    Total Feature Vector: 206 dimensions.
    
    Supports:
    - Left hand only
    - Right hand only
    - Both hands simultaneously
    - Crossing/overlapping hands
    - Clear missing-hand representation (explicit zero-padding with presence flags)
    """

    @staticmethod
    def normalize_landmarks(landmarks: List[Dict[str, float]]) -> np.ndarray:
        """
        Translates landmarks to wrist origin (landmark 0)
        and scales by max palm span for camera distance invariance.
        Returns shape (21, 3).
        """
        if not landmarks or len(landmarks) < 21:
            return np.zeros((21, 3), dtype=np.float32)
        
        coords = np.array([[lm.get('x', 0.0), lm.get('y', 0.0), lm.get('z', 0.0)] for lm in landmarks[:21]], dtype=np.float32)
        
        # 1. Translate wrist (index 0) to (0,0,0)
        wrist = coords[0].copy()
        translated = coords - wrist
        
        # 2. Compute bounding radius / scale factor (max distance from wrist to knuckles: MCPs 5, 9, 13, 17)
        mcp_indices = [5, 9, 13, 17]
        distances = np.linalg.norm(translated[mcp_indices], axis=1)
        scale = np.max(distances)
        if scale < 1e-6:
            scale = 1.0
            
        normalized = translated / scale
        return normalized

    @staticmethod
    def compute_joint_angles(coords: np.ndarray) -> np.ndarray:
        """
        Computes 3D joint bending angles for the 5 fingers (15 angles).
        For each finger, computes angle at MCP, PIP, and DIP.
        """
        angles = []
        joint_triplets = [
            (0, 1, 2), (1, 2, 3), (2, 3, 4),      # Thumb
            (0, 5, 6), (5, 6, 7), (6, 7, 8),      # Index
            (0, 9, 10), (9, 10, 11), (10, 11, 12),# Middle
            (0, 13, 14), (13, 14, 15), (14, 15, 16), # Ring
            (0, 17, 18), (17, 18, 19), (18, 19, 20)  # Pinky
        ]
        
        for a_idx, b_idx, c_idx in joint_triplets:
            v1 = coords[a_idx] - coords[b_idx]
            v2 = coords[c_idx] - coords[b_idx]
            
            dot = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            
            if norm_v1 * norm_v2 < 1e-6:
                angle = 0.0
            else:
                cos_val = np.clip(dot / (norm_v1 * norm_v2), -1.0, 1.0)
                angle = np.arccos(cos_val) / np.pi  # Normalize to [0, 1]
            angles.append(angle)
            
        return np.array(angles, dtype=np.float32)

    @staticmethod
    def compute_fingertip_distances(coords: np.ndarray) -> np.ndarray:
        """
        Computes distances between fingertips (4, 8, 12, 16, 20) and wrist (0)
        and pairwise fingertip distances (15 distances).
        """
        tips = [4, 8, 12, 16, 20]
        wrist_dist = [np.linalg.norm(coords[t]) for t in tips]
        
        pairwise_dist = []
        for i in range(len(tips)):
            for j in range(i + 1, len(tips)):
                d = np.linalg.norm(coords[tips[i]] - coords[tips[j]])
                pairwise_dist.append(d)
                
        return np.array(wrist_dist + pairwise_dist, dtype=np.float32)

    @classmethod
    def extract_single_hand_features(cls, landmarks: Optional[List[Dict[str, float]]]) -> np.ndarray:
        """
        Extracts 93-dimensional feature vector for one hand:
        - 21 normalized 3D landmarks (63)
        - 15 joint angles (15)
        - 15 fingertip distances (15)
        Returns zeros(93) if hand is missing.
        """
        if not landmarks or len(landmarks) < 21:
            return np.zeros(93, dtype=np.float32)
            
        norm_coords = cls.normalize_landmarks(landmarks)
        flat_coords = norm_coords.flatten()
        angles = cls.compute_joint_angles(norm_coords)
        distances = cls.compute_fingertip_distances(norm_coords)
        
        return np.concatenate([flat_coords, angles, distances])

    @classmethod
    def compute_palm_normal(cls, coords: np.ndarray) -> np.ndarray:
        """
        Computes the palm surface normal vector using wrist (0), index MCP (5), and pinky MCP (17).
        """
        v1 = coords[5] - coords[0]
        v2 = coords[17] - coords[0]
        normal = np.cross(v1, v2)
        norm = np.linalg.norm(normal)
        return normal / norm if norm > 1e-6 else np.array([0.0, 0.0, 1.0], dtype=np.float32)

    @classmethod
    def extract_dual_hand_features(
        cls,
        left_landmarks: Optional[List[Dict[str, float]]],
        right_landmarks: Optional[List[Dict[str, float]]]
    ) -> np.ndarray:
        """
        Produces the full unified 206-dimensional ISL feature vector:
        - Left hand features (93)
        - Right hand features (93)
        - Dual-hand presence & spatial interaction features (20)
        """
        left_valid = left_landmarks is not None and len(left_landmarks) >= 21
        right_valid = right_landmarks is not None and len(right_landmarks) >= 21
        
        # 1. Individual Hand Features (93 + 93)
        left_feats = cls.extract_single_hand_features(left_landmarks) if left_valid else np.zeros(93, dtype=np.float32)
        right_feats = cls.extract_single_hand_features(right_landmarks) if right_valid else np.zeros(93, dtype=np.float32)
        
        # 2. Inter-Hand Interaction Features (20)
        num_hands = float(left_valid) + float(right_valid)
        interaction = np.zeros(20, dtype=np.float32)
        
        # Feature 0..2: Presence flags
        interaction[0] = 1.0 if left_valid else 0.0
        interaction[1] = 1.0 if right_valid else 0.0
        interaction[2] = num_hands
        
        if left_valid and right_valid:
            l_coords = np.array([[lm['x'], lm['y'], lm.get('z', 0.0)] for lm in left_landmarks[:21]], dtype=np.float32)
            r_coords = np.array([[lm['x'], lm['y'], lm.get('z', 0.0)] for lm in right_landmarks[:21]], dtype=np.float32)
            
            # 3..5: Relative wrist vector (r - l)
            wrist_diff = r_coords[0] - l_coords[0]
            interaction[3:6] = wrist_diff
            
            # 6: Wrist-to-wrist Euclidean distance
            interaction[6] = np.linalg.norm(wrist_diff)
            
            # 7..11: Fingertip-to-fingertip distances (thumb, index, middle, ring, pinky)
            tips = [4, 8, 12, 16, 20]
            for idx, t in enumerate(tips):
                interaction[7 + idx] = np.linalg.norm(r_coords[t] - l_coords[t])
                
            # 12..13: Cross index-to-opposite-wrist distances
            interaction[12] = np.linalg.norm(l_coords[8] - r_coords[0])  # Left index to right wrist (TIME sign)
            interaction[13] = np.linalg.norm(r_coords[8] - l_coords[0])  # Right index to left wrist (TIME sign)
            
            # 14: Palm normal dot product (opposing = -1 for Namaste, parallel = +1, perpendicular = 0 for Stop)
            l_normal = cls.compute_palm_normal(l_coords)
            r_normal = cls.compute_palm_normal(r_coords)
            interaction[14] = float(np.dot(l_normal, r_normal))
            
            # 15: Relative wrist height (y coordinate)
            interaction[15] = r_coords[0, 1] - l_coords[0, 1]
            
            # 16: Relative index tip height
            interaction[16] = r_coords[8, 1] - l_coords[8, 1]
            
            # 17..19: Relative centroid difference
            l_centroid = np.mean(l_coords, axis=0)
            r_centroid = np.mean(r_coords, axis=0)
            interaction[17:20] = r_centroid - l_centroid
            
        return np.concatenate([left_feats, right_feats, interaction])

    @classmethod
    def extract_full_feature_vector(
        cls,
        landmarks: Optional[List[Dict[str, float]]] = None,
        left_landmarks: Optional[List[Dict[str, float]]] = None,
        right_landmarks: Optional[List[Dict[str, float]]] = None,
        handedness: str = "Right"
    ) -> np.ndarray:
        """
        Unified feature extractor supporting both legacy single-hand calls and modern dual-hand calls.
        Returns a 206-dimensional feature vector.
        """
        if left_landmarks is not None or right_landmarks is not None:
            return cls.extract_dual_hand_features(left_landmarks, right_landmarks)
            
        # Legacy fallback: single hand provided
        if landmarks and len(landmarks) >= 21:
            if handedness.lower() == "left":
                return cls.extract_dual_hand_features(left_landmarks=landmarks, right_landmarks=None)
            else:
                return cls.extract_dual_hand_features(left_landmarks=None, right_landmarks=landmarks)
                
        return np.zeros(206, dtype=np.float32)

    @classmethod
    def extract_sequence_features(
        cls,
        frames: List[Dict[str, Any]],
        max_seq_len: int = 20
    ) -> np.ndarray:
        """
        Converts a list of dual-hand frames into a temporal sequence matrix (max_seq_len, 206).
        """
        if not frames:
            return np.zeros((max_seq_len, 206), dtype=np.float32)
            
        feat_list = []
        for f in frames[-max_seq_len:]:
            if isinstance(f, dict) and ("left_landmarks" in f or "right_landmarks" in f):
                vec = cls.extract_dual_hand_features(f.get("left_landmarks"), f.get("right_landmarks"))
            elif isinstance(f, list):
                vec = cls.extract_full_feature_vector(landmarks=f)
            else:
                vec = np.zeros(206, dtype=np.float32)
            feat_list.append(vec)
            
        while len(feat_list) < max_seq_len:
            feat_list.insert(0, feat_list[0] if feat_list else np.zeros(206, dtype=np.float32))
            
        return np.array(feat_list, dtype=np.float32)
