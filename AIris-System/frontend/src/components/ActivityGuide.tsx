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

export default function ActivityGuide({
  cameraOn,
  voiceOnlyMode = false,
}: ActivityGuideProps) {
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
  const [currentTaskTarget, setCurrentTaskTarget] = useState<string>("");
  const [cameraFacingTowardsUser, setCameraFacingTowardsUser] = useState<boolean>(true);
  const frameIntervalRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
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

  // Auto-read instructions when they change (voice-only mode ONLY)
  useEffect(() => {
    if (!voiceOnlyMode) {
      // Voice-only mode is OFF - don't speak
      return;
    }

    if (
      currentInstruction &&
      currentInstruction !== lastSpokenInstructionRef.current &&
      currentInstruction !== "Start the camera and enter a task." // Skip default message
    ) {
      lastSpokenInstructionRef.current = currentInstruction;
      // Interrupt previous audio and speak new instruction
      voiceControlRef.current.speakText(currentInstruction, true);
    }
  }, [currentInstruction, voiceOnlyMode]);

  // Auto-read confirmation question when awaiting feedback (voice-only mode ONLY)
  useEffect(() => {
    if (!voiceOnlyMode) {
      // Voice-only mode is OFF - don't speak
      return;
    }

    if (awaitingFeedback && currentInstruction) {
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
    console.log(
      `[ActivityGuide] Registering voice command callback. Voice-only mode: ${voiceOnlyMode}`
    );
    const unregister = voiceControl.registerCommandCallback(
      (command, transcript) => {
        console.log(
          `[ActivityGuide] Voice command received: ${command} - "${transcript}"`,
          {
            isProcessing,
            cameraOn,
            isInDictationMode: isInDictationModeRef.current,
            awaitingFeedback,
            taskInput: taskInput.substring(0, 50) + "...",
          }
        );

        switch (command) {
          case "enter_task":
            console.log(`[ActivityGuide] Processing enter_task command`);
            // Start dictation mode using voiceControl service
            if (!isInDictationModeRef.current && !isProcessing && cameraOn) {
              console.log(`[ActivityGuide] Starting dictation...`);
              isInDictationModeRef.current = true;
              // Clear existing input when starting dictation
              setTaskInput("");
              // Audio cue: Ready to accept task input
              voiceControl.markUserInteracted();
              voiceControl.speakText("Alright, what do I need to find?", false);
              voiceControl.startDictation((dictatedText) => {
                console.log(
                  `[ActivityGuide] Dictation text received: "${dictatedText}"`
                );
                // Update input field in real-time as user speaks
                // The dictatedText is the full phrase from Web Speech API
                setTaskInput((prev) => {
                  const newText = dictatedText.trim();
                  // In dictation mode, replace or append based on what makes sense
                  // If the new text is longer or different, use it
                  if (newText) {
                    // If previous text is empty or new text doesn't contain previous, append
                    if (
                      !prev ||
                      (!newText.toLowerCase().includes(prev.toLowerCase()) &&
                        !prev.toLowerCase().includes(newText.toLowerCase()))
                    ) {
                      return prev ? prev + " " + newText : newText;
                    }
                    // If new text contains previous, use new text (it's more complete)
                    if (newText.toLowerCase().includes(prev.toLowerCase())) {
                      return newText;
                    }
                    return prev;
                  }
                  return prev;
                });
              });
            } else {
              console.log(`[ActivityGuide] Cannot start dictation:`, {
                isInDictationMode: isInDictationModeRef.current,
                isProcessing,
                cameraOn,
              });
            }
            break;

          case "start_task":
            console.log(`[ActivityGuide] Processing start_task command`);
            // Stop dictation if active
            if (isInDictationModeRef.current) {
              console.log(`[ActivityGuide] Stopping dictation`);
              voiceControl.stopDictation();
              isInDictationModeRef.current = false;
            }
            // Start task if we have input
            if (!isProcessing && taskInput.trim()) {
              console.log(
                `[ActivityGuide] Starting task with input: "${taskInput}"`
              );
              handleStartTask();
            } else {
              console.log(`[ActivityGuide] Cannot start task:`, {
                isProcessing,
                hasInput: !!taskInput.trim(),
                taskInput: taskInput.substring(0, 50),
              });
            }
            break;

          case "yes":
            console.log(`[ActivityGuide] Processing yes command`);
            // Click yes button if awaiting feedback
            if (awaitingFeedback && yesButtonRef.current) {
              console.log(`[ActivityGuide] Clicking yes button`);
              yesButtonRef.current.click();
            } else {
              console.log(`[ActivityGuide] Cannot click yes:`, {
                awaitingFeedback,
                hasButton: !!yesButtonRef.current,
              });
            }
            break;

          case "no":
            console.log(`[ActivityGuide] Processing no command`);
            // Click no button if awaiting feedback
            if (awaitingFeedback && noButtonRef.current) {
              console.log(`[ActivityGuide] Clicking no button`);
              noButtonRef.current.click();
            } else {
              console.log(`[ActivityGuide] Cannot click no:`, {
                awaitingFeedback,
                hasButton: !!noButtonRef.current,
              });
            }
            break;

          default:
            console.log(`[ActivityGuide] Unhandled command: ${command}`);
        }
      }
    );

    return () => {
      unregister();
      voiceControl.stopDictation();
      isInDictationModeRef.current = false;
    };
  }, [voiceOnlyMode, awaitingFeedback, isProcessing, taskInput, cameraOn]);

  useEffect(() => {
    if (cameraOn) {
      startFrameProcessing();
    } else {
      stopFrameProcessing();
      setFrameUrl(null);
    }
    return () => stopFrameProcessing();
  }, [cameraOn, stage]);

  // Update camera orientation when toggle changes
  useEffect(() => {
    if (cameraOn) {
      apiClient.setCameraOrientation(cameraFacingTowardsUser).catch((error) => {
        console.error("Failed to set camera orientation:", error);
      });
    }
  }, [cameraFacingTowardsUser, cameraOn]);

  const startFrameProcessing = () => {
    if (frameIntervalRef.current) return;

    let consecutiveErrors = 0;
    let lastFrameTime = 0;
    const FRAME_INTERVAL_MS = 100; // 10 FPS - smooth video feed
    const MAX_CONSECUTIVE_ERRORS = 5;

    const processFrame = async () => {
      // Stop if camera is off
      if (!cameraOn) {
        if (frameIntervalRef.current) {
          clearInterval(frameIntervalRef.current);
          frameIntervalRef.current = null;
        }
        return;
      }

      const now = Date.now();
      // Throttle to prevent overwhelming the backend
      if (now - lastFrameTime < FRAME_INTERVAL_MS) {
        return;
      }
      lastFrameTime = now;

      try {
        // Always use process-frame endpoint to get annotated frames with YOLO boxes and hand tracking
        const result = await apiClient.processActivityFrame();

        // Reset error counter on success
        consecutiveErrors = 0;

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
      } catch (error: any) {
        consecutiveErrors++;

        // Check for specific error types (Axios errors have error.code, error.response, etc.)
        const errorCode = error?.code || error?.response?.status || "";
        const errorMessage = error?.message || String(error) || "";
        const isResourceError =
          errorCode === "ERR_EMPTY_RESPONSE" ||
          errorCode === "ERR_INSUFFICIENT_RESOURCES" ||
          errorCode === 503 ||
          errorCode === 500 ||
          errorMessage.includes("ERR_EMPTY_RESPONSE") ||
          errorMessage.includes("ERR_INSUFFICIENT_RESOURCES") ||
          errorMessage.includes("Network Error") ||
          (error?.response?.status >= 500 && error?.response?.status < 600);

        if (isResourceError) {
          // Backend is overwhelmed or crashed - back off
          console.warn(
            `[ActivityGuide] Backend resource error (${consecutiveErrors}/${MAX_CONSECUTIVE_ERRORS}):`,
            {
              code: errorCode,
              message: errorMessage,
              status: error?.response?.status,
            }
          );

          if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
            // Too many errors - stop processing and wait
            console.error(
              "[ActivityGuide] Too many consecutive errors, stopping frame processing"
            );
            if (frameIntervalRef.current) {
              clearInterval(frameIntervalRef.current);
              frameIntervalRef.current = null;
            }
            // Restart after delay
            setTimeout(() => {
              if (cameraOn && frameIntervalRef.current === null) {
                console.log(
                  "[ActivityGuide] Retrying frame processing after backoff"
                );
                consecutiveErrors = 0;
                startFrameProcessing();
              }
            }, 5000); // Wait 5 seconds before retrying
            return;
          }
        } else {
          // Other errors - log but continue (reset counter after a few non-resource errors)
          if (consecutiveErrors > 3) {
            console.error("Error processing frame:", {
              error,
              code: errorCode,
              message: errorMessage,
              status: error?.response?.status,
            });
            consecutiveErrors = 0; // Reset after logging to prevent false positives
          }
        }
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

  const handlePlayAudio = () => {
    if (!currentInstruction) return;
    // Use native TTS for instant playback
    voiceControlRef.current.speakText(currentInstruction, true);
  };

  return (
    <div className="flex-1 flex flex-col lg:flex-row p-6 md:p-10 gap-6 md:gap-10 overflow-hidden h-full">
      {/* Left Panel - Camera Feed */}
      <div className="flex-1 flex flex-col min-h-0 lg:min-h-0 lg:h-full">
        {/* Camera Orientation Toggle */}
        <div className="mb-3 flex items-center justify-end">
          <label className="flex items-center gap-2 text-xs text-dark-text-secondary cursor-pointer hover:text-dark-text-primary transition-colors">
            <input
              type="checkbox"
              checked={cameraFacingTowardsUser}
              onChange={(e) => setCameraFacingTowardsUser(e.target.checked)}
              className="w-4 h-4 rounded border-dark-border bg-dark-bg text-brand-gold focus:ring-brand-gold focus:ring-offset-0 cursor-pointer"
            />
            <span>
              Camera is facing {cameraFacingTowardsUser ? "towards me" : "away from me"}
            </span>
          </label>
        </div>
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
              {!voiceOnlyMode && (
                <button
                  ref={micButtonRef}
                  onClick={() => {
                    // In non-voice-only mode, use voiceControl for dictation
                    const voiceControl = voiceControlRef.current;
                    if (!isInDictationModeRef.current) {
                      isInDictationModeRef.current = true;
                      voiceControl.startDictation((dictatedText) => {
                        setTaskInput((prev) => {
                          const newText = dictatedText.trim();
                          if (prev && !prev.endsWith(newText)) {
                            return prev + " " + newText;
                          }
                          return newText;
                        });
                      });
                    } else {
                      voiceControl.stopDictation();
                      isInDictationModeRef.current = false;
                    }
                  }}
                  disabled={
                    !cameraOn ||
                    isProcessing ||
                    (stage !== "IDLE" && stage !== "DONE")
                  }
                  className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all ${
                    isInDictationModeRef.current
                      ? "bg-red-600 text-white animate-pulse"
                      : "text-dark-text-secondary hover:text-brand-gold hover:bg-dark-surface"
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                  title={
                    isInDictationModeRef.current
                      ? "Stop listening"
                      : "Start voice input"
                  }
                >
                  {isInDictationModeRef.current ? (
                    <MicOff className="w-4 h-4" />
                  ) : (
                    <Mic className="w-4 h-4" />
                  )}
                </button>
              )}
              {voiceOnlyMode && (
                <div
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-brand-gold pointer-events-none"
                  title="Voice-only mode active - say 'input task' to start dictation"
                >
                  <Mic className="w-4 h-4 animate-pulse" />
                </div>
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
          {!voiceOnlyMode && (
            <p className="text-xs text-dark-text-secondary mt-2">
              {isInDictationModeRef.current ? (
                <span className="text-red-400">
                  🎤 Listening... Speak your task now. Click mic again to stop.
                </span>
              ) : (
                <span>💡 Click the microphone icon to use voice input</span>
              )}
            </p>
          )}
          {voiceOnlyMode && (
            <p className="text-xs text-dark-text-secondary mt-2">
              {isInDictationModeRef.current ? (
                <span className="text-red-400">
                  🎤 Dictation active... Say "start task" when done.
                </span>
              ) : (
                <span>💡 Say "input task" to start voice input</span>
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
