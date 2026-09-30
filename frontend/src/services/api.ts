import {
  AuthResponse,
  Gesture,
  PredictionResult,
  TextToSignResponse,
  TranslationRecord,
  Lesson,
  UserProgress,
  CustomGesture,
  ChatMessage,
  AnalyticsData,
  ModelStatus,
  Language
} from '../types';

const API_BASE = '/api';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('signbridge_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Auth
  login: (data: { email: string; password: string }) =>
    request<AuthResponse>('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  
  register: (data: { email: string; password: string; full_name?: string }) =>
    request<AuthResponse>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  
  guestLogin: () =>
    request<AuthResponse>('/auth/guest', { method: 'POST' }),

  // Gestures
  getGestures: (category?: string) =>
    request<Gesture[]>(`/gestures${category ? `?category=${category}` : ''}`),
  
  getGestureById: (id: number) =>
    request<Gesture>(`/gestures/${id}`),

  // Prediction
  predictLandmarks: (landmarks: Array<{ x: number; y: number; z?: number }>, handedness = 'Right', userId?: number) =>
    request<PredictionResult>('/predict/landmarks', {
      method: 'POST',
      body: JSON.stringify({ landmarks, handedness, user_id: userId }),
    }),

  predictDualHands: (leftLandmarks: Array<{ x: number; y: number; z?: number }> | null, rightLandmarks: Array<{ x: number; y: number; z?: number }> | null, mirrored = true, userId?: number) =>
    request<PredictionResult>('/predict/landmarks', {
      method: 'POST',
      body: JSON.stringify({
        left_hand_landmarks: leftLandmarks,
        right_hand_landmarks: rightLandmarks,
        mirrored_camera: mirrored,
        user_id: userId,
      }),
    }),

  // Translation
  translateText: (text: string, sourceLang: Language, targetLang: Language, userId?: number) =>
    request<{ source_text: string; translated_text: string; source_language: string; target_language: string; sign_tokens: string[] }>('/translate/text', {
      method: 'POST',
      body: JSON.stringify({ text, source_language: sourceLang, target_language: targetLang, user_id: userId }),
    }),

  textToSign: (text: string, language: Language = 'en', userId?: number) =>
    request<TextToSignResponse>('/translate/text-to-sign', {
      method: 'POST',
      body: JSON.stringify({ text, language, user_id: userId }),
    }),

  speechToSign: (transcript: string, language: Language = 'en') =>
    request<TextToSignResponse>('/speech/to-sign', {
      method: 'POST',
      body: JSON.stringify({ transcript, language }),
    }),

  // Chatbot
  sendChatMessage: (text: string, language: Language = 'en', sessionId?: number) =>
    request<ChatMessage>('/chat/send', {
      method: 'POST',
      body: JSON.stringify({ text, language, session_id: sessionId }),
    }),

  // Learning & Quizzes
  getLessons: () =>
    request<Lesson[]>('/learning/lessons'),
  
  getLessonDetail: (lessonId: number) =>
    request<Lesson>(`/learning/lessons/${lessonId}`),
  
  submitQuiz: (quizId: number, userAnswer: string) =>
    request<{
      quiz_id: number;
      is_correct: boolean;
      correct_answer: string;
      explanation?: string;
      score_earned: number;
      total_xp: number;
      current_streak: number;
    }>('/learning/quiz/submit', {
      method: 'POST',
      body: JSON.stringify({ quiz_id: quizId, user_answer: userAnswer }),
    }),

  getUserProgress: () =>
    request<UserProgress>('/learning/progress'),

  // Custom Gestures
  getCustomGestures: () =>
    request<CustomGesture[]>('/custom-gestures'),

  createCustomGesture: (data: { name: string; description?: string; text_en?: string; text_hi?: string; text_bn?: string }) =>
    request<CustomGesture>('/custom-gestures', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  uploadCustomSamples: (gestureId: number, samples: Array<Array<{ x: number; y: number; z?: number }>>) =>
    request<CustomGesture>(`/custom-gestures/${gestureId}/samples`, {
      method: 'POST',
      body: JSON.stringify({ samples }),
    }),

  trainCustomGesture: (gestureId: number) =>
    request<CustomGesture>(`/custom-gestures/${gestureId}/train`, {
      method: 'POST',
    }),

  deleteCustomGesture: (gestureId: number) =>
    request<{ status: string; id: number }>(`/custom-gestures/${gestureId}`, {
      method: 'DELETE',
    }),

  // Analytics & History
  getAnalytics: () =>
    request<AnalyticsData>('/analytics'),

  getHistory: (limit = 50) =>
    request<TranslationRecord[]>(`/analytics/history?limit=${limit}`),

  // Admin & Model Management
  getModelStatus: () =>
    request<ModelStatus>('/admin/model-status'),

  updateModelConfig: (data: { active_model: string; confidence_threshold: number }) =>
    request<{ status: string; active_model: string; confidence_threshold: number }>('/admin/model-config', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};
