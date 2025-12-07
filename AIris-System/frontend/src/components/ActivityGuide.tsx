import { useState, useEffect, useRef, useCallback } from "react";
import {
  Volume2,
  CheckCircle,
  XCircle,
  Loader2,
  Mic,
  MicOff,
  Trash2,
} from "lucide-react";
import { apiClient, type TaskRequest } from "../services/api";
import { getVoiceControlService } from "../services/voiceControl";

// Web Speech API type definitions
interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onresult:
    | ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any)
    | null;
  onerror:
    | ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any)
    | null;
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

interface ActivityGuideProps {
  cameraOn: boolean;
  voiceOnlyMode?: boolean;
}

// Log entry with metadata
interface LogEntry {
  id: number;
  instruction: string;
  timestamp: Date;
  stage: string;
  type: "instruction" | "task_start" | "task_complete" | "feedback";
}

// Helper function to calculate text similarity (Jaccard similarity on words)
function calculateSimilarity(str1: string, str2: string): number {
  const words1 = new Set(
    str1
      .toLowerCase()
      .split(/\s+/)
      .filter((w) => w.length > 2)
  );
  const words2 = new Set(
    str2
      .toLowerCase()
      .split(/\s+/)
      .filter((w) => w.length > 2)
  );

  if (words1.size === 0 && words2.size === 0) return 1;
  if (words1.size === 0 || words2.size === 0) return 0;

  const intersection = new Set([...words1].filter((x) => words2.has(x)));
  const union = new Set([...words1, ...words2]);

  return intersection.size / union.size;
}

// Helper function to check if instruction is meaningfully different
function isSignificantlyDifferent(
  newInstruction: string,
  recentEntries: LogEntry[]
): boolean {
  if (recentEntries.length === 0) return true;

  // Compare against last 5 entries to catch repeated patterns
  const recentToCheck = recentEntries.slice(0, 5);

  for (const entry of recentToCheck) {
    // Exact match - definitely a duplicate
    if (entry.instruction === newInstruction) return false;

    // Check similarity
    const similarity = calculateSimilarity(entry.instruction, newInstruction);
    if (similarity > 0.75) return false;
  }

  return true;
}

// Helper to format relative time
function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);

  if (diffSec < 5) return "just now";
  if (diffSec < 60) return `${diffSec}s ago`;

  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;

  const diffHour = Math.floor(diffMin / 60);
  return `${diffHour}h ago`;
}

// Stage badge colors
const stageBadgeColors: Record<string, string> = {
  IDLE: "bg-gray-600",
  FINDING_OBJECT: "bg-blue-600",
  GUIDING_TO_PICKUP: "bg-yellow-600",
  CONFIRMING_PICKUP: "bg-purple-600",
  VERIFYING_OBJECT: "bg-orange-600",
  AWAITING_FEEDBACK: "bg-pink-600",
  DONE: "bg-green-600",
};

export default function ActivityGuide({ cameraOn, voiceOnlyMode = false }: ActivityGuideProps) {
  const [taskInput, setTaskInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentInstruction, setCurrentInstruction] = useState(
    "Start the camera and enter a task."
  );
  const [guidanceLog, setGuidanceLog] = useState<LogEntry[]>([]);
  const logIdCounterRef = useRef(0);
  const [stage, setStage] = useState("IDLE");
  const [awaitingFeedback, setAwaitingFeedback] = useState(false);
  const [frameUrl, setFrameUrl] = useState<string | null>(null);
  const [detectedObjects, setDetectedObjects] = useState<
    Array<{ name: string; box: number[] }>
  >([]);
  const [handDetected, setHandDetected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [useWebSpeech, setUseWebSpeech] = useState(true); // Try Web Speech API first
  const [fallbackToOffline, setFallbackToOffline] = useState(false);
  const [currentTaskTarget, setCurrentTaskTarget] = useState<string>("");
  const frameIntervalRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const lastInstructionRef = useRef<string>("");
  
  // Refs for voice control
  const taskInputRef = useRef<HTMLInputElement>(null);
  const micButtonRef = useRef<HTMLButtonElement>(null);
  const startTaskButtonRef = useRef<HTMLButtonElement>(null);
  const yesButtonRef = useRef<HTMLButtonElement>(null);
  const noButtonRef = useRef<HTMLButtonElement>(null);
  const voiceControlRef = useRef(getVoiceControlService());
  const isInDictationModeRef = useRef(false);
  const lastSpokenInstructionRef = useRef<string>("");

  // Add entry to guidance log with duplicate filtering
  const addLogEntry = useCallback(
    (
      instruction: string,
      stage: string,
      type: LogEntry["type"] = "instruction"
    ) => {
      setGuidanceLog((prev) => {
        // Skip if this is a duplicate or too similar to recent entries
        if (
          type === "instruction" &&
          !isSignificantlyDifferent(instruction, prev)
        ) {
          return prev;
        }

        // Increment counter using ref (avoids stale closure issues)
        logIdCounterRef.current += 1;

        const newEntry: LogEntry = {
          id: logIdCounterRef.current,
          instruction,
          timestamp: new Date(),
          stage,
          type,
        };

        // Prepend new entry (newest first), keep max 50 entries
        return [newEntry, ...prev].slice(0, 50);
      });
    },
    []
  );

  // Clear guidance log
  const clearLog = useCallback(() => {
    setGuidanceLog([]);
  }, []);

  // Auto-read instructions when they change (voice-only mode)
  useEffect(() => {
    if (voiceOnlyMode && currentInstruction && currentInstruction !== lastSpokenInstructionRef.current) {
      lastSpokenInstructionRef.current = currentInstruction;
      // Interrupt previous audio and speak new instruction
      voiceControlRef.current.speakText(currentInstruction, true);
    }
  }, [currentInstruction, voiceOnlyMode]);

  // Auto-read confirmation question when awaiting feedback (voice-only mode)
  useEffect(() => {
    if (voiceOnlyMode && awaitingFeedback && currentInstruction) {
      // Read the confirmation question
      voiceControlRef.current.speakText(currentInstruction, true);
    }
  }, [awaitingFeedback, voiceOnlyMode, currentInstruction]);

  // Voice control setup for Activity Guide
  useEffect(() => {
    if (!voiceOnlyMode) {
      // Stop dictation if active
      voiceControlRef.current.stopDictation();
      isInDictationModeRef.current = false;
      return;
    }

    const voiceControl = voiceControlRef.current;

    // Register command callback (don't start a new listener - App.tsx manages it)
    const unregister = voiceControl.registerCommandCallback(
      (command, transcript) => {
        console.log(`[Activity Guide] Voice command: ${command} - "${transcript}"`);

        switch (command) {
          case "enter_task":
            // Click the mic button to start listening/dictation
            if (!isListening && !isInDictationModeRef.current && micButtonRef.current) {
              micButtonRef.current.click();
            }
            break;

          case "start_task":
            // Stop dictation/listening if active
            if (isListening && micButtonRef.current) {
              // Click mic button to stop if listening
              micButtonRef.current.click();
            } else if (isInDictationModeRef.current) {
              voiceControl.stopDictation();
              isInDictationModeRef.current = false;
            }
            // Click start task button
            if (startTaskButtonRef.current && !isProcessing && taskInput.trim()) {
              startTaskButtonRef.current.click();
            }
            break;

          case "yes":
            // Click yes button if awaiting feedback
            if (awaitingFeedback && yesButtonRef.current) {
              yesButtonRef.current.click();
            }
            break;

          case "no":
            // Click no button if awaiting feedback
            if (awaitingFeedback && noButtonRef.current) {
              noButtonRef.current.click();
            }
            break;
        }
      }
    );

    return () => {
      unregister();
      voiceControl.stopDictation();
      isInDictationModeRef.current = false;
    };
  }, [voiceOnlyMode, awaitingFeedback, isProcessing, taskInput, isListening]);

  useEffect(() => {
    if (cameraOn) {
      startFrameProcessing();
    } else {
      stopFrameProcessing();
      setFrameUrl(null);
    }
    return () => stopFrameProcessing();
  }, [cameraOn, stage]);

  // Initialize Web Speech API first, fallback to MediaRecorder if not available
  useEffect(() => {
    // Check for Web Speech API support
    const SpeechRecognitionClass =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognitionClass) {
      setSpeechSupported(true);
      setUseWebSpeech(true);

      const recognition = new SpeechRecognitionClass();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setIsListening(true);
        setFallbackToOffline(false);
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        if (
          event.results &&
          event.results.length > 0 &&
          event.results[0].length > 0
        ) {
          const transcript = event.results[0][0].transcript.trim();
          if (transcript) {
            setTaskInput((prev) => prev + (prev ? " " : "") + transcript);
          }
        }
        setIsListening(false);
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error("Web Speech API error:", event.error, event.message);

        // If network error or service unavailable, fall back to offline method
        if (
          event.error === "network" ||
          event.error === "service-not-allowed"
        ) {
          console.log(
            "Web Speech API network error, falling back to offline Whisper model..."
          );
          setUseWebSpeech(false);
          setFallbackToOffline(true);
          setIsListening(false);

          // Automatically start offline recording if we have MediaRecorder support
          if (
            navigator.mediaDevices &&
            typeof navigator.mediaDevices.getUserMedia === "function"
          ) {
            setTimeout(() => {
              startRecording();
            }, 500);
          } else {
            alert(
              "Web Speech API failed and offline mode not available. Please check your internet connection."
            );
          }
        } else if (event.error === "not-allowed") {
          // Permission denied - don't auto-fallback, just show error
          setIsListening(false);
          alert(
            "Microphone permission denied. Please enable microphone access in your browser settings."
          );
        } else if (event.error === "no-speech") {
          // Normal - user didn't speak
          setIsListening(false);
        } else if (event.error === "aborted") {
          // User or system aborted
          setIsListening(false);
        } else {
          setIsListening(false);
          console.warn("Web Speech API error:", event.error);
        }
      };

      recognition.onend = () => {
        // Don't set listening to false here - let error/result handlers do it
      };

      recognitionRef.current = recognition;
    } else {
      // No Web Speech API, use offline method
      console.log("Web Speech API not available, using offline Whisper model");
      setUseWebSpeech(false);
      if (
        navigator.mediaDevices &&
        typeof navigator.mediaDevices.getUserMedia === "function"
      ) {
        setSpeechSupported(true);
      } else {
        setSpeechSupported(false);
        console.warn("No speech recognition available in this browser");
      }
    }

    return () => {
      // Cleanup Web Speech API
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
          recognitionRef.current.abort();
        } catch (e) {
          // Ignore errors during cleanup
        }
      }
      // Cleanup MediaRecorder
      if (
        mediaRecorderRef.current &&
        mediaRecorderRef.current.state !== "inactive"
      ) {
        try {
          mediaRecorderRef.current.stop();
        } catch (e) {
          // Ignore errors during cleanup
        }
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
    };
  }, []);

  const startFrameProcessing = () => {
    if (frameIntervalRef.current) return;

    const processFrame = async () => {
      try {
        // Always use process-frame endpoint to get annotated frames with YOLO boxes and hand tracking
        const result = await apiClient.processActivityFrame();
        setFrameUrl(`data:image/jpeg;base64,${result.frame}`);
        setCurrentInstruction(result.instruction);
        setStage(result.stage);
        setDetectedObjects(result.detected_objects || []);
        setHandDetected(result.hand_detected || false);

        // Only add to log if instruction is meaningfully different from the last one
        if (
          result.instruction &&
          result.instruction !== lastInstructionRef.current
        ) {
          lastInstructionRef.current = result.instruction;
          addLogEntry(result.instruction, result.stage, "instruction");
        }

        if (result.stage === "AWAITING_FEEDBACK") {
          setAwaitingFeedback(true);
        }
      } catch (error) {
        console.error("Error processing frame:", error);
      }
    };

    processFrame();
    frameIntervalRef.current = window.setInterval(processFrame, 100); // Update every 100ms for smooth video (~10 FPS)
  };

  const stopFrameProcessing = () => {
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }
  };

  const handleStartTask = async () => {
    if (!taskInput.trim() || !cameraOn) {
      alert("Please start the camera and enter a task.");
      return;
    }

    setIsProcessing(true);
    try {
      const request: TaskRequest = { goal: taskInput };
      const response = await apiClient.startTask(request);

      if (response.status === "success") {
        setCurrentInstruction(response.message);
        setStage(response.stage);
        setCurrentTaskTarget(response.primary_target || taskInput);
        lastInstructionRef.current = ""; // Reset to allow first instruction

        // Add task start entry to log (don't clear history)
        addLogEntry(
          `🎯 New Task: "${taskInput}" → Target: ${
            response.primary_target || "unknown"
          }`,
          response.stage,
          "task_start"
        );

        setTaskInput("");
      } else {
        alert("Failed to start task: " + response.message);
      }
    } catch (error) {
      console.error("Error starting task:", error);
      alert("Failed to start task. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFeedback = async (confirmed: boolean) => {
    try {
      const response = await apiClient.submitFeedback({ confirmed });
      setAwaitingFeedback(false);
      setStage(response.next_stage);
      setCurrentInstruction(response.message);
      lastInstructionRef.current = ""; // Reset to allow next instruction

      if (confirmed && response.next_stage === "DONE") {
        // Task completed
        addLogEntry(
          `✅ Task Completed: Found ${currentTaskTarget}!`,
          "DONE",
          "task_complete"
        );
      } else if (!confirmed) {
        // User said no - add feedback entry
        const attemptInfo = response.failed_attempts
          ? ` (Attempt #${response.failed_attempts})`
          : "";
        addLogEntry(
          `❌ Not correct${attemptInfo} - Rescanning...`,
          response.next_stage,
          "feedback"
        );
      }
    } catch (error) {
      console.error("Error submitting feedback:", error);
    }
  };

  const handlePlayAudio = async () => {
    if (!currentInstruction) return;

    try {
      const audioData = await apiClient.generateSpeech(currentInstruction);
      const audioBlob = new Blob(
        [Uint8Array.from(atob(audioData.audio_base64), (c) => c.charCodeAt(0))],
        { type: "audio/mpeg" }
      );
      const audioUrl = URL.createObjectURL(audioBlob);

      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
      }
    } catch (error) {
      console.error("Error generating speech:", error);
    }
  };

  const handleToggleListening = async () => {
    if (!speechSupported) {
      alert("Microphone access not available in this browser.");
      return;
    }

    if (isListening) {
      // Stop recording/listening
      if (useWebSpeech && recognitionRef.current) {
        try {
          recognitionRef.current.stop();
          recognitionRef.current.abort();
        } catch (e) {
          // Ignore errors
        }
      } else {
        await stopRecording();
      }
      setIsListening(false);
    } else {
      // Start recording - try Web Speech API first, fallback to offline
      if (useWebSpeech && recognitionRef.current) {
        startWebSpeechRecognition();
      } else {
        await startRecording();
      }
    }
  };

  const startWebSpeechRecognition = () => {
    if (!recognitionRef.current) {
      alert("Speech recognition not initialized.");
      return;
    }

    try {
      // Abort any existing recognition
      try {
        recognitionRef.current.abort();
      } catch (e) {
        // Ignore
      }

      // Start Web Speech API
      setTimeout(() => {
        if (recognitionRef.current) {
          try {
            recognitionRef.current.start();
          } catch (error: any) {
            const errorMsg = error.message || error.toString() || "";
            if (errorMsg.includes("already started")) {
              // Already running
              setIsListening(true);
            } else {
              console.error("Web Speech API start error:", error);
              // Fall back to offline
              setUseWebSpeech(false);
              startRecording();
            }
          }
        }
      }, 100);
    } catch (error) {
      console.error("Error starting Web Speech API:", error);
      // Fall back to offline
      setUseWebSpeech(false);
      startRecording();
    }
  };

  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Create MediaRecorder with WAV format (better compatibility)
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : "audio/wav",
      });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Convert audio chunks to blob
        const audioBlob = new Blob(audioChunksRef.current, {
          type: mediaRecorder.mimeType || "audio/webm",
        });

        // Convert to base64
        const reader = new FileReader();
        reader.onloadend = async () => {
          const base64Audio = (reader.result as string).split(",")[1];

          // Transcribe using backend
          setIsTranscribing(true);
          try {
            const result = await apiClient.transcribeAudio(base64Audio);
            if (result.success && result.text) {
              setTaskInput(
                (prev) => prev + (prev ? " " : "") + result.text.trim()
              );
            }
          } catch (error) {
            console.error("Transcription error:", error);
            alert("Failed to transcribe audio. Please try again.");
          } finally {
            setIsTranscribing(false);
          }
        };
        reader.readAsDataURL(audioBlob);

        // Stop all tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
          streamRef.current = null;
        }
      };

      // Start recording
      mediaRecorder.start();
      setIsListening(true);
    } catch (error: any) {
      console.error("Error starting recording:", error);
      setIsListening(false);

      if (
        error.name === "NotAllowedError" ||
        error.name === "PermissionDeniedError"
      ) {
        alert(
          "Microphone permission denied. Please enable microphone access in your browser settings."
        );
      } else if (
        error.name === "NotFoundError" ||
        error.name === "DevicesNotFoundError"
      ) {
        alert(
          "No microphone found. Please connect a microphone and try again."
        );
      } else {
        alert(
          "Failed to access microphone. Please check your browser settings and try again."
        );
      }
    }
  };

  const stopRecording = async () => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      try {
        mediaRecorderRef.current.stop();
      } catch (error) {
        console.error("Error stopping recording:", error);
      }
    }
    setIsListening(false);
  };

  return (
    <div className="flex-1 flex flex-col lg:flex-row p-6 md:p-10 gap-6 md:gap-10 overflow-hidden h-full">
      {/* Left Panel - Camera Feed */}
      <div className="flex-1 flex flex-col min-h-0 lg:min-h-0 lg:h-full">
        <div className="flex-1 bg-black rounded-3xl overflow-hidden relative border-2 border-dark-border shadow-2xl shadow-black/50 min-h-0 h-full">
          {cameraOn && frameUrl ? (
            <img
              src={frameUrl}
              alt="Camera feed"
              className="w-full h-full object-contain"
              style={{ display: "block", maxWidth: "100%", maxHeight: "100%" }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-dark-text-secondary bg-dark-surface">
              <div className="text-center">
                <p className="text-lg">Camera feed will appear here</p>
                {!cameraOn && (
                  <p className="text-sm mt-2">Please start the camera</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right Panel - Controls and Logs */}
      <div className="lg:w-[38%] flex flex-col flex-shrink-0 gap-6 min-h-0 lg:h-full">
        {/* Task Input */}
        <div className="bg-dark-surface rounded-2xl border border-dark-border p-4">
          <h2 className="text-base font-semibold font-heading text-dark-text-primary mb-3">
            Task Input
          </h2>
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <input
                ref={taskInputRef}
                type="text"
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleStartTask()}
                placeholder="Enter a task (e.g., 'find my watch')"
                disabled={
                  !cameraOn ||
                  isProcessing ||
                  (stage !== "IDLE" && stage !== "DONE")
                }
                className="w-full px-4 py-2 pr-12 bg-dark-bg border border-dark-border rounded-xl text-dark-text-primary placeholder-dark-text-secondary focus:outline-none focus:border-brand-gold disabled:opacity-50"
              />
              {speechSupported && (
                <>
                  <button
                    ref={micButtonRef}
                    onClick={handleToggleListening}
                    disabled={
                      !cameraOn ||
                      isProcessing ||
                      (stage !== "IDLE" && stage !== "DONE")
                    }
                    className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all ${
                      isListening
                        ? "bg-red-600 text-white animate-pulse"
                        : "text-dark-text-secondary hover:text-brand-gold hover:bg-dark-surface"
                    } disabled:opacity-50 disabled:cursor-not-allowed ${
                      voiceOnlyMode ? "opacity-0 pointer-events-none" : ""
                    }`}
                    title={isListening ? "Stop listening" : "Start voice input"}
                  >
                    {isListening ? (
                      <MicOff className="w-4 h-4" />
                    ) : (
                      <Mic className="w-4 h-4" />
                    )}
                  </button>
                  {voiceOnlyMode && (
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-brand-gold pointer-events-none">
                      <Mic className="w-4 h-4 animate-pulse" title="Voice-only mode active" />
                    </div>
                  )}
                </>
              )}
            </div>
            <button
              ref={startTaskButtonRef}
              onClick={handleStartTask}
              disabled={
                !cameraOn ||
                isProcessing ||
                (stage !== "IDLE" && stage !== "DONE")
              }
              className="px-5 py-2 bg-brand-gold text-brand-charcoal rounded-xl font-semibold hover:bg-opacity-85 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isProcessing ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                "Start"
              )}
            </button>
          </div>
          {speechSupported && (
            <p className="text-xs text-dark-text-secondary mt-2">
              {isTranscribing ? (
                <span className="text-blue-400">
                  ⏳ Transcribing with offline model...
                </span>
              ) : isListening ? (
                <span className="text-red-400">
                  {useWebSpeech ? (
                    <>🎤 Listening (Web Speech API)... Speak your task now.</>
                  ) : (
                    <>
                      🎤 Recording (offline)... Speak your task now. Click mic
                      again to stop.
                    </>
                  )}
                </span>
              ) : (
                <span>
                  💡 Click the microphone icon to use voice input
                  {useWebSpeech ? " (Web Speech API)" : " (offline Whisper)"}
                </span>
              )}
            </p>
          )}
        </div>

        {/* Current Instruction */}
        <div className="bg-dark-surface rounded-2xl border border-dark-border p-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-base font-semibold font-heading text-dark-text-primary">
              Current Instruction
            </h2>
            <button
              onClick={handlePlayAudio}
              className="p-1.5 border border-dark-border text-dark-text-secondary rounded-lg hover:border-brand-gold hover:text-brand-gold transition-all"
            >
              <Volume2 className="w-4 h-4" />
            </button>
          </div>
          <div className="bg-dark-bg rounded-lg p-3">
            <p className="text-dark-text-primary leading-snug text-sm">
              {currentInstruction}
            </p>
          </div>

          {/* Feedback Buttons */}
          {awaitingFeedback && (
            <div className="mt-4 flex gap-3">
              <button
                ref={yesButtonRef}
                onClick={() => handleFeedback(true)}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 transition-all"
              >
                <CheckCircle className="w-5 h-5" />
                Yes
              </button>
              <button
                ref={noButtonRef}
                onClick={() => handleFeedback(false)}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-red-600 text-white rounded-xl font-semibold hover:bg-red-700 transition-all"
              >
                <XCircle className="w-5 h-5" />
                No
              </button>
            </div>
          )}
        </div>

        {/* Guidance Log */}
        <div className="flex-[2] bg-dark-surface rounded-2xl border border-dark-border p-4 overflow-hidden min-h-[200px] flex flex-col">
          <div className="flex items-center justify-between mb-2 flex-shrink-0">
            <h3 className="text-sm font-semibold font-heading text-dark-text-primary uppercase tracking-wider">
              Guidance Log
            </h3>
            {guidanceLog.length > 0 && (
              <button
                onClick={clearLog}
                className="p-1 text-dark-text-secondary hover:text-red-400 hover:bg-dark-bg rounded transition-all"
                title="Clear log"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
          <div className="space-y-1 flex-1 overflow-y-auto custom-scrollbar pr-1">
            {guidanceLog.length === 0 ? (
              <p className="text-dark-text-secondary text-xs py-2">
                No entries yet. Start a task to see the log.
              </p>
            ) : (
              guidanceLog.map((entry) => (
                <div
                  key={entry.id}
                  className={`text-xs rounded px-2.5 py-1.5 flex items-start gap-2 ${
                    entry.type === "task_start"
                      ? "bg-blue-900/30 border-l-2 border-blue-500"
                      : entry.type === "task_complete"
                      ? "bg-green-900/30 border-l-2 border-green-500"
                      : entry.type === "feedback"
                      ? "bg-orange-900/30 border-l-2 border-orange-500"
                      : "bg-dark-bg/50"
                  }`}
                >
                  {/* Instruction text - takes most space */}
                  <p
                    className={`flex-1 leading-snug ${
                      entry.type === "task_start"
                        ? "text-blue-200"
                        : entry.type === "task_complete"
                        ? "text-green-200"
                        : entry.type === "feedback"
                        ? "text-orange-200"
                        : "text-dark-text-primary/90"
                    }`}
                  >
                    {entry.instruction}
                  </p>
                  {/* Right side: Time + Stage badge */}
                  <div className="flex flex-col items-end gap-0.5 flex-shrink-0">
                    <span className="text-[10px] text-dark-text-secondary">
                      {formatRelativeTime(entry.timestamp)}
                    </span>
                    <span
                      className={`text-[9px] px-1.5 py-0.5 rounded text-white/90 ${
                        stageBadgeColors[entry.stage] || "bg-gray-600"
                      }`}
                    >
                      {entry.stage.replace(/_/g, " ")}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Detection Info */}
        <div className="bg-dark-surface rounded-xl border border-dark-border px-4 py-2.5">
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <span className="text-dark-text-secondary">
                Objects Detected:
              </span>
              <span className="ml-2 text-dark-text-primary font-semibold">
                {detectedObjects.length}
              </span>
            </div>
            <div>
              <span className="text-dark-text-secondary">Hand Detected:</span>
              <span
                className={`ml-2 font-semibold ${
                  handDetected ? "text-green-400" : "text-gray-400"
                }`}
              >
                {handDetected ? "Yes" : "No"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Hidden audio element */}
      <audio ref={audioRef} />
    </div>
  );
}
