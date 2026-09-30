# Machine Learning Pipeline Guide

## 1. Landmark Feature Extraction

The pipeline transforms raw MediaPipe keypoints into a scale- and rotation-invariant 93-dimensional feature vector:

1. **Wrist Normalization**: Translates all 21 keypoints relative to Landmark 0 (Wrist):
   $$\mathbf{p}'_i = \mathbf{p}_i - \mathbf{p}_0$$
2. **Scale Invariance**: Scales by the maximum palm span between the wrist and the MCP knuckles:
   $$\text{scale} = \max_{j \in \{5, 9, 13, 17\}} \|\mathbf{p}'_j\|$$
   $$\mathbf{p}''_{i} = \frac{\mathbf{p}'_i}{\text{scale}}$$
3. **Joint Angle Invariants (15 features)**: Computes 3D joint bending angles across the 5 fingers.
4. **Fingertip Distances (15 features)**: Computes Euclidean distances from fingertips to the wrist and pairwise fingertip distances (e.g. thumb-to-index pinch distance).

---

## 2. Model Architectures

- **Static Gestures**: Random Forest Classifier (100 estimators) & Deep Multi-Layer Perceptron (MLP) trained on geometric feature representations.
- **Dynamic Gestures**: Bidirectional LSTM (2 layers, 64 hidden units) processing temporal sequence buffers across 15–30 frames.
- **Personalized Custom Gestures**: Real-time centroid template matching with cosine similarity calibration.

---

## 3. Training & Evaluation Commands

```bash
# 1. Train static classifier
python ml/training/train_classifier.py

# 2. Train dynamic sequence LSTM
python ml/training/train_lstm.py

# 3. Benchmark latency and evaluation metrics
python ml/evaluation/evaluate.py
```
