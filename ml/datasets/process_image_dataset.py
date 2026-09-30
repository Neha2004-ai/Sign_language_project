"""
ISL Gesture Image Dataset Processor
Extracts 21 3D hand landmarks and 206-dimensional invariant feature vectors from 
the 'dataset - Gesture Speech' alphabet gesture images using MediaPipe Tasks HandLandmarker.

Saves:
- dataset/raw/<SIGN>/sample_XXXX.json (Raw landmarks)
- dataset/processed/X_static.npy (Feature matrix)
- dataset/processed/y_static.npy (Labels)
- dataset/processed/class_names.json (Class list)
- dataset/processed/dataset_manifest.json (Dataset metadata)

Usage:
    python ml/datasets/process_image_dataset.py --samples_per_class 200
"""

import os
import sys
import json
import glob
import time
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

from app.ml.feature_extractor import LandmarkFeatureExtractor

MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "hand_landmarker.task")


def create_detector():
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_hands=2,
        min_hand_detection_confidence=0.4,
        min_hand_presence_confidence=0.4
    )
    return vision.HandLandmarker.create_from_options(options)


def process_image(detector, image_path: str):
    """
    Reads an image and detects hand landmarks.
    Returns (left_landmarks, right_landmarks) or (None, None).
    """
    try:
        bgr = cv2.imread(image_path)
        if bgr is None:
            return None, None
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        res = detector.detect(mp_img)

        if not res or not res.hand_landmarks:
            return None, None

        left_lms = None
        right_lms = None

        for idx, lms in enumerate(res.hand_landmarks):
            handedness = "Right"
            if res.handedness and idx < len(res.handedness) and len(res.handedness[idx]) > 0:
                handedness = res.handedness[idx][0].category_name

            lm_list = [{"x": float(p.x), "y": float(p.y), "z": float(p.z)} for p in lms]

            if handedness.lower() == "left":
                left_lms = lm_list
            else:
                right_lms = lm_list

        # If only one hand detected and handedness wasn't set, default to right hand
        if left_lms is None and right_lms is None and len(res.hand_landmarks) > 0:
            right_lms = [{"x": float(p.x), "y": float(p.y), "z": float(p.z)} for p in res.hand_landmarks[0]]

        return left_lms, right_lms
    except Exception:
        return None, None


def main():
    parser = argparse.ArgumentParser(description="Process Sign Gesture Image Dataset")
    parser.add_argument("--samples_per_class", type=int, default=200, help="Max samples to extract per class")
    parser.add_argument("--dataset_dir", type=str, default="dataset - Gesture Speech", help="Path to gesture images")
    args = parser.parse_args()

    input_dir = os.path.join(PROJECT_ROOT, args.dataset_dir)
    raw_dir = os.path.join(PROJECT_ROOT, "dataset", "raw")
    processed_dir = os.path.join(PROJECT_ROOT, "dataset", "processed")

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    print("=" * 65)
    print("  ISL Gesture Dataset Processor (A-Z Alphabets)")
    print("=" * 65)
    print(f"  Input Dataset:      {input_dir}")
    print(f"  Target Raw Dir:     {raw_dir}")
    print(f"  Target Processed:   {processed_dir}")
    print(f"  Samples per class:  {args.samples_per_class}")
    print(f"  Model Asset:        {MODEL_PATH}")
    print("=" * 65 + "\n")

    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model file {MODEL_PATH} not found!")
        sys.exit(1)

    class_dirs = sorted([d for d in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, d))])
    if not class_dirs:
        print(f"ERROR: No class directories found in {input_dir}")
        sys.exit(1)

    detector = create_detector()

    all_features = []
    all_labels = []
    class_counts = {}

    start_time = time.time()
    total_processed = 0

    for c_dir in class_dirs:
        label = c_dir.upper()
        c_path = os.path.join(input_dir, c_dir)
        raw_class_dir = os.path.join(raw_dir, label)
        os.makedirs(raw_class_dir, exist_ok=True)

        images = glob.glob(os.path.join(c_path, "*.jpg")) + glob.glob(os.path.join(c_path, "*.png"))
        if not images:
            continue

        # Sort and select evenly spaced images
        images = sorted(images)
        step = max(1, len(images) // args.samples_per_class)
        selected_images = images[::step][:args.samples_per_class]

        extracted_count = 0

        for img_path in selected_images:
            left_lms, right_lms = process_image(detector, img_path)
            if left_lms is None and right_lms is None:
                continue

            # 1. Extract 206-dim feature vector
            feat_vec = LandmarkFeatureExtractor.extract_dual_hand_features(left_lms, right_lms)
            all_features.append(feat_vec)
            all_labels.append(label)

            # 2. Save raw sample JSON
            sample_data = {
                "sign_name": label,
                "timestamp": datetime.now().isoformat(),
                "image_source": os.path.basename(img_path),
                "left_landmarks": left_lms,
                "right_landmarks": right_lms
            }
            sample_file = os.path.join(raw_class_dir, f"sample_{extracted_count:04d}.json")
            with open(sample_file, "w") as f:
                json.dump(sample_data, f)

            extracted_count += 1
            total_processed += 1

        class_counts[label] = extracted_count
        print(f"  [OK] Class '{label:3s}': {extracted_count:4d} samples extracted from {len(selected_images)} images", flush=True)

    detector.close()

    elapsed = time.time() - start_time
    print(f"\nLandmark extraction completed in {elapsed:.1f}s ({total_processed} total samples).")

    if not all_features:
        print("ERROR: No features extracted from dataset!")
        sys.exit(1)

    X = np.array(all_features, dtype=np.float32)
    y = np.array(all_labels)
    unique_classes = sorted(list(set(y)))

    # Save processed numpy arrays
    np.save(os.path.join(processed_dir, "X_static.npy"), X)
    np.save(os.path.join(processed_dir, "y_static.npy"), y)
    print(f"\nSaved {os.path.join(processed_dir, 'X_static.npy')} -> Shape: {X.shape}")
    print(f"Saved {os.path.join(processed_dir, 'y_static.npy')} -> Shape: {y.shape}")

    # Save class names
    with open(os.path.join(processed_dir, "class_names.json"), "w") as f:
        json.dump(unique_classes, f, indent=2)

    # Save manifest
    manifest = {
        "created_at": datetime.now().isoformat(),
        "total_samples": len(X),
        "num_classes": len(unique_classes),
        "class_names": unique_classes,
        "samples_per_class": class_counts,
        "feature_dim": 206,
        "source": args.dataset_dir,
        "static_shape": list(X.shape)
    }
    with open(os.path.join(processed_dir, "dataset_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print("Saved dataset manifest and class names.")
    print("\nDataset is now ready for training! Next step:")
    print("  python ml/training/train_classifier.py\n")


if __name__ == "__main__":
    main()
