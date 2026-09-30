# SignBridge AI API Documentation

## Base URL
- REST API: `http://localhost:8000/api`
- WebSocket: `ws://localhost:8000/ws/sign-recognition`

---

## Authentication Endpoints

### `POST /api/auth/register`
Register a new user account.
- **Request Body**: `{ "email": "user@example.com", "password": "secure_password", "full_name": "User Name" }`
- **Response**: `{ "access_token": "jwt...", "token_type": "bearer", "user": { ... } }`

### `POST /api/auth/login`
Authenticate with email and password.
- **Request Body**: `{ "email": "user@example.com", "password": "secure_password" }`
- **Response**: JWT access token and user profile.

### `POST /api/auth/guest`
Instant 1-click guest authentication session.

---

## Prediction & Inference Endpoints

### `POST /api/predict/landmarks`
Real-time prediction on 21 hand landmarks.
- **Request Body**:
  ```json
  {
    "landmarks": [
      {"x": 0.5, "y": 0.8, "z": 0.0},
      ... 21 landmark items
    ],
    "handedness": "Right",
    "user_id": 1,
    "use_custom_gestures": true
  }
  ```
- **Response**:
  ```json
  {
    "gesture": "HELLO",
    "confidence": 0.94,
    "text_en": "Hello",
    "text_hi": "नमस्ते / हैलो",
    "text_bn": "হ্যালো / নমস্কার",
    "category": "words",
    "is_dynamic": true,
    "status": "success",
    "fps": 30.0,
    "latency_ms": 12.4
  }
  ```

### `WebSocket /ws/sign-recognition`
Real-time bi-directional streaming endpoint for 30 FPS camera feeds.

---

## Translation & Speech Endpoints

### `POST /api/translate/text`
Multilingual translation across English, Hindi, and Bengali.

### `POST /api/translate/text-to-sign`
Normalizes natural sentences into ISL tokens and gesture playback sequences.

### `POST /api/speech/to-sign`
Converts voice transcriptions directly into ISL gesture sequences.

---

## Chatbot Endpoints

### `POST /api/chat/send`
Send a message to the assistive AI communication bot. Automatically receives text and mapped ISL sign sequences.

---

## Learning & Gamification Endpoints

### `GET /api/learning/lessons`
List all learning modules (Alphabets, Numbers, Words, Phrases).

### `POST /api/learning/quiz/submit`
Submit answers for multiple choice or live camera quizzes and earn XP/streak increments.

---

## Custom Gestures Endpoints

- `GET /api/custom-gestures`: List user's custom gestures
- `POST /api/custom-gestures`: Create new custom gesture entry
- `POST /api/custom-gestures/{id}/samples`: Upload landmark samples (20–50 samples)
- `POST /api/custom-gestures/{id}/train`: Train personalized classifier
- `DELETE /api/custom-gestures/{id}`: Delete custom gesture
