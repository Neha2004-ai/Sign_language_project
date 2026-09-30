# SignBridge AI Architecture Documentation

## System Overview

SignBridge AI is an AI-powered, bidirectional Indian Sign Language (ISL) communication platform designed to enable accessible, real-time dialogue between ISL users and hearing individuals across **English, Hindi, and Bengali**.

## High-Level Architecture

```
+-----------------------------------------------------------------------------------+
|                                  USER CLIENT                                      |
|                                                                                   |
|  [ Live Webcam ]               [ Microphone ]              [ Text / Keyboard ]    |
|         │                             │                             │             |
|         ▼                             ▼                             ▼             |
|  MediaPipe Hands               Web Speech API               Natural Multilingual  |
|  (21 3D Keypoints)             (EN / HI / BN)               Sentence Input        |
|         │                             │                             │             |
+---------┼─────────────────────────────┼─────────────────────────────┼-------------+
          │ (WebSocket / REST)          │ (REST API)                  │ (REST API)
          ▼                             ▼                             ▼
+-----------------------------------------------------------------------------------+
|                             FASTAPI BACKEND GATEWAY                               |
|                                                                                   |
|  [ WebSocket Handler ]       [ Speech & NLP Router ]       [ Translation Router ] |
|  /ws/sign-recognition        /api/speech/to-sign           /api/translate/text    |
|         │                             │                             │             |
|         ▼                             ▼                             ▼             |
|  +--------------------+     +---------------------+     +-----------------------+ |
|  |  ML Inference &    |     |  Semantic ISL       |     |  Provider-Independent| |
|  |  Temporal Engine   |     |  Tokenizer & Normal |     |  EN ↔ HI ↔ BN Engine  | |
|  +--------------------+     +---------------------+     +-----------------------+ |
|         │                             │                             │             |
|         ▼                             ▼                             ▼             |
|  [ Custom Gesture     ]      [ Assistive Chatbot  ]      [ SQLite / SQLAlchemy  ] |
|  [ Personalized Match ]      [ Engine & Presets   ]      [ ORM Persistence Layer] |
+---------┼─────────────────────────────┼─────────────────────────────┼-------------+
          │                             │                             │
          ▼                             ▼                             ▼
+-----------------------------------------------------------------------------------+
|                               OUTPUT PRESENTATION                                 |
|                                                                                   |
|   [ Multilingual Speech Synthesis ]        [ SignRenderer: ISL Visual Avatar ]   |
|   (Browser Speech API / pyttsx3)           (Kinetic Skeletal Gesture Stepper)     |
+-----------------------------------------------------------------------------------+
```

## Key Components

1. **Vision Landmark Extractor**: Real-time extraction of 21 hand landmarks ($x, y, z$) with wrist origin normalization and palm-scale invariant bounds.
2. **Feature Extractor**: Computes 93-dimensional feature vectors containing 63 normalized coordinates, 15 inter-finger joint bending angles, and 15 fingertip pairwise Euclidean distances.
3. **Classification Ensemble**:
   - Geometric heuristic classifier for instant rule-based precision.
   - Machine learning classifier (Random Forest / MLP) trained on ISL feature sets.
   - Dynamic sequence LSTM for trajectory tracking across 15–30 frame windows.
   - Custom user gesture centroid similarity matcher for personalized vocabulary.
4. **Debouncing & Temporal Smoothing**: Sliding window voting buffer over 5 frames with configurable confidence thresholds to prevent rapid output flickering.
5. **SignRenderer Abstraction**: Modular component rendering 3D avatar animations, kinetic gestures, and step-by-step fingerspelling sequences.
