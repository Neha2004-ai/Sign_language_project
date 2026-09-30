# Dataset Preparation Guide

## Folder Structure

```
dataset/
  raw/           # Raw video recordings / image frames
  processed/     # Extracted 21-landmark JSON / CSV vectors
  seed/          # Seed gesture baseline dataset
```

## Adding New ISL Gestures

1. Add gesture metadata to `backend/app/db/seed_data.py` or via the Admin Dashboard.
2. Record 50–150 samples per gesture using the webcam or `Custom Gestures` module.
3. Run `python ml/training/train_classifier.py` to retrain and update weights.
