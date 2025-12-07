/**
 * Voice Control Service - Handles voice-only mode commands
 * Uses Web Speech API for speech recognition
 */

// Web Speech API type definitions
interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any) | null;
  onend: ((this: SpeechRecognition, ev: Event) => any) | null;
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
  isFinal: boolean;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

declare global {
  interface Window {
    SpeechRecognition: {
      new (): SpeechRecognition;
    };
    webkitSpeechRecognition: {
      new (): SpeechRecognition;
    };
  }
}

export type VoiceCommandCallback = (command: string, transcript: string) => void;
export type DictationCallback = (text: string) => void;

export class VoiceControlService {
  private recognition: SpeechRecognition | null = null;
  private isListening = false;
  private isDictationMode = false;
  private currentAudio: HTMLAudioElement | null = null;
  private commandCallback: VoiceCommandCallback | null = null;
  private dictationCallback: DictationCallback | null = null;
  private ttsQueue: string[] = [];
  private isSpeaking = false;
  private commandCallbacks: Set<VoiceCommandCallback> = new Set();
  private hasUserInteracted = false;

  constructor() {
    this.initializeRecognition();
  }

  private initializeRecognition(): boolean {
    const SpeechRecognitionClass =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognitionClass) {
      console.warn("Web Speech API not supported in this browser");
      return false;
    }

    try {
      this.recognition = new SpeechRecognitionClass();
      this.recognition.continuous = true;
      this.recognition.interimResults = false;
      this.recognition.lang = "en-US";

      this.recognition.onresult = (event: SpeechRecognitionEvent) => {
        // Get the most recent result
        const resultIndex = event.resultIndex;
        const transcript = event.results[resultIndex][0].transcript
          .trim()
          .toLowerCase();

        if (this.isDictationMode) {
          // In dictation mode, check for "start task" command first
          if (transcript.includes("start task")) {
            // Exit dictation mode
            this.isDictationMode = false;
            const savedDictationCallback = this.dictationCallback;
            this.dictationCallback = null;
            
            // Stop current recognition
            try {
              this.recognition.stop();
            } catch (e) {
              // Ignore
            }
            
            // Trigger all command callbacks
            const callbacks = Array.from(this.commandCallbacks);
            if (this.commandCallback) {
              callbacks.push(this.commandCallback);
            }
            callbacks.forEach(cb => cb("start_task", transcript));
            
            // Restart command listening after a delay
            setTimeout(() => {
              if (this.isListening && !this.isDictationMode && this.recognition) {
                try {
                  this.recognition.start();
                } catch (e) {
                  // Might already be starting, ignore
                }
              }
            }, 300);
            return;
          }
          
          // Otherwise, just pass the text as dictation
          if (this.dictationCallback) {
            this.dictationCallback(transcript);
          }
        } else {
          // Command mode - process commands
          this.processCommand(transcript);
        }
      };

      this.recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error("Speech recognition error:", event.error);
        if (event.error === "not-allowed") {
          console.error("Microphone permission denied");
        }
      };

      this.recognition.onend = () => {
        // Auto-restart if we're supposed to be listening
        if (this.isListening && !this.isDictationMode) {
          setTimeout(() => {
            if (this.isListening && this.recognition) {
              try {
                this.recognition.start();
              } catch (e) {
                console.error("Failed to restart recognition:", e);
              }
            }
          }, 100);
        }
      };

      return true;
    } catch (error) {
      console.error("Failed to initialize speech recognition:", error);
      return false;
    }
  }

  private processCommand(transcript: string): void {
    // Call all registered command callbacks
    const callbacks = Array.from(this.commandCallbacks);
    if (callbacks.length === 0 && this.commandCallback) {
      callbacks.push(this.commandCallback);
    }

    // Reserved keywords for mode switching
    if (transcript.includes("activity guide")) {
      callbacks.forEach(cb => cb("switch_mode", "activity guide"));
      return;
    }

    if (transcript.includes("scene description")) {
      callbacks.forEach(cb => cb("switch_mode", "scene description"));
      return;
    }

    // Activity Guide commands
    if (transcript.includes("turn on camera") || transcript.includes("start camera")) {
      callbacks.forEach(cb => cb("camera_on", transcript));
      return;
    }

    if (transcript.includes("turn off camera") || transcript.includes("stop camera")) {
      callbacks.forEach(cb => cb("camera_off", transcript));
      return;
    }

    if (transcript.includes("enter task")) {
      callbacks.forEach(cb => cb("enter_task", transcript));
      return;
    }

    if (transcript.includes("start task")) {
      callbacks.forEach(cb => cb("start_task", transcript));
      return;
    }

    // Confirmation commands
    if (transcript === "yes" || transcript.includes("yes")) {
      callbacks.forEach(cb => cb("yes", transcript));
      return;
    }

    if (transcript === "no" || transcript.includes("no")) {
      callbacks.forEach(cb => cb("no", transcript));
      return;
    }
  }

  // Register a command callback (allows multiple components to listen)
  registerCommandCallback(callback: VoiceCommandCallback): () => void {
    this.commandCallbacks.add(callback);
    // Return unregister function
    return () => {
      this.commandCallbacks.delete(callback);
    };
  }

  startListening(
    onCommand?: VoiceCommandCallback,
    onDictation?: DictationCallback
  ): boolean {
    if (!this.recognition) {
      console.error("Speech recognition not initialized");
      return false;
    }

    // Register callback if provided
    if (onCommand) {
      this.commandCallback = onCommand;
      this.commandCallbacks.add(onCommand);
    }
    this.dictationCallback = onDictation || null;

    // If already listening, just register the callback and return
    if (this.isListening && !this.isDictationMode) {
      return true;
    }

    // Stop any existing recognition first
    if (this.isListening) {
      try {
        this.recognition.stop();
      } catch (e) {
        // Ignore errors when stopping
      }
      // Wait for it to fully stop before restarting
      setTimeout(() => {
        this.isListening = true;
        this.isDictationMode = false;
        try {
          if (this.recognition) {
            this.recognition.start();
          }
        } catch (error) {
          console.error("Failed to restart recognition:", error);
          this.isListening = false;
        }
      }, 300);
      return true;
    }

    this.isListening = true;
    this.isDictationMode = false;

    try {
      this.recognition.start();
      return true;
    } catch (error) {
      // Check if it's already started (common error)
      if (error instanceof Error && error.name === 'InvalidStateError') {
        // Recognition is already running, just mark as listening
        this.isListening = true;
        return true;
      }
      console.error("Failed to start recognition:", error);
      this.isListening = false;
      return false;
    }
  }

  startDictation(onDictation: DictationCallback): boolean {
    if (!this.recognition) {
      return false;
    }

    // Stop current listening if active
    if (this.isListening) {
      try {
        this.recognition.stop();
      } catch (e) {
        // Ignore
      }
    }

    this.dictationCallback = onDictation;
    this.isDictationMode = true;
    this.isListening = true;

    // Start dictation after a brief delay
    setTimeout(() => {
      if (this.recognition && this.isDictationMode) {
        try {
          this.recognition.start();
        } catch (error) {
          console.error("Failed to start dictation:", error);
          this.isListening = false;
          this.isDictationMode = false;
        }
      }
    }, 200);
    return true;
  }

  stopDictation(): void {
    const wasInDictation = this.isDictationMode;
    this.isDictationMode = false;
    this.dictationCallback = null;
    
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop();
      } catch (e) {
        // Ignore
      }
    }
    
    // Restart command listening if we have a command callback and were in dictation mode
    if (wasInDictation && this.commandCallback && this.isListening) {
      setTimeout(() => {
        if (this.isListening && !this.isDictationMode && this.recognition) {
          try {
            this.recognition.start();
          } catch (e) {
            // Ignore restart errors - might already be starting
          }
        }
      }, 300);
    }
  }

  stopListening(): void {
    this.isListening = false;
    this.isDictationMode = false;

    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (error) {
        // Ignore errors when stopping
      }
    }
  }

  markUserInteracted(): void {
    this.hasUserInteracted = true;
  }

  async speakText(text: string, interrupt: boolean = true): Promise<void> {
    if (interrupt && this.currentAudio) {
      // Stop current audio immediately
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
      this.isSpeaking = false;
    }

    if (!text || text.trim() === "") return;

    // Don't try to play audio if user hasn't interacted yet
    if (!this.hasUserInteracted) {
      console.log("Skipping audio playback - user hasn't interacted yet");
      return;
    }

    try {
      // Use the existing TTS API (same as apiClient.generateSpeech)
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const response = await fetch(
        `${apiBaseUrl}/api/v1/tts/generate?text=${encodeURIComponent(text)}`,
        { 
          method: "POST",
          headers: {
            'Content-Type': 'application/json',
          }
        }
      );

      if (!response.ok) {
        console.error("TTS API error:", response.statusText);
        return;
      }

      const data = await response.json();
      const audioBlob = new Blob(
        [
          Uint8Array.from(
            atob(data.audio_base64),
            (c) => c.charCodeAt(0)
          ),
        ],
        { type: "audio/mpeg" }
      );

      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      this.currentAudio = audio;
      this.isSpeaking = true;

      audio.onended = () => {
        this.isSpeaking = false;
        this.currentAudio = null;
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = () => {
        this.isSpeaking = false;
        this.currentAudio = null;
        URL.revokeObjectURL(audioUrl);
      };

      try {
        await audio.play();
      } catch (playError: any) {
        // Handle autoplay restrictions gracefully
        if (playError.name === 'NotAllowedError' || playError.name === 'NotSupportedError') {
          console.log("Audio autoplay blocked - user interaction required");
          this.hasUserInteracted = false; // Reset flag
        } else {
          throw playError;
        }
        this.isSpeaking = false;
        this.currentAudio = null;
        URL.revokeObjectURL(audioUrl);
      }
    } catch (error) {
      // Only log non-autoplay errors
      if (error instanceof Error && error.name !== 'NotAllowedError') {
        console.error("Error speaking text:", error);
      }
      this.isSpeaking = false;
      this.currentAudio = null;
    }
  }

  stopSpeaking(): void {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
      this.isSpeaking = false;
    }
  }

  isCurrentlySpeaking(): boolean {
    return this.isSpeaking;
  }

  isActive(): boolean {
    return this.isListening;
  }

  cleanup(): void {
    this.stopListening();
    this.stopSpeaking();
    this.commandCallback = null;
    this.dictationCallback = null;
    this.commandCallbacks.clear();
  }
}

// Singleton instance
let voiceControlInstance: VoiceControlService | null = null;

export function getVoiceControlService(): VoiceControlService {
  if (!voiceControlInstance) {
    voiceControlInstance = new VoiceControlService();
  }
  return voiceControlInstance;
}

