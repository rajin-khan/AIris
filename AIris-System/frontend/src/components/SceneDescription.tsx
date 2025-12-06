import { useState, useEffect, useRef } from "react";
import {
  Volume2,
  Play,
  Square,
  Eye,
  FileText,
  AlertTriangle,
  Loader2,
  Calendar,
  Clock,
  Radio,
  ChevronDown,
} from "lucide-react";
import { apiClient } from "../services/api";

interface SceneDescriptionProps {
  cameraOn: boolean;
}

interface SessionStats {
  elapsed_seconds: number;
  descriptions_count: number;
  summaries_count: number;
  alerts_count: number;
  buffer_size: number;
  buffer_max: number;
  analysis_interval: number;
}

interface SummaryEvent {
  timestamp: string;
  summary: string;
  isAlert: boolean;
}

export default function SceneDescription({ cameraOn }: SceneDescriptionProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentDescription, setCurrentDescription] = useState("");
  const [currentSummary, setCurrentSummary] = useState("");
  const [safetyAlert, setSafetyAlert] = useState(false);
  const [frameUrl, setFrameUrl] = useState<string | null>(null);
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [recordingLogs, setRecordingLogs] = useState<any[]>([]);
  const [expandedLogIdx, setExpandedLogIdx] = useState<number | null>(0);
  const [analysisCountdown, setAnalysisCountdown] = useState(3);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [currentSessionEvents, setCurrentSessionEvents] = useState<
    SummaryEvent[]
  >([]);
  const [filledFrames, setFilledFrames] = useState<number[]>([]);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);

  const frameIntervalRef = useRef<number | null>(null);
  const analysisIntervalRef = useRef<number | null>(null);
  const countdownIntervalRef = useRef<number | null>(null);
  const timerIntervalRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const lastSummaryRef = useRef<string>("");
  const frameCountRef = useRef(0);

  const BUFFER_MAX = 5;

  useEffect(() => {
    loadLogs();
  }, []);

  useEffect(() => {
    if (cameraOn) {
      startFastFrameUpdates();
    } else {
      stopAllIntervals();
      setFrameUrl(null);
    }
    return () => stopAllIntervals();
  }, [cameraOn]);

  useEffect(() => {
    if (isRecording) {
      startAnalysisInterval();
      startCountdownTimer();
      startElapsedTimer();
      setCurrentSessionEvents([]);
      setFilledFrames([]);
      frameCountRef.current = 0;
    } else {
      stopAnalysisInterval();
      stopCountdownTimer();
      stopElapsedTimer();
      setAnalysisCountdown(3);
      setElapsedTime(0);
    }
    return () => {
      stopAnalysisInterval();
      stopCountdownTimer();
      stopElapsedTimer();
    };
  }, [isRecording]);

  const loadLogs = async () => {
    try {
      const logs = await apiClient.getRecordingLogs();
      setRecordingLogs(logs);
    } catch (error) {
      console.error("Error loading logs:", error);
    }
  };

  const startFastFrameUpdates = () => {
    if (frameIntervalRef.current) clearInterval(frameIntervalRef.current);

    const updateFrame = async () => {
      try {
        const frameUrl = await apiClient.getCameraFrame();
        setFrameUrl(frameUrl);
      } catch (error) {
        console.error("Error getting frame:", error);
      }
    };

    updateFrame();
    frameIntervalRef.current = window.setInterval(updateFrame, 50);
  };

  const startAnalysisInterval = () => {
    if (analysisIntervalRef.current) clearInterval(analysisIntervalRef.current);

    const processFrame = async () => {
      try {
        setIsProcessing(true);
        const result = await apiClient.processSceneFrame();

        if (result.description) {
          setCurrentDescription(result.description);
          // Add a filled frame indicator
          frameCountRef.current += 1;
          const frameIndex = (frameCountRef.current - 1) % BUFFER_MAX;
          setFilledFrames((prev) => {
            const newFrames = [...prev];
            if (!newFrames.includes(frameIndex)) {
              newFrames.push(frameIndex);
            }
            return newFrames;
          });
        }

        if (result.stats) {
          setStats(result.stats);
        }

        // Check if we got a new summary
        if (result.summary && result.summary !== lastSummaryRef.current) {
          setIsGeneratingSummary(true);
          const newSummary = result.summary;
          const isAlert = result.safety_alert || false;

          setTimeout(() => {
            setCurrentSummary(newSummary);
            lastSummaryRef.current = newSummary;

            // Add to current session events
            const newEvent: SummaryEvent = {
              timestamp: new Date().toISOString(),
              summary: newSummary,
              isAlert: isAlert,
            };
            setCurrentSessionEvents((prev) => [newEvent, ...prev]);

            // Reset frame buffer visualization
            setFilledFrames([]);
            frameCountRef.current = 0;
            setIsGeneratingSummary(false);
          }, 500);
        }

        setSafetyAlert(result.safety_alert || false);
        setIsRecording(result.is_recording);
        setIsProcessing(false);
        setAnalysisCountdown(3);
      } catch (error) {
        console.error("Error processing frame:", error);
        setIsProcessing(false);
      }
    };

    processFrame();
    analysisIntervalRef.current = window.setInterval(processFrame, 3000);
  };

  const startCountdownTimer = () => {
    if (countdownIntervalRef.current)
      clearInterval(countdownIntervalRef.current);
    countdownIntervalRef.current = window.setInterval(() => {
      setAnalysisCountdown((prev) => (prev > 0 ? prev - 1 : 3));
    }, 1000);
  };

  const startElapsedTimer = () => {
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    timerIntervalRef.current = window.setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);
  };

  const stopAllIntervals = () => {
    if (frameIntervalRef.current) clearInterval(frameIntervalRef.current);
    if (analysisIntervalRef.current) clearInterval(analysisIntervalRef.current);
    if (countdownIntervalRef.current)
      clearInterval(countdownIntervalRef.current);
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    frameIntervalRef.current = null;
    analysisIntervalRef.current = null;
    countdownIntervalRef.current = null;
    timerIntervalRef.current = null;
  };

  const stopAnalysisInterval = () => {
    if (analysisIntervalRef.current) {
      clearInterval(analysisIntervalRef.current);
      analysisIntervalRef.current = null;
    }
  };

  const stopCountdownTimer = () => {
    if (countdownIntervalRef.current) {
      clearInterval(countdownIntervalRef.current);
      countdownIntervalRef.current = null;
    }
  };

  const stopElapsedTimer = () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
  };

  const handleStartRecording = async () => {
    if (!cameraOn) {
      alert("Please start the camera first!");
      return;
    }

    try {
      const response = await apiClient.startRecording();
      if (response.status === "success") {
        setIsRecording(true);
        setCurrentDescription("");
        setCurrentSummary("");
        setSafetyAlert(false);
        setStats(null);
        setCurrentSessionEvents([]);
        setFilledFrames([]);
        frameCountRef.current = 0;
        lastSummaryRef.current = "";
      }
    } catch (error) {
      console.error("Error starting recording:", error);
      alert("Failed to start recording");
    }
  };

  const handleStopRecording = async () => {
    try {
      const response = await apiClient.stopRecording();
      if (response.status === "success") {
        setIsRecording(false);
        await loadLogs();
      }
    } catch (error) {
      console.error("Error stopping recording:", error);
      alert("Failed to stop recording");
    }
  };

  const handlePlayAudio = async () => {
    const textToSpeak = currentSummary || currentDescription;
    if (!textToSpeak) return;

    try {
      const audioData = await apiClient.generateSpeech(textToSpeak);
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

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs
      .toString()
      .padStart(2, "0")}`;
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return "Unknown";
    }
  };

  const formatTimeShort = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return "";
    }
  };

  return (
    <div className="flex-1 flex flex-col lg:flex-row p-6 gap-5 overflow-hidden h-full">
      {/* Left Panel - Camera Feed */}
      <div className="flex-1 flex flex-col min-h-0 lg:h-full">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-semibold font-heading text-dark-text-primary">
            Live View
          </h2>
          <div className="flex items-center gap-3">
            {isRecording && (
              <div className="flex items-center gap-2 px-2.5 py-1 bg-dark-surface rounded-lg border border-dark-border">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                <span className="text-dark-text-primary text-xs font-medium">
                  {formatTime(elapsedTime)}
                </span>
              </div>
            )}
            {!isRecording ? (
              <button
                onClick={handleStartRecording}
                disabled={!cameraOn || isProcessing}
                className="px-4 py-2 rounded-lg font-semibold text-sm transition-all flex items-center gap-2
                  bg-brand-gold text-brand-charcoal hover:bg-opacity-90
                  disabled:bg-dark-surface disabled:text-dark-text-secondary disabled:cursor-not-allowed"
              >
                <Play className="w-4 h-4" />
                START
              </button>
            ) : (
              <button
                onClick={handleStopRecording}
                className="px-4 py-2 rounded-lg font-semibold text-sm transition-all flex items-center gap-2 
                  bg-red-600 text-white hover:bg-red-700"
              >
                <Square className="w-4 h-4" />
                STOP
              </button>
            )}
          </div>
        </div>

        {/* Video Feed */}
        <div className="flex-1 bg-black rounded-xl overflow-hidden relative border border-dark-border min-h-0 h-full">
          {cameraOn && frameUrl ? (
            <>
              <img
                src={frameUrl}
                alt="Camera feed"
                className="w-full h-full object-contain"
              />
              {isRecording && (
                <>
                  <div className="absolute top-3 left-3 flex items-center gap-2 bg-black/70 px-2.5 py-1 rounded">
                    <Radio className="w-3 h-3 text-red-500 animate-pulse" />
                    <span className="text-white text-xs font-medium">REC</span>
                  </div>
                  <div className="absolute top-3 right-3 bg-black/70 px-2.5 py-1 rounded">
                    <span className="text-dark-text-secondary text-xs">
                      {isProcessing ? (
                        <span className="text-brand-gold flex items-center gap-1">
                          <Loader2 className="w-3 h-3 animate-spin" />
                          Analyzing
                        </span>
                      ) : (
                        `Next: ${analysisCountdown}s`
                      )}
                    </span>
                  </div>
                </>
              )}
            </>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-dark-text-secondary bg-dark-surface">
              <div className="text-center">
                <Eye className="w-10 h-10 mx-auto mb-2 opacity-30" />
                <p className="text-sm">Camera feed will appear here</p>
                {!cameraOn && (
                  <p className="text-xs mt-1 opacity-60">
                    Start the camera first
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right Panel */}
      <div className="lg:w-[38%] flex flex-col gap-4 min-h-0 lg:h-full overflow-hidden">
        {/* Current Description */}
        <div className="bg-dark-surface rounded-xl border border-dark-border p-4 flex-shrink-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-semibold text-dark-text-secondary uppercase tracking-wider flex items-center gap-1.5">
              <Eye className="w-3.5 h-3.5" />
              Current Observation
            </h3>
            <button
              onClick={handlePlayAudio}
              disabled={!currentDescription}
              className="p-1 text-dark-text-secondary hover:text-brand-gold transition-colors disabled:opacity-30"
            >
              <Volume2 className="w-4 h-4" />
            </button>
          </div>
          <div className="bg-dark-bg rounded-lg p-3 min-h-[50px]">
            {currentDescription ? (
              <p className="text-dark-text-primary text-sm leading-relaxed">
                {currentDescription}
              </p>
            ) : (
              <p className="text-dark-text-secondary text-sm opacity-60">
                {isRecording
                  ? "Waiting for analysis..."
                  : "Start recording to begin"}
              </p>
            )}
          </div>
        </div>

        {/* Summary Section with Frame Buffer */}
        <div className="bg-dark-surface rounded-xl border border-dark-border p-4 flex-shrink-0">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-semibold text-dark-text-secondary uppercase tracking-wider">
              Summary Generation
            </h3>
            {stats && (
              <span className="text-xs text-dark-text-secondary">
                {stats.summaries_count} generated
              </span>
            )}
          </div>

          {/* Frame Buffer Visualization */}
          <div className="mb-3">
            <div className="flex items-center gap-1.5 mb-2">
              {Array.from({ length: BUFFER_MAX }).map((_, idx) => (
                <div
                  key={idx}
                  className={`flex-1 h-2 rounded-full transition-all duration-500 ${
                    filledFrames.includes(idx) ? "bg-brand-gold" : "bg-dark-bg"
                  }`}
                  style={{
                    transitionDelay: `${idx * 50}ms`,
                  }}
                />
              ))}
            </div>
            <p className="text-xs text-dark-text-secondary text-center">
              {isGeneratingSummary ? (
                <span className="text-brand-gold flex items-center justify-center gap-1">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Generating summary...
                </span>
              ) : isRecording ? (
                `${filledFrames.length} of ${BUFFER_MAX} frames collected`
              ) : (
                "Frames will fill as analysis runs"
              )}
            </p>
          </div>

          {/* Current Summary */}
          <div
            className={`bg-dark-bg rounded-lg p-3 min-h-[60px] transition-all ${
              safetyAlert ? "border border-red-500/50" : ""
            }`}
          >
            {safetyAlert && (
              <div className="flex items-center gap-1.5 mb-2 text-red-400 text-xs">
                <AlertTriangle className="w-3.5 h-3.5" />
                Safety Alert
              </div>
            )}
            {currentSummary ? (
              <p className="text-dark-text-primary text-sm leading-relaxed">
                {currentSummary}
              </p>
            ) : (
              <p className="text-dark-text-secondary text-sm opacity-60">
                Summary will appear after {BUFFER_MAX} observations
              </p>
            )}
          </div>
        </div>

        {/* Recording History */}
        <div className="bg-dark-surface rounded-xl border border-dark-border flex-1 min-h-0 overflow-hidden flex flex-col">
          <div className="px-4 py-3 border-b border-dark-border flex items-center justify-between flex-shrink-0">
            <h3 className="text-xs font-semibold text-dark-text-secondary uppercase tracking-wider flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5" />
              Recording History
            </h3>
            <span className="text-xs text-dark-text-secondary">
              {recordingLogs.length} sessions
            </span>
          </div>

          <div className="flex-1 overflow-y-auto custom-scrollbar p-3">
            {/* Current Session (live) */}
            {isRecording && currentSessionEvents.length > 0 && (
              <div className="mb-3 pb-3 border-b border-dark-border">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-xs font-semibold text-dark-text-primary">
                    Current Session
                  </span>
                  <span className="text-xs text-dark-text-secondary ml-auto">
                    {currentSessionEvents.length} events
                  </span>
                </div>
                <div className="space-y-2 max-h-[150px] overflow-y-auto custom-scrollbar">
                  {currentSessionEvents.map((event, idx) => (
                    <div
                      key={idx}
                      className={`p-2.5 rounded-lg text-xs animate-slideIn ${
                        event.isAlert
                          ? "bg-red-950/30 border-l-2 border-red-500"
                          : "bg-dark-bg border-l-2 border-brand-gold"
                      }`}
                      style={{ animationDelay: `${idx * 50}ms` }}
                    >
                      <div className="flex items-center gap-2 mb-1 text-dark-text-secondary">
                        <Clock className="w-3 h-3" />
                        {formatTimeShort(event.timestamp)}
                        {event.isAlert && (
                          <span className="text-red-400 text-[10px] font-medium ml-auto">
                            ALERT
                          </span>
                        )}
                      </div>
                      <p className="text-dark-text-primary leading-relaxed">
                        {event.summary}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Past Sessions */}
            {recordingLogs.length === 0 && !isRecording ? (
              <div className="text-center py-8">
                <FileText className="w-8 h-8 text-dark-text-secondary/20 mx-auto mb-2" />
                <p className="text-dark-text-secondary text-sm">
                  No recordings yet
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {recordingLogs.map((log, idx) => {
                  const hasAlerts = log.events?.some(
                    (e: any) => e.flag === "SAFETY_ALERT"
                  );
                  const eventCount = log.events?.length || 0;
                  const isExpanded = expandedLogIdx === idx;

                  return (
                    <div
                      key={idx}
                      className={`rounded-lg overflow-hidden border transition-colors ${
                        hasAlerts
                          ? "bg-red-950/20 border-red-500/30"
                          : "bg-dark-bg border-dark-border"
                      }`}
                    >
                      <button
                        onClick={() =>
                          setExpandedLogIdx(isExpanded ? null : idx)
                        }
                        className="w-full p-3 text-left hover:bg-dark-surface/50 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-dark-text-primary">
                              Session {recordingLogs.length - idx}
                            </span>
                            <span className="text-xs text-dark-text-secondary bg-dark-surface px-1.5 py-0.5 rounded">
                              {eventCount} events
                            </span>
                            {hasAlerts && (
                              <AlertTriangle className="w-3.5 h-3.5 text-red-400" />
                            )}
                          </div>
                          <ChevronDown
                            className={`w-4 h-4 text-dark-text-secondary transition-transform ${
                              isExpanded ? "rotate-180" : ""
                            }`}
                          />
                        </div>
                        <div className="flex items-center gap-1.5 mt-1 text-xs text-dark-text-secondary">
                          <Calendar className="w-3 h-3" />
                          {log.session_start
                            ? formatDate(log.session_start)
                            : "Unknown date"}
                        </div>
                      </button>

                      {isExpanded && log.events && log.events.length > 0 && (
                        <div className="px-3 pb-3 border-t border-dark-border/50">
                          <div className="mt-2 space-y-2 max-h-[200px] overflow-y-auto custom-scrollbar">
                            {log.events.map((event: any, eventIdx: number) => (
                              <div
                                key={eventIdx}
                                className={`p-2.5 rounded text-xs ${
                                  event.flag === "SAFETY_ALERT"
                                    ? "bg-red-950/30 border-l-2 border-red-500"
                                    : "bg-dark-surface/50 border-l-2 border-dark-border"
                                }`}
                              >
                                <div className="flex items-center gap-2 mb-1 text-dark-text-secondary">
                                  <Clock className="w-3 h-3" />
                                  {event.timestamp
                                    ? formatTimeShort(event.timestamp)
                                    : ""}
                                  {event.flag === "SAFETY_ALERT" && (
                                    <span className="text-red-400 text-[10px] font-medium ml-auto">
                                      ALERT
                                    </span>
                                  )}
                                </div>
                                <p className="text-dark-text-primary leading-relaxed">
                                  {event.summary || "No summary"}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      <audio ref={audioRef} />

      <style>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideIn {
          animation: slideIn 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  );
}
