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
export type TranscriptionCallback = (type: 'user' | 'system' | 'refresh', text: string) => void;

export class VoiceControlService {
  private recognition: SpeechRecognition | null = null;
  private isListening = false;
  private isDictationMode = false;
  private currentUtterance: SpeechSynthesisUtterance | null = null;
  private commandCallback: VoiceCommandCallback | null = null;
  private dictationCallback: DictationCallback | null = null;
  private isSpeaking = false;
  private commandCallbacks: Set<VoiceCommandCallback> = new Set();
  private transcriptionCallbacks: Set<TranscriptionCallback> = new Set();
  private hasUserInteracted = false;
  private lastSpeakTime = 0;
  private speakDebounceTimer: ReturnType<typeof setTimeout> | null = null;

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
        const rawTranscript = event.results[resultIndex][0].transcript.trim();
        const transcript = rawTranscript.toLowerCase();

        // Emit user transcription event (with original casing)
        this.emitTranscription('user', rawTranscript);

        console.log(`[VoiceControl] Recognition result received:`, {
          transcript,
          isDictationMode: this.isDictationMode,
          isListening: this.isListening,
          resultIndex,
          totalResults: event.results.length
        });

        if (this.isDictationMode) {
          // In dictation mode, check for "start task" command first (with fuzzy matching)
          if (this.fuzzyMatch(transcript, [
            "start task",
            "start desk",
            "start ask",
            "start tusk",
            "star task",
            "star desk",
            "stuck task",
            "stuck desk",
            "stat task",
            "stat desk",
            "start a task",
            "start task status",
            "stardusk",
            "status",
            "begin task",
            "begin desk",
            "begin ask",
            "begin tusk",
            "be gin task",
            "be in task"
          ])) {
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
          
          // Check for "refresh" command in dictation mode to break out of loops
          if (this.fuzzyMatch(transcript, [
            "refresh",
            "re fresh",
            "refresh recognition",
            "restart",
            "re start",
            "restart recognition",
            "reset",
            "re set",
            "reset recognition"
          ])) {
            console.log(`[VoiceControl] Detected "refresh" command in dictation mode, restarting recognition`);
            this.emitTranscription('refresh', 'Refreshing voice recognition...');
            this.restartRecognition();
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
        const errorDetails = {
          error: event.error,
          message: event.message,
          isListening: this.isListening,
          isDictationMode: this.isDictationMode
        };
        console.error(`[VoiceControl] Speech recognition error:`, errorDetails);
        
        if (event.error === "not-allowed") {
          console.error("[VoiceControl] Microphone permission denied");
          this.isListening = false; // Stop trying if permission denied
        } else if (event.error === "no-speech") {
          // This is normal - just means no speech detected, don't log as error
          return;
        } else if (event.error === "aborted") {
          // Recognition was aborted (probably by us) - this is expected
          return;
        } else if (event.error === "network") {
          console.error("[VoiceControl] Network error in speech recognition");
          // Don't auto-restart on network errors - wait a bit
          this.isListening = false;
          setTimeout(() => {
            if (!this.isDictationMode && this.recognition) {
              try {
                this.isListening = true;
                this.recognition.start();
              } catch (e) {
                console.error("[VoiceControl] Failed to restart after network error:", e);
              }
            }
          }, 2000); // Wait 2 seconds before retrying
        }
      };

      this.recognition.onend = () => {
        console.log(`[VoiceControl] Recognition ended`, {
          isListening: this.isListening,
          isDictationMode: this.isDictationMode,
          willRestart: this.isListening && !this.isDictationMode
        });
        // Auto-restart logic:
        // - Command mode: auto-restart if isListening is true
        // - Dictation mode: auto-restart if isListening is true (startDictation also handles this)
        // - Don't restart if isListening is false (we're stopping)
        if (this.isListening && this.recognition) {
          setTimeout(() => {
            // Double-check state before restarting (might have changed during timeout)
            if (this.isListening && this.recognition) {
              try {
                const mode = this.isDictationMode ? 'dictation' : 'command';
                console.log(`[VoiceControl] Auto-restarting recognition (${mode} mode)`);
                this.recognition.start();
              } catch (e) {
                // If it's already started, that's fine - ignore InvalidStateError
                if (e instanceof Error && e.name !== 'InvalidStateError') {
                  const mode = this.isDictationMode ? 'dictation' : 'command';
                  console.error(`[VoiceControl] Failed to restart recognition (${mode} mode):`, e);
                  // If restart fails with certain errors, stop trying to prevent infinite loops
                  if (e.name === 'NotAllowedError' || e.name === 'AbortError') {
                    console.warn(`[VoiceControl] Stopping recognition due to ${e.name}`);
                    this.isListening = false;
                  }
                }
              }
            }
          }, 100); // Reduced delay for faster response
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
    const lowerTranscript = transcript.toLowerCase().trim();
    
    for (const pattern of patterns) {
      const lowerPattern = pattern.toLowerCase().trim();
      
      // Exact match
      if (lowerTranscript === lowerPattern || lowerTranscript.includes(lowerPattern)) {
        return true;
      }
      
      // Check if transcript contains the pattern (even with extra words)
      if (lowerTranscript.includes(lowerPattern)) {
        return true;
      }
      
      // Check if pattern contains the transcript (for partial matches)
      if (lowerPattern.includes(lowerTranscript)) {
        return true;
      }
      
      // Word-by-word fuzzy matching for common misrecognitions
      const patternWords = lowerPattern.split(/\s+/);
      const transcriptWords = lowerTranscript.split(/\s+/);
      
      // Check if all pattern words have matches in transcript (allowing for extra words)
      let matchedWords = 0;
      for (const patternWord of patternWords) {
        for (const transcriptWord of transcriptWords) {
          // Exact word match
          if (patternWord === transcriptWord) {
            matchedWords++;
            break;
          }
          
          // Check common misrecognitions
          const misrecognitions: Record<string, string[]> = {
            "scene": ["seen", "sean", "see", "sea", "sin"],
            "description": ["discription", "desk ription"],
            "camera": ["camra", "cam era", "camer"],
            "on": ["own", "an"],
            "off": ["of"],
            "task": ["desk", "ask", "tusk", "tax", "podcast", "test", "has"],
            "start": ["star", "stuck", "stat", "stardusk", "status"],
            "begin": ["be gin", "be in", "be gone", "begin"],
            "stop": ["stap", "stopp", "stob"],
            "recording": ["record", "record in", "record ing"],
            "enter": ["inner"],
            "input": ["in put", "inpoot", "in putt", "in the", "importance"],
            "guide": ["guy", "good", "guyed"],
            "yes": ["yeah", "yep", "yea", "yas"],
            "no": ["know", "now", "nope"],
            "refresh": ["re fresh", "refreshed", "refresh it", "fresh"],
            "restart": ["re start", "restarted", "restart it", "start"],
            "reset": ["re set", "resetted", "reset it", "set"]
          };
          
          if (misrecognitions[patternWord]) {
            if (misrecognitions[patternWord].some(mis => transcriptWord.includes(mis) || mis.includes(transcriptWord))) {
              matchedWords++;
              break;
            }
          }
          
          // Check if words are similar (one contains the other)
          if (patternWord.includes(transcriptWord) || transcriptWord.includes(patternWord)) {
            matchedWords++;
            break;
          }
        }
      }
      
      // If most words match (70% threshold), consider it a match
      if (matchedWords >= Math.ceil(patternWords.length * 0.7)) {
        return true;
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
    if (this.fuzzyMatch(transcript, [
      "activity guide",
      "activity guy",
      "activity good",
      "act of tea guide",
      "act of t guide"
    ])) {
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

    if (this.fuzzyMatch(transcript, [
      "scene description",
      "seen description",
      "sean description",
      "see description",
      "sea description",
      "scene discription",
      "seen discription",
      "sin description",
      "scene desk ription"
    ])) {
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
    if (this.fuzzyMatch(transcript, [
      "turn on camera",
      "start camera",
      "camera on",
      "camera own",
      "camera an",
      "camra on",
      "cam era on",
      "turn on camra",
      "start camra",
      "turn own camera",
      "turn an camera",
      "come on",
      "come on camera"
    ])) {
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

    if (this.fuzzyMatch(transcript, [
      "turn off camera",
      "stop camera",
      "camera off",
      "camera of",
      "camra off",
      "camra of",
      "cam era off",
      "turn of camera",
      "turn off camra",
      "turn of camra",
      "stop camra"
    ])) {
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
    if (this.fuzzyMatch(transcript, [
      "enter task",
      "input task",
      "enter desk",
      "input desk",
      "enter ask",
      "input ask",
      "enter tusk",
      "input tusk",
      "inner task",
      "in put task",
      "enter tax",
      "input tax",
      "in the task",
      "in podcast",
      "importance",
      "input test",
      "input has"
    ])) {
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

    if (this.fuzzyMatch(transcript, [
      "start task",
      "start desk",
      "start ask",
      "start tusk",
      "star task",
      "star desk",
      "stuck task",
      "stuck desk",
      "stat task",
      "stat desk",
      "start a task",
      "start task status",
      "stardusk",
      "status",
      "begin task",
      "begin desk",
      "begin ask",
      "begin tusk",
      "be gin task",
      "be in task"
    ])) {
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
    if (this.fuzzyMatch(transcript, [
      "start recording",
      "star recording",
      "start record",
      "start record in",
      "star record",
      "stuck recording",
      "stat recording"
    ])) {
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

    if (this.fuzzyMatch(transcript, [
      "stop recording",
      "stap recording",
      "stop record",
      "stap record",
      "stopp recording",
      "stob recording"
    ])) {
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

    // Confirmation commands (with fuzzy matching)
    if (this.fuzzyMatch(transcript, ["yes", "yeah", "yep", "yea", "yas"])) {
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

    if (this.fuzzyMatch(transcript, ["no", "know", "now", "nope"])) {
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

    // Refresh command - restart speech recognition
    if (this.fuzzyMatch(transcript, [
      "refresh",
      "re fresh",
      "refresh recognition",
      "restart",
      "re start",
      "restart recognition",
      "reset",
      "re set",
      "reset recognition"
    ])) {
      console.log(`[VoiceControl] Matched command: refresh - restarting speech recognition`);
      this.emitTranscription('refresh', 'Refreshing voice recognition...');
      this.restartRecognition();
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

  // Register a transcription callback (for UI display)
  registerTranscriptionCallback(callback: TranscriptionCallback): () => void {
    console.log(`[VoiceControl] Registering transcription callback. Total callbacks: ${this.transcriptionCallbacks.size + 1}`);
    this.transcriptionCallbacks.add(callback);
    // Return unregister function
    return () => {
      console.log(`[VoiceControl] Unregistering transcription callback. Total callbacks: ${this.transcriptionCallbacks.size - 1}`);
      this.transcriptionCallbacks.delete(callback);
    };
  }

  // Emit transcription event to all registered callbacks
  private emitTranscription(type: 'user' | 'system' | 'refresh', text: string): void {
    this.transcriptionCallbacks.forEach(callback => {
      try {
        callback(type, text);
      } catch (error) {
        console.error(`[VoiceControl] Error in transcription callback:`, error);
      }
    });
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

    // Set dictation mode FIRST to prevent auto-restart in onend handler
    this.dictationCallback = onDictation;
    this.isDictationMode = true;

    // Stop current listening if active - wait for it to fully stop
    if (this.isListening) {
      console.log(`[VoiceControl] Stopping current recognition before starting dictation`);
      this.isListening = false; // Mark as not listening
      try {
        this.recognition.stop();
        this.recognition.abort(); // Force abort to ensure it stops
      } catch (e) {
        console.warn("[VoiceControl] Error stopping recognition:", e);
      }
    }

    // Wait for recognition to fully stop before restarting in dictation mode
    const startDictationRecognition = () => {
      if (!this.recognition || !this.isDictationMode) {
        console.warn(`[VoiceControl] Cannot start dictation - recognition or mode changed`);
        return;
      }

      try {
        this.recognition.start();
        this.isListening = true;
        console.log(`[VoiceControl] Dictation recognition started`);
      } catch (error: any) {
        if (error?.name === 'InvalidStateError') {
          // Recognition is already running - that's fine, we're in dictation mode now
          console.log("[VoiceControl] Recognition already running, continuing with dictation mode");
          this.isListening = true;
        } else {
          console.error("[VoiceControl] Failed to start dictation:", error);
          this.isListening = false;
          this.isDictationMode = false;
        }
      }
    };

    // If recognition was already stopped, start immediately for faster response
    // Otherwise wait for it to stop (onend handler will fire)
    if (!this.isListening) {
      // Recognition is already stopped, start immediately
      startDictationRecognition();
    } else {
      // Wait for recognition to fully stop (onend will fire)
      // The onend handler will see isDictationMode=true and handle restart
      // But we also start it manually after a short delay as backup
      setTimeout(startDictationRecognition, 200); // Reduced delay for faster response
    }
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

  restartRecognition(): void {
    console.log(`[VoiceControl] Restarting speech recognition`, {
      wasListening: this.isListening,
      wasInDictationMode: this.isDictationMode,
      hasCommandCallback: !!this.commandCallback,
      hasDictationCallback: !!this.dictationCallback
    });

    // Store current state
    const wasInDictation = this.isDictationMode;
    const savedDictationCallback = this.dictationCallback;
    const savedCommandCallback = this.commandCallback;

    // Stop current recognition
    this.isListening = false;
    if (this.recognition) {
      try {
        this.recognition.stop();
        this.recognition.abort();
      } catch (e) {
        // Ignore errors when stopping
      }
    }

    // Audio cue: Voice input refreshed
    this.markUserInteracted();
    this.speakText("Voice input refreshed!", false);

    // Wait a moment for recognition to fully stop, then restart
    setTimeout(() => {
      if (!this.recognition) {
        console.warn(`[VoiceControl] Cannot restart - recognition not initialized`);
        return;
      }

      // Restart in the same mode it was in before
      if (wasInDictation && savedDictationCallback) {
        console.log(`[VoiceControl] Restarting in dictation mode`);
        this.isDictationMode = true;
        this.dictationCallback = savedDictationCallback;
        this.isListening = true;
        try {
          this.recognition.start();
          console.log(`[VoiceControl] Dictation recognition restarted successfully`);
        } catch (error) {
          console.error(`[VoiceControl] Failed to restart dictation:`, error);
          this.isListening = false;
          this.isDictationMode = false;
        }
      } else if (savedCommandCallback || this.commandCallbacks.size > 0) {
        console.log(`[VoiceControl] Restarting in command mode`);
        this.isDictationMode = false;
        this.dictationCallback = null;
        this.isListening = true;
        try {
          this.recognition.start();
          console.log(`[VoiceControl] Command recognition restarted successfully`);
        } catch (error) {
          console.error(`[VoiceControl] Failed to restart command recognition:`, error);
          this.isListening = false;
        }
      } else {
        console.log(`[VoiceControl] No callbacks registered - not restarting`);
      }
    }, 300); // Wait 300ms for recognition to fully stop
  }

  markUserInteracted(): void {
    this.hasUserInteracted = true;
  }

  async speakText(text: string, interrupt: boolean = true): Promise<void> {
    // Check if SpeechSynthesis is available
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      console.warn("SpeechSynthesis not supported in this browser");
      return;
    }

    if (!text || text.trim() === "") {
      console.log("[VoiceControl] speakText: Empty text, skipping");
      return;
    }

    // Don't try to play audio if user hasn't interacted yet
    // This prevents autoplay restrictions - user must enable voice-only mode first
    if (!this.hasUserInteracted) {
      console.log("[VoiceControl] speakText: User hasn't interacted yet, skipping:", text.substring(0, 50));
      return;
    }

    // Debounce rapid TTS calls to prevent overwhelming the system
    // If called within 500ms of last call, cancel previous and schedule new one
    const now = Date.now();
    if (this.speakDebounceTimer) {
      clearTimeout(this.speakDebounceTimer);
      this.speakDebounceTimer = null;
    }

    // If we're already speaking and this is an interrupt, cancel immediately
    if (interrupt && this.isSpeaking) {
      window.speechSynthesis.cancel();
      this.isSpeaking = false;
      this.currentUtterance = null;
    }

    // Debounce: if called too soon after last speak, wait a bit
    const timeSinceLastSpeak = now - this.lastSpeakTime;
    const DEBOUNCE_MS = 300; // Minimum time between TTS calls

    if (timeSinceLastSpeak < DEBOUNCE_MS && !interrupt) {
      // Schedule to speak after debounce period
      this.speakDebounceTimer = setTimeout(() => {
        this._doSpeak(text, interrupt);
        this.speakDebounceTimer = null;
      }, DEBOUNCE_MS - timeSinceLastSpeak);
      return;
    }

    // Speak immediately
    this._doSpeak(text, interrupt);
  }

  private _doSpeak(text: string, interrupt: boolean): void {
    console.log("[VoiceControl] speakText: Speaking text:", text.substring(0, 100));
    this.lastSpeakTime = Date.now();

    // Cancel any ongoing speech if interrupt is true
    if (interrupt) {
      window.speechSynthesis.cancel();
      this.isSpeaking = false;
      this.currentUtterance = null;
    }

    try {
      // Create a new utterance
      const utterance = new SpeechSynthesisUtterance(text.trim());
      
      // Configure voice settings
      utterance.rate = 1.0; // Normal speed
      utterance.pitch = 1.0; // Normal pitch
      utterance.volume = 1.0; // Full volume

      // Set up event handlers
      utterance.onstart = () => {
        this.isSpeaking = true;
        this.currentUtterance = utterance;
        // Emit system transcription event
        this.emitTranscription('system', text.trim());
      };

      utterance.onend = () => {
        this.isSpeaking = false;
        // Only clear if this is still the current utterance
        if (this.currentUtterance === utterance) {
          this.currentUtterance = null;
        }
      };

      utterance.onerror = (event) => {
        // Filter out expected errors (interrupted/canceled are normal when interrupting)
        const error = event.error;
        if (error === 'interrupted' || error === 'canceled') {
          // These are expected when interrupting speech - don't log as errors
          this.isSpeaking = false;
          if (this.currentUtterance === utterance) {
            this.currentUtterance = null;
          }
          return;
        }
        
        // Log only unexpected errors
        console.error("SpeechSynthesis error:", error);
        this.isSpeaking = false;
        if (this.currentUtterance === utterance) {
          this.currentUtterance = null;
        }
      };

      // Store reference and speak
      this.currentUtterance = utterance;
      window.speechSynthesis.speak(utterance);
    } catch (error) {
      console.error("Error speaking text:", error);
      this.isSpeaking = false;
      this.currentUtterance = null;
    }
  }

  stopSpeaking(): void {
    // Clear any pending debounced speech
    if (this.speakDebounceTimer) {
      clearTimeout(this.speakDebounceTimer);
      this.speakDebounceTimer = null;
    }
    
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      this.isSpeaking = false;
      this.currentUtterance = null;
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
    this.transcriptionCallbacks.clear();
    // Clear debounce timer
    if (this.speakDebounceTimer) {
      clearTimeout(this.speakDebounceTimer);
      this.speakDebounceTimer = null;
    }
    // Ensure SpeechSynthesis is fully stopped
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
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

