/**
 * API Client for AIris Backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export type TaskRequest = {
  goal: string;
  target_objects?: string[];
};

export type TaskResponse = {
  status: string;
  message: string;
  target_objects: string[];
  primary_target: string;
  stage: string;
};

export type FeedbackRequest = {
  confirmed: boolean;
  feedback_text?: string;
};

export type CameraStatus = {
  is_running: boolean;
  is_available: boolean;
};

export type ProcessFrameResponse = {
  frame: string;
  guidance?: {
    instruction: string;
    stage: string;
  };
  stage: string;
  instruction: string;
  detected_objects: Array<{ name: string; box: number[] }>;
  hand_detected: boolean;
  object_location?: number[];
  hand_location?: number[];
};

export type SceneDescriptionResponse = {
  frame: string;
  description?: string;
  summary?: string;
  safety_alert: boolean;
  is_recording: boolean;
  stats?: {
    elapsed_seconds: number;
    descriptions_count: number;
    summaries_count: number;
    alerts_count: number;
    buffer_size: number;
    buffer_max: number;
    analysis_interval: number;
  };
  recent_observations?: string[];
};

export const apiClient = {
  // Camera endpoints
  async setCameraConfig(sourceType: 'webcam' | 'esp32', ipAddress?: string): Promise<void> {
    await client.post('/api/v1/camera/config', {
      source_type: sourceType,
      ip_address: ipAddress,
    });
  },

  async provisionESP32WiFi(ssid: string, password: string = ''): Promise<{ success: boolean; message: string }> {
    const response = await client.post('/api/v1/camera/esp32/provision-wifi', {
      ssid,
      password,
    });
    return response.data;
  },
  async startCamera(): Promise<void> {
    await client.post('/api/v1/camera/start');
  },

  async stopCamera(): Promise<void> {
    await client.post('/api/v1/camera/stop');
  },

  async getCameraStatus(): Promise<CameraStatus> {
    const response = await client.get('/api/v1/camera/status');
    return response.data;
  },

  async getCameraFrame(): Promise<string> {
    const response = await client.get('/api/v1/camera/frame', {
      responseType: 'blob',
    });
    return URL.createObjectURL(response.data);
  },

  // Activity Guide endpoints
  async startTask(request: TaskRequest): Promise<TaskResponse> {
    const response = await client.post('/api/v1/activity-guide/start-task', request);
    return response.data;
  },

  async processActivityFrame(): Promise<ProcessFrameResponse> {
    const response = await client.post('/api/v1/activity-guide/process-frame');
    return response.data;
  },

  async submitFeedback(request: FeedbackRequest): Promise<any> {
    const response = await client.post('/api/v1/activity-guide/feedback', request);
    return response.data;
  },

  async getActivityGuideStatus(): Promise<any> {
    const response = await client.get('/api/v1/activity-guide/status');
    return response.data;
  },

  async resetActivityGuide(): Promise<void> {
    await client.post('/api/v1/activity-guide/reset');
  },

  // Scene Description endpoints
  async startRecording(): Promise<any> {
    const response = await client.post('/api/v1/scene-description/start-recording');
    return response.data;
  },

  async stopRecording(): Promise<any> {
    const response = await client.post('/api/v1/scene-description/stop-recording');
    return response.data;
  },

  async processSceneFrame(): Promise<SceneDescriptionResponse> {
    const response = await client.post('/api/v1/scene-description/process-frame');
    return response.data;
  },

  async getRecordingLogs(): Promise<any[]> {
    const response = await client.get('/api/v1/scene-description/logs');
    return response.data.logs || [];
  },

  // TTS endpoints
  async generateSpeech(text: string): Promise<{ audio_base64: string; duration: number }> {
    const response = await client.post('/api/v1/tts/generate', null, {
      params: { text },
    });
    return response.data;
  },

  // STT endpoints
  async transcribeAudio(audioBase64: string, sampleRate: number = 16000): Promise<{ text: string; success: boolean }> {
    const response = await client.post('/api/v1/stt/transcribe-base64', {
      audio_base64: audioBase64,
      sample_rate: sampleRate,
    });
    return response.data;
  },

  // Email endpoints
  async getEmailStatus(): Promise<{
    configured: boolean;
    sender: string | null;
    recipient: string | null;
    cooldown_minutes: number;
    pending_events: number;
  }> {
    const response = await client.get('/api/v1/email/status');
    return response.data;
  },

  async getGuardianEmail(): Promise<{
    configured: boolean;
    recipient: string | null;
    sender_configured: boolean;
  }> {
    const response = await client.get('/api/v1/email/guardian');
    return response.data;
  },

  async setupGuardian(email: string, name?: string): Promise<{ status: string; message: string; recipient: string }> {
    const response = await client.post('/api/v1/email/setup-guardian', {
      email,
      name: name || 'Guardian',
    });
    return response.data;
  },

  async sendTestEmail(): Promise<{ status: string; message: string }> {
    const response = await client.post('/api/v1/email/test');
    return response.data;
  },

  async sendTestAlert(): Promise<{ status: string; message: string }> {
    const response = await client.post('/api/v1/email/test-alert');
    return response.data;
  },

  async sendTestDaily(): Promise<{ status: string; message: string }> {
    const response = await client.post('/api/v1/email/test-daily');
    return response.data;
  },

  async sendTestWeekly(): Promise<{ status: string; message: string }> {
    const response = await client.post('/api/v1/email/test-weekly');
    return response.data;
  },

  async sendRealDailySummary(): Promise<{ status: string; message: string }> {
    const response = await client.post('/api/v1/email/send-daily-summary');
    return response.data;
  },

  async sendRealWeeklyReport(): Promise<{ status: string; message: string }> {
    const response = await client.post('/api/v1/email/send-weekly-report');
    return response.data;
  },
};

