export type Language = 'en' | 'hi' | 'bn';

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_guest: boolean;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LandmarkPoint {
  x: number;
  y: number;
  z?: number;
}

export interface DualHandData {
  left_hand: LandmarkPoint[] | null;
  right_hand: LandmarkPoint[] | null;
  num_hands: number;
}

export interface Gesture {
  id: number;
  name: string;
  category: string;
  is_dynamic: boolean;
  description?: string;
  image_url?: string;
  video_url?: string;
  animation_data?: any;
  text_en: string;
  text_hi: string;
  text_bn: string;
  is_active: boolean;
}

export interface PredictionResult {
  gesture: string;
  confidence: number;
  text_en: string;
  text_hi: string;
  text_bn: string;
  category?: string;
  is_dynamic?: boolean;
  status: 'success' | 'low_confidence' | 'no_hand' | 'error';
  message?: string;
  alternatives?: Array<{ gesture: string; confidence: number }>;
  num_hands?: number;
  left_detected?: boolean;
  right_detected?: boolean;
  recognition_mode?: string;
  sequence_len?: number;
  state_machine_state?: string;
  is_new_confirmed_output?: boolean;
  model_status?: string;
  fps?: number;
  latency_ms?: number;
  timestamp?: number;
}

export interface ISLTokenGesture {
  token: string;
  type: 'word' | 'fingerspell';
  label: string;
  duration_ms: number;
  description: string;
}

export interface TextToSignResponse {
  normalized_text: string;
  source_language: string;
  detected_language: string;
  isl_tokens: string[];
  gestures: ISLTokenGesture[];
  sign_sequence_description: string;
}

export interface TranslationRecord {
  id?: number;
  source_type: string;
  target_type: string;
  source_language: string;
  target_language: string;
  source_content: string;
  target_content: string;
  confidence?: number;
  created_at?: string;
}

export interface QuizOption {
  id: string;
  label: string;
  image_url?: string;
  gesture_name?: string;
}

export interface Quiz {
  id: number;
  lesson_id?: number;
  quiz_type: 'sign_to_word' | 'word_to_sign' | 'camera_practice';
  prompt_text: string;
  prompt_media?: string;
  target_gesture: string;
  options?: QuizOption[];
  points: number;
}

export interface Lesson {
  id: number;
  title: string;
  category: string;
  level: string;
  description?: string;
  order: number;
  xp_reward: number;
  signs_data: Array<{
    name: string;
    label: string;
    meaning: string;
    tips: string;
    image_url?: string;
  }>;
  quizzes?: Quiz[];
}

export interface UserProgress {
  total_xp: number;
  level: number;
  completed_lessons_count: number;
  completed_quizzes_count: number;
  signs_learned: number;
  practice_minutes: number;
  current_streak: number;
  longest_streak: number;
}

export interface CustomGesture {
  id: number;
  name: string;
  description?: string;
  text_en?: string;
  text_hi?: string;
  text_bn?: string;
  is_trained: boolean;
  is_active: boolean;
  samples_count: number;
  accuracy_score?: number;
  created_at: string;
}

export interface ChatMessage {
  id: number;
  sender: 'user' | 'assistant';
  text_content: string;
  language: string;
  sign_sequence?: ISLTokenGesture[];
  timestamp: string;
}

export interface AnalyticsData {
  total_translations: number;
  recognition_accuracy: number;
  signs_learned: number;
  current_streak: number;
  daily_activity: Array<{
    day: string;
    translations: number;
    practice_mins: number;
    accuracy: number;
  }>;
  sign_distribution: Array<{
    name: string;
    count: number;
    percentage: number;
  }>;
  model_metrics: {
    model_name: string;
    version: string;
    avg_latency_ms: number;
    avg_fps: number;
    top_1_accuracy: number;
    top_3_accuracy: number;
    low_confidence_rate: number;
    device: string;
  };
}

export interface ModelStatus {
  active_model: string;
  model_version: string;
  confidence_threshold: number;
  supported_gestures_count: number;
  dataset_samples_count: number;
  model_type: string;
  is_demo_model: boolean;
  last_trained: string;
  hardware_accelerator: string;
}

type float = number;
