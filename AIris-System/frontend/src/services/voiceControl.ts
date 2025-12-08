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

        console.log(`[VoiceControl] Recognition result received:`, {
          transcript,
          isDictationMode: this.isDictationMode,
          isListening: this.isListening,
          resultIndex,
          totalResults: event.results.length
        });

        if (this.isDictationMode) {
          // In dictation mode, check for "start task" command first (with fuzzy matching)
          if (this.fuzzyMatch(transcript, ["start task", "start desk"])) {
            console.log(`[VoiceControl] Detected "start task" command in dictation mode, exiting dictation`);
            // Exit dictation mode
            this.isDictationMode = false;
            this.dictationCallback = null;
            
            // Stop current recognition
            this.isListening = false;
            if (this.recognition) {
              try {
                this.recognition.stop();
                this.recognition.abort();
              } catch (e) {
                // Ignore
              }
            }
            
            // Trigger all command callbacks (deduplicated)
            const callbacksSet = new Set<VoiceCommandCallback>();
            this.commandCallbacks.forEach(cb => callbacksSet.add(cb));
            if (this.commandCallback) {
              callbacksSet.add(this.commandCallback);
            }
            const callbacks = Array.from(callbacksSet);
            callbacks.forEach(cb => {
              try {
                cb("start_task", transcript);
              } catch (error) {
                console.error(`[VoiceControl] Error in start_task callback:`, error);
              }
            });
            
            // Restart command listening after a delay
            setTimeout(() => {
              if (!this.isDictationMode && this.recognition) {
                try {
                  this.isListening = true;
                  this.recognition.start();
                  console.log(`[VoiceControl] Restarted command listening after dictation`);
                } catch (e) {
                  // Might already be starting, ignore
                  if (e instanceof Error && e.name !== 'InvalidStateError') {
                    console.warn(`[VoiceControl] Error restarting after dictation:`, e);
                  }
                }
              }
            }, 500);
            return;
          }
          
          // Otherwise, just pass the text as dictation
          if (this.dictationCallback) {
            console.log(`[VoiceControl] Dictation callback triggered with: "${transcript}"`);
            this.dictationCallback(transcript);
          } else {
            console.warn(`[VoiceControl] Dictation mode active but no dictation callback registered`);
          }
        } else {
          // Command mode - process commands
          console.log(`[VoiceControl] Processing command from transcript: "${transcript}"`);
          this.processCommand(transcript);
        }
      };

      this.recognition.onstart = () => {
        console.log(`[VoiceControl] Recognition started`, {
          isDictationMode: this.isDictationMode,
          isListening: this.isListening,
          callbacksCount: this.commandCallbacks.size
        });
      };

      this.recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error(`[VoiceControl] Speech recognition error:`, {
          error: event.error,
          message: event.message,
          isListening: this.isListening,
          isDictationMode: this.isDictationMode
        });
        if (event.error === "not-allowed") {
          console.error("[VoiceControl] Microphone permission denied");
        }
      };

      this.recognition.onend = () => {
        console.log(`[VoiceControl] Recognition ended`, {
          isListening: this.isListening,
          isDictationMode: this.isDictationMode,
          willRestart: this.isListening && !this.isDictationMode
        });
        // Auto-restart if we're supposed to be listening
        if (this.isListening && !this.isDictationMode) {
          setTimeout(() => {
            if (this.isListening && this.recognition) {
              try {
                console.log(`[VoiceControl] Auto-restarting recognition`);
                this.recognition.start();
              } catch (e) {
                console.error("[VoiceControl] Failed to restart recognition:", e);
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

  // Helper function for fuzzy string matching (handles common misrecognitions)
  private fuzzyMatch(transcript: string, patterns: string[]): boolean {
    const lowerTranscript = transcript.toLowerCase();
    
    for (const pattern of patterns) {
      const lowerPattern = pattern.toLowerCase();
      // Exact match
      if (lowerTranscript === lowerPattern || lowerTranscript.includes(lowerPattern)) {
        return true;
      }
      
      // Fuzzy matching for common misrecognitions
      // "scene" vs "seen"
      if (lowerPattern.includes("scene") && (lowerTranscript.includes("seen") || lowerTranscript.includes("scene"))) {
        const rest = lowerPattern.replace("scene", "").trim();
        if (rest === "" || lowerTranscript.includes(rest)) {
          return true;
        }
      }
      
      // "off" vs "of"
      if (lowerPattern.includes(" off") && lowerTranscript.includes(" of")) {
        const before = lowerPattern.split(" off")[0];
        if (lowerTranscript.includes(before + " of")) {
          return true;
        }
      }
      
      // "task" vs "desk"
      if (lowerPattern.includes("task") && lowerTranscript.includes("desk")) {
        const before = lowerPattern.split("task")[0];
        if (lowerTranscript.includes(before + "desk")) {
          return true;
        }
      }
    }
    
    return false;
  }

  private processCommand(transcript: string): void {
    console.log(`[VoiceControl] processCommand called with transcript: "${transcript}"`);
    
    // Collect all callbacks - use a Set to avoid duplicates
    const callbacksSet = new Set<VoiceCommandCallback>();
    this.commandCallbacks.forEach(cb => callbacksSet.add(cb));
    if (this.commandCallback) {
      callbacksSet.add(this.commandCallback);
    }
    const callbacks = Array.from(callbacksSet);

    console.log(`[VoiceControl] Found ${callbacks.length} callbacks to notify`, {
      registeredCallbacks: this.commandCallbacks.size,
      hasMainCallback: !!this.commandCallback,
      uniqueCallbacks: callbacks.length
    });

    if (callbacks.length === 0) {
      console.warn(`[VoiceControl] No callbacks registered! Commands will not be processed.`);
      return;
    }

    // Reserved keywords for mode switching (with fuzzy matching)
    if (this.fuzzyMatch(transcript, ["activity guide"])) {
      console.log(`[VoiceControl] Matched command: switch_mode (activity guide)`);
      callbacks.forEach((cb, idx) => {
        console.log(`[VoiceControl] Calling callback ${idx + 1}/${callbacks.length}`);
        try {
          cb("switch_mode", "activity guide");
        } catch (error) {
          console.error(`[VoiceControl] Error in callback ${idx + 1}:`, error);
        }
      });
      return;
    }

    if (this.fuzzyMatch(transcript, ["scene description", "seen description"])) {
      console.log(`[VoiceControl] Matched command: switch_mode (scene description)`);
      callbacks.forEach((cb, idx) => {
        console.log(`[VoiceControl] Calling callback ${idx + 1}/${callbacks.length}`);
        try {
          cb("switch_mode", "scene description");
        } catch (error) {
          console.error(`[VoiceControl] Error in callback ${idx + 1}:`, error);
        }
      });
      return;
    }

    // Camera commands (with fuzzy matching)
    if (this.fuzzyMatch(transcript, ["turn on camera", "start camera", "camera on"])) {
      console.log(`[VoiceControl] Matched command: camera_on`);
      callbacks.forEach((cb, idx) => {
        console.log(`[VoiceControl] Calling callback ${idx + 1}/${callbacks.length} for camera_on`);
        try {
          cb("camera_on", transcript);
        } catch (error) {
          console.error(`[VoiceControl] Error in callback ${idx + 1}:`, error);
        }
      });
      return;
    }

    if (this.fuzzyMatch(transcript, ["turn off camera", "stop camera", "camera off", "camera of"])) {
      console.log(`[VoiceControl] Matched command: camera_off`);
      callbacks.forEach((cb, idx) => {
        console.log(`[VoiceControl] Calling callback ${idx + 1}/${callbacks.length} for camera_off`);
        try {
          cb("camera_off", transcript);
        } catch (error) {
          console.error(`[VoiceControl] Error in callback ${idx + 1}:`, error);
        }
      });
      return;
    }

    // Activity Guide commands (with fuzzy matching)
    if (this.fuzzyMatch(transcript, ["enter task", "input task", "enter desk", "input desk"])) {
      console.log(`[VoiceControl] Matched command: enter_task`);
      callbacks.forEach((cb, idx) => {
        console.log(`[VoiceControl] Calling callback ${idx + 1}/${callbacks.length} for enter_task`);
        try {
          cb("enter_task", transcript);
        } catch (error) {
          console.error(`[VoiceControl] Error in callback ${idx + 1}:`, error);
        }
      });
      return;
    }

    if (this.fuzzyMatch(transcript, ["start task", "start desk"])) {
      console.log(`[VoiceControl] Matched command: start_task`);
      callbacks.forEach((cb, idx) => {
        console.log(`[VoiceControl] Calling callback ${idx + 1}/${callbacks.length} for start_task`);
        try {
          cb("start_task", transcript);
        } catch (error) {
          console.error(`[VoiceControl] Error in callback ${idx + 1}:`, error);
        }
      });
      return;
    }

    // Scene Description commands
    if (this.fuzzyMatch(transcript, ["start recording"])) {
      console.log(`[VoiceControl] Matched command: start_recording`);
      callbacks.forEach((cb, idx) => {
        console.log(`[VoiceControl] Calling callback ${idx + 1}/${callbacks.length} for start_recording`);
        try {
          cb("start_recording", transcript);
        } catch (error) {
          console.error(`[VoiceControl] Error in callback ${idx + 1}:`, error);
        }
      });
      return;
    }

    if (this.fuzzyMatch(transcript, ["stop recording"])) {
      console.log(`[VoiceControl] Matched command: stop_recording`);
      callbacks.forEach((cb, idx) => {
        console.log(`[VoiceControl] Calling callback ${idx + 1}/${callbacks.length} for stop_recording`);
        try {
          cb("stop_recording", transcript);
        } catch (error) {
          console.error(`[VoiceControl] Error in callback ${idx + 1}:`, error);
        }
      });
      return;
    }

    // Confirmation commands
    if (transcript === "yes" || transcript.includes("yes")) {
      console.log(`[VoiceControl] Matched command: yes`);
      callbacks.forEach((cb, idx) => {
        console.log(`[VoiceControl] Calling callback ${idx + 1}/${callbacks.length} for yes`);
        try {
          cb("yes", transcript);
        } catch (error) {
          console.error(`[VoiceControl] Error in callback ${idx + 1}:`, error);
        }
      });
      return;
    }

    if (transcript === "no" || transcript.includes("no")) {
      console.log(`[VoiceControl] Matched command: no`);
      callbacks.forEach((cb, idx) => {
        console.log(`[VoiceControl] Calling callback ${idx + 1}/${callbacks.length} for no`);
        try {
          cb("no", transcript);
        } catch (error) {
          console.error(`[VoiceControl] Error in callback ${idx + 1}:`, error);
        }
      });
      return;
    }

    console.log(`[VoiceControl] No command matched for transcript: "${transcript}"`);
  }

  // Register a command callback (allows multiple components to listen)
  registerCommandCallback(callback: VoiceCommandCallback): () => void {
    console.log(`[VoiceControl] Registering command callback. Total callbacks: ${this.commandCallbacks.size + 1}`);
    this.commandCallbacks.add(callback);
    console.log(`[VoiceControl] Callback registered. Total callbacks now: ${this.commandCallbacks.size}`);
    // Return unregister function
    return () => {
      console.log(`[VoiceControl] Unregistering command callback. Total callbacks: ${this.commandCallbacks.size - 1}`);
      this.commandCallbacks.delete(callback);
    };
  }

  startListening(
    onCommand?: VoiceCommandCallback,
    onDictation?: DictationCallback
  ): boolean {
    console.log(`[VoiceControl] startListening called`, {
      hasRecognition: !!this.recognition,
      isListening: this.isListening,
      isDictationMode: this.isDictationMode,
      hasOnCommand: !!onCommand,
      hasOnDictation: !!onDictation,
      currentCallbacksCount: this.commandCallbacks.size
    });

    if (!this.recognition) {
      console.error("[VoiceControl] Speech recognition not initialized");
      return false;
    }

    // Register callback if provided - only add if not already in set
    if (onCommand) {
      this.commandCallback = onCommand;
      if (!this.commandCallbacks.has(onCommand)) {
        this.commandCallbacks.add(onCommand);
        console.log(`[VoiceControl] Main command callback registered. Total callbacks: ${this.commandCallbacks.size}`);
      } else {
        console.log(`[VoiceControl] Main command callback already registered, skipping duplicate`);
      }
    }
    this.dictationCallback = onDictation || null;

    // If already listening, just register the callback and return
    if (this.isListening && !this.isDictationMode) {
      console.log(`[VoiceControl] Already listening, callback registered. Not restarting.`);
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
      console.log(`[VoiceControl] Starting recognition...`);
      this.recognition.start();
      console.log(`[VoiceControl] Recognition start() called successfully`);
      return true;
    } catch (error) {
      // Check if it's already started (common error)
      if (error instanceof Error && error.name === 'InvalidStateError') {
        // Recognition is already running, just mark as listening
        console.log(`[VoiceControl] Recognition already running (InvalidStateError), marking as listening`);
        this.isListening = true;
        return true;
      }
      console.error("[VoiceControl] Failed to start recognition:", error);
      this.isListening = false;
      return false;
    }
  }

  startDictation(onDictation: DictationCallback): boolean {
    console.log(`[VoiceControl] startDictation called`, {
      hasRecognition: !!this.recognition,
      isListening: this.isListening,
      isDictationMode: this.isDictationMode
    });

    if (!this.recognition) {
      console.error("[VoiceControl] Cannot start dictation - recognition not initialized");
      return false;
    }

    // Stop current listening if active - wait for it to fully stop
    if (this.isListening) {
      console.log(`[VoiceControl] Stopping current recognition before starting dictation`);
      this.isListening = false; // Mark as not listening first
      try {
        this.recognition.stop();
        this.recognition.abort(); // Force abort to ensure it stops
      } catch (e) {
        console.warn("[VoiceControl] Error stopping recognition:", e);
      }
    }

    this.dictationCallback = onDictation;
    this.isDictationMode = true;

    // Wait longer for recognition to fully stop before restarting
    setTimeout(() => {
      if (this.recognition && this.isDictationMode) {
        try {
          console.log(`[VoiceControl] Starting dictation recognition...`);
          this.isListening = true;
          this.recognition.start();
          console.log(`[VoiceControl] Dictation recognition started`);
        } catch (error: any) {
          console.error("[VoiceControl] Failed to start dictation:", error);
          // If already started error, that's okay - it means recognition is running
          if (error?.name === 'InvalidStateError') {
            console.log("[VoiceControl] Recognition already running, continuing with dictation mode");
            this.isListening = true;
          } else {
            this.isListening = false;
            this.isDictationMode = false;
          }
        }
      } else {
        console.warn(`[VoiceControl] Cannot start dictation - recognition or mode changed`, {
          hasRecognition: !!this.recognition,
          isDictationMode: this.isDictationMode
        });
      }
    }, 500); // Increased delay to ensure recognition fully stops
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
    console.log(`[VoiceControl] stopListening called`, {
      wasListening: this.isListening,
      wasInDictationMode: this.isDictationMode,
      callbacksCount: this.commandCallbacks.size
    });
    this.isListening = false;
    this.isDictationMode = false;

    if (this.recognition) {
      try {
        this.recognition.stop();
        console.log(`[VoiceControl] Recognition stopped`);
      } catch (error) {
        console.warn(`[VoiceControl] Error stopping recognition:`, error);
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

