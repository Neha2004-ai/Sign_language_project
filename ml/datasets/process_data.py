"""
ISL Data Preprocessor — Converts raw landmark JSON files to feature vectors.

Reads JSON samples from dataset/raw/<SIGN_NAME>/ and extracts 206-dimensional
feature vectors using the project's LandmarkFeatureExtractor, then saves
processed numpy arrays ready for model training.

Usage:
    python ml/datasets/process_data.py

Output:
    dataset/processed/X_static.npy       — Feature vectors for static model
    dataset/processed/y_static.npy       — Labels for static model
    dataset/processed/X_sequences.npy    — Sequence data for LSTM model (grouped samples)
    dataset/processed/y_sequences.npy    — Labels for LSTM model
    dataset/processed/class_names.json   — Ordered list of class names
    dataset/processed/dataset_manifest.json — Summary of dataset
"""

import os
import sys
import json
import numpy as np
from datetime import datetime
from collections import defaultdict

# Add project paths for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

from app.ml.feature_extractor import LandmarkFeatureExtractor


def load_raw_samples(raw_dir: str) -> dict:
    """
    Loads all JSON sample files from the raw dataset directory.
    
    Returns:
        dict: {sign_name: [list of sample dicts]}
    """
    samples_by_sign = defaultdict(list)
    
    if not os.path.exists(raw_dir):
        print(f"ERROR: Raw data directory not found: {raw_dir}")
        return samples_by_sign
    
    sign_dirs = [d for d in os.listdir(raw_dir) 
                 if os.path.isdir(os.path.join(raw_dir, d))]
    
    if not sign_dirs:
        print(f"WARNING: No sign directories found in {raw_dir}")
        return samples_by_sign
    
    for sign_dir_name in sorted(sign_dirs):
        sign_path = os.path.join(raw_dir, sign_dir_name)
        json_files = sorted([f for f in os.listdir(sign_path) if f.endswith(".json")])
        
        # Restore original sign name (underscore to space)
        sign_name = sign_dir_name.replace("_", " ")
        
        for jf in json_files:
            try:
                with open(os.path.join(sign_path, jf), "r") as f:
                    sample = json.load(f)
                samples_by_sign[sign_name].append(sample)
            except (json.JSONDecodeError, IOError) as e:
                print(f"  WARNING: Skipping corrupt file {sign_path}/{jf}: {e}")
    
    return dict(samples_by_sign)


def extract_features(samples_by_sign: dict) -> tuple:
    """
    Extracts 206-dimensional feature vectors from raw landmark data.
    
    Returns:
        X: np.ndarray of shape (N, 206) — feature vectors
        y: np.ndarray of shape (N,) — string labels
        class_names: sorted list of unique class names
    """
    X_list = []
    y_list = []
    
    for sign_name, samples in sorted(samples_by_sign.items()):
        for sample in samples:
            left_lms = sample.get("left_landmarks")
            right_lms = sample.get("right_landmarks")
            
            # Extract 206-dim feature vector using project's extractor
            feature_vec = LandmarkFeatureExtractor.extract_dual_hand_features(
                left_landmarks=left_lms,
                right_landmarks=right_lms
            )
            
            X_list.append(feature_vec)
            y_list.append(sign_name)
    
    if not X_list:
        return np.array([]), np.array([]), []
    
    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list)
    class_names = sorted(list(set(y_list)))
    
    return X, y, class_names


def create_sequences(samples_by_sign: dict, seq_len: int = 20) -> tuple:
    """
    Creates temporal sequences for the LSTM model.
    
    For signs with enough samples, creates overlapping windows of seq_len frames.
    For signs with fewer samples, replicates and augments to fill the sequence.
    
    Returns:
        X_seq: np.ndarray of shape (N, seq_len, 206)
        y_seq: np.ndarray of shape (N,) — integer class indices
        class_names: ordered list of class names
    """
    X_sequences = []
    y_sequences = []
    class_names = sorted(samples_by_sign.keys())
    class_to_idx = {name: idx for idx, name in enumerate(class_names)}
    
    for sign_name, samples in sorted(samples_by_sign.items()):
        # Extract feature vectors for all samples of this sign
        features = []
        for sample in samples:
            left_lms = sample.get("left_landmarks")
            right_lms = sample.get("right_landmarks")
            feat = LandmarkFeatureExtractor.extract_dual_hand_features(left_lms, right_lms)
            features.append(feat)
        
        if len(features) < 3:
            print(f"  WARNING: Sign '{sign_name}' has only {len(features)} samples — too few for sequences, skipping")
            continue
        
        features = np.array(features, dtype=np.float32)
        
        # Create sequences by sliding window or padding
        if len(features) >= seq_len:
            # Sliding window
            for start in range(0, len(features) - seq_len + 1):
                seq = features[start:start + seq_len]
                X_sequences.append(seq)
                y_sequences.append(class_to_idx[sign_name])
        else:
            # Pad by repeating samples with slight augmentation
            augmented_sequences = []
            for _ in range(max(3, seq_len // len(features))):
                # Shuffle and repeat to fill seq_len
                indices = np.random.choice(len(features), size=seq_len, replace=True)
                seq = features[indices]
                # Add small noise for augmentation
                noise = np.random.normal(0, 0.01, size=seq.shape).astype(np.float32)
                seq = seq + noise
                augmented_sequences.append(seq)
            
            for seq in augmented_sequences:
                X_sequences.append(seq)
                y_sequences.append(class_to_idx[sign_name])
    
    if not X_sequences:
        return np.array([]), np.array([]), class_names
    
    X_seq = np.array(X_sequences, dtype=np.float32)
    y_seq = np.array(y_sequences, dtype=np.int64)
    
    return X_seq, y_seq, class_names


def main():
    raw_dir = os.path.join(PROJECT_ROOT, "dataset", "raw")
    processed_dir = os.path.join(PROJECT_ROOT, "dataset", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("  ISL Data Preprocessor")
    print("=" * 60)
    print(f"  Raw data:      {raw_dir}")
    print(f"  Output:        {processed_dir}")
    print("=" * 60 + "\n")
    
    # 1. Load raw samples
    print("Loading raw samples...")
    samples_by_sign = load_raw_samples(raw_dir)
    
    if not samples_by_sign:
        print("\nERROR: No raw data found!")
        print(f"  Please run 'python ml/datasets/collect_data.py' first to record ISL signs.")
        print(f"  Expected data in: {raw_dir}/<SIGN_NAME>/sample_XXXX.json")
        sys.exit(1)
    
    total_samples = sum(len(v) for v in samples_by_sign.values())
    print(f"  Found {total_samples} samples across {len(samples_by_sign)} signs:")
    for sign, samples in sorted(samples_by_sign.items()):
        print(f"    {sign:20s} — {len(samples):4d} samples")
    
    # 2. Extract static features
    print("\nExtracting 206-dim feature vectors...")
    X_static, y_static, class_names = extract_features(samples_by_sign)
    
    if len(X_static) == 0:
        print("ERROR: No features extracted!")
        sys.exit(1)
    
    print(f"  Static features: {X_static.shape} ({len(class_names)} classes)")
    
    # Save static features
    np.save(os.path.join(processed_dir, "X_static.npy"), X_static)
    np.save(os.path.join(processed_dir, "y_static.npy"), y_static)
    print(f"  Saved X_static.npy and y_static.npy")
    
    # 3. Create temporal sequences for LSTM
    print("\nCreating temporal sequences for LSTM...")
    X_seq, y_seq, seq_class_names = create_sequences(samples_by_sign, seq_len=20)
    
    if len(X_seq) > 0:
        print(f"  Sequence features: {X_seq.shape} ({len(seq_class_names)} classes)")
        np.save(os.path.join(processed_dir, "X_sequences.npy"), X_seq)
        np.save(os.path.join(processed_dir, "y_sequences.npy"), y_seq)
        print(f"  Saved X_sequences.npy and y_sequences.npy")
    else:
        print("  WARNING: Not enough data for sequence creation (need 3+ samples per sign)")
    
    # 4. Save class names and manifest
    with open(os.path.join(processed_dir, "class_names.json"), "w") as f:
        json.dump(class_names, f, indent=2)
    
    manifest = {
        "created_at": datetime.now().isoformat(),
        "total_samples": total_samples,
        "num_classes": len(class_names),
        "class_names": class_names,
        "samples_per_class": {sign: len(samples) for sign, samples in sorted(samples_by_sign.items())},
        "feature_dim": 206,
        "static_shape": list(X_static.shape),
        "sequence_shape": list(X_seq.shape) if len(X_seq) > 0 else None,
        "sequence_length": 20
    }
    
    with open(os.path.join(processed_dir, "dataset_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n  Saved class_names.json and dataset_manifest.json")
    
    print(f"\n{'='*60}")
    print(f"  Processing Complete!")
    print(f"  Classes: {len(class_names)}")
    print(f"  Static samples: {len(X_static)}")
    print(f"  Sequence samples: {len(X_seq)}")
    print(f"{'='*60}")
    print(f"\n  Next step: Run training scripts:")
    print(f"    python ml/training/train_classifier.py")
    print(f"    python ml/training/train_lstm.py\n")


if __name__ == "__main__":
    main()
