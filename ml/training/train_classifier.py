import os
import sys
import json
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Ensure backend path is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
from app.ml.feature_extractor import LandmarkFeatureExtractor
from app.ml.isl_vocabulary import ISL_VOCABULARY

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))


def load_real_dataset():
    """
    Loads real ISL dataset from processed numpy files.
    Returns (X, y) or (None, None) if no real data available.
    """
    processed_dir = os.path.join(PROJECT_ROOT, "dataset", "processed")
    x_path = os.path.join(processed_dir, "X_static.npy")
    y_path = os.path.join(processed_dir, "y_static.npy")

    if not os.path.exists(x_path) or not os.path.exists(y_path):
        return None, None

    X = np.load(x_path)
    y = np.load(y_path)

    if len(X) == 0:
        return None, None

    print(f"Loaded real dataset: {X.shape[0]} samples, {X.shape[1]} features, {len(set(y))} classes")
    for cls in sorted(set(y)):
        count = np.sum(y == cls)
        print(f"  {cls:20s} — {count:4d} samples")

    return X, y


def generate_hand_landmarks(wrist_x: float, wrist_y: float, finger_config: list, jitter: float = 0.02) -> list:
    """
    Generates 21 synthetic 3D hand landmarks for a given finger extension state.
    finger_config: [thumb, index, middle, ring, pinky] (1 = extended, 0 = curled)
    ONLY used as fallback when no real data is available.
    """
    landmarks = [{"x": wrist_x + np.random.normal(0, jitter), "y": wrist_y + np.random.normal(0, jitter), "z": 0.0}]
    finger_bases_x = [-0.08, -0.04, 0.0, 0.04, 0.08]

    for f_idx, is_ext in enumerate(finger_config):
        base_x = wrist_x + finger_bases_x[f_idx]
        ext_factor = 1.0 if is_ext else 0.35
        landmarks.append({"x": base_x + np.random.normal(0, 0.01), "y": wrist_y - 0.15 + np.random.normal(0, 0.01), "z": 0.0})
        landmarks.append({"x": base_x + np.random.normal(0, 0.01), "y": wrist_y - 0.25 * ext_factor + np.random.normal(0, 0.01), "z": 0.0})
        landmarks.append({"x": base_x + np.random.normal(0, 0.01), "y": wrist_y - 0.35 * ext_factor + np.random.normal(0, 0.01), "z": 0.0})
        landmarks.append({"x": base_x + np.random.normal(0, 0.01), "y": wrist_y - 0.45 * ext_factor + np.random.normal(0, 0.015), "z": 0.0})

    return landmarks


def generate_synthetic_fallback(num_samples_per_class: int = 120):
    """
    Generates synthetic ISL training samples as a FALLBACK only.
    Prints a prominent warning that real data should be used instead.
    """
    print("\n" + "!" * 60)
    print("  WARNING: No real ISL data found!")
    print("  Training on SYNTHETIC data (low accuracy).")
    print("  For real ISL recognition, collect data first:")
    print("    python ml/datasets/collect_data.py")
    print("    python ml/datasets/process_data.py")
    print("!" * 60 + "\n")

    X = []
    y = []

    # 1-Hand Gestures
    one_hand_templates = {
        "HELLO": [1, 1, 1, 1, 1],
        "THANK YOU": [0, 1, 1, 1, 1],
        "YES": [1, 0, 0, 0, 0],
        "NO": [0, 1, 1, 0, 0],
        "SORRY": [1, 0, 0, 0, 0],
        "PLEASE": [0, 1, 1, 1, 0],
        "WATER": [1, 0, 0, 0, 0],
        "I LOVE YOU": [1, 1, 0, 0, 1],
        "OK": [0, 1, 1, 1, 0],
        "1": [0, 1, 0, 0, 0],
        "2": [0, 1, 1, 0, 0],
        "3": [1, 1, 1, 0, 0],
        "4": [0, 1, 1, 1, 1],
        "5": [1, 1, 1, 1, 1]
    }

    for g_name, f_conf in one_hand_templates.items():
        for _ in range(num_samples_per_class):
            is_right_hand = np.random.random() > 0.3
            hand_lms = generate_hand_landmarks(0.5, 0.6, f_conf)
            if is_right_hand:
                feat = LandmarkFeatureExtractor.extract_dual_hand_features(left_landmarks=None, right_landmarks=hand_lms)
            else:
                feat = LandmarkFeatureExtractor.extract_dual_hand_features(left_landmarks=hand_lms, right_landmarks=None)
            X.append(feat)
            y.append(g_name)

    # 2-Hand Gestures
    two_hand_templates = {
        "NAMASTE": {"l_ext": [1, 1, 1, 1, 1], "r_ext": [1, 1, 1, 1, 1], "l_pos": (0.45, 0.55), "r_pos": (0.55, 0.55)},
        "HELP": {"l_ext": [0, 1, 1, 1, 1], "r_ext": [1, 0, 0, 0, 0], "l_pos": (0.48, 0.62), "r_pos": (0.50, 0.52)},
        "BOOK": {"l_ext": [1, 1, 1, 1, 1], "r_ext": [1, 1, 1, 1, 1], "l_pos": (0.40, 0.58), "r_pos": (0.60, 0.58)},
        "HOUSE": {"l_ext": [1, 1, 1, 1, 1], "r_ext": [1, 1, 1, 1, 1], "l_pos": (0.42, 0.45), "r_pos": (0.58, 0.45)},
        "TIME": {"l_ext": [0, 0, 0, 0, 0], "r_ext": [0, 1, 0, 0, 0], "l_pos": (0.45, 0.60), "r_pos": (0.47, 0.60)},
        "STOP": {"l_ext": [0, 1, 1, 1, 1], "r_ext": [1, 1, 1, 1, 1], "l_pos": (0.48, 0.65), "r_pos": (0.50, 0.50)},
        "WORK": {"l_ext": [0, 0, 0, 0, 0], "r_ext": [0, 0, 0, 0, 0], "l_pos": (0.46, 0.58), "r_pos": (0.54, 0.58)},
        "PEACE": {"l_ext": [0, 1, 1, 0, 0], "r_ext": [0, 1, 1, 0, 0], "l_pos": (0.35, 0.50), "r_pos": (0.65, 0.50)}
    }

    for g_name, spec in two_hand_templates.items():
        for _ in range(num_samples_per_class):
            l_lms = generate_hand_landmarks(spec["l_pos"][0], spec["l_pos"][1], spec["l_ext"])
            r_lms = generate_hand_landmarks(spec["r_pos"][0], spec["r_pos"][1], spec["r_ext"])
            feat = LandmarkFeatureExtractor.extract_dual_hand_features(left_landmarks=l_lms, right_landmarks=r_lms)
            X.append(feat)
            y.append(g_name)

    # UNKNOWN_GESTURE Negative Samples
    for _ in range(num_samples_per_class * 2):
        rand_left = np.random.random() > 0.5
        rand_right = np.random.random() > 0.5
        if not rand_left and not rand_right:
            rand_right = True

        l_lms = generate_hand_landmarks(np.random.uniform(0.2, 0.5), np.random.uniform(0.3, 0.8), np.random.choice([0, 1], size=5).tolist(), jitter=0.08) if rand_left else None
        r_lms = generate_hand_landmarks(np.random.uniform(0.5, 0.8), np.random.uniform(0.3, 0.8), np.random.choice([0, 1], size=5).tolist(), jitter=0.08) if rand_right else None
        feat = LandmarkFeatureExtractor.extract_dual_hand_features(left_landmarks=l_lms, right_landmarks=r_lms)
        feat += np.random.normal(0, 0.05, size=feat.shape).astype(np.float32)
        X.append(feat)
        y.append("UNKNOWN_GESTURE")

    return np.array(X, dtype=np.float32), np.array(y)


def add_unknown_gesture_samples(X, y, num_samples=200):
    """Adds UNKNOWN_GESTURE negative samples if not already present in the dataset."""
    if "UNKNOWN_GESTURE" in set(y):
        return X, y

    print(f"Adding {num_samples} UNKNOWN_GESTURE negative samples...")
    unknown_X = []
    unknown_y = []

    for _ in range(num_samples):
        # Generate random feature vectors as negatives
        rand_feat = np.random.normal(0, 0.3, size=206).astype(np.float32)
        unknown_X.append(rand_feat)
        unknown_y.append("UNKNOWN_GESTURE")

    X_combined = np.concatenate([X, np.array(unknown_X, dtype=np.float32)], axis=0)
    y_combined = np.concatenate([y, np.array(unknown_y)], axis=0)

    return X_combined, y_combined


def train_and_save_model():
    # 1. Try to load real dataset first
    print("Attempting to load real ISL dataset...")
    X, y = load_real_dataset()

    # 2. Fall back to synthetic if no real data
    if X is None or len(X) == 0:
        X, y = generate_synthetic_fallback(num_samples_per_class=120)
    else:
        print(f"\n[OK] Using REAL ISL dataset for training!")
        # Add unknown gesture negatives
        X, y = add_unknown_gesture_samples(X, y)

    print(f"\nTotal: {len(X)} samples with {X.shape[1]} features across {len(set(y))} classes.")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Training Random Forest Classifier on dual-hand 206-feature space...")
    clf = RandomForestClassifier(n_estimators=150, max_depth=20, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"\nTraining Complete! Test Accuracy: {acc * 100:.2f}%")
    print("\nClassification Report:\n", classification_report(y_test, preds))

    # Save model in both root models/ and backend/models/
    target_dirs = [
        os.path.join(PROJECT_ROOT, "models"),
        os.path.join(PROJECT_ROOT, "backend", "models")
    ]

    for t_dir in target_dirs:
        os.makedirs(t_dir, exist_ok=True)
        model_path = os.path.join(t_dir, "static_gesture_model.pkl")
        joblib.dump(clf, model_path)
        print(f"Model saved to: {model_path}")

    # Save training metadata
    meta = {
        "trained_at": __import__("datetime").datetime.now().isoformat(),
        "total_samples": len(X),
        "test_accuracy": round(acc, 4),
        "num_classes": len(set(y)),
        "class_names": sorted(list(set(y))),
        "data_source": "real" if os.path.exists(os.path.join(PROJECT_ROOT, "dataset", "processed", "X_static.npy")) else "synthetic",
        "model_type": "RandomForestClassifier",
        "n_estimators": 150,
        "feature_dim": 206
        
    }
    meta_path = os.path.join(PROJECT_ROOT, "models", "static_model_meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Training metadata saved to: {meta_path}")


if __name__ == "__main__":
    train_and_save_model()
