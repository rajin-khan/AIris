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
  Mail,
  Send,
  TestTube,
} from "lucide-react";
import { apiClient } from "../services/api";

interface SceneDescriptionProps {
  cameraOn: boolean;
  voiceOnlyMode?: boolean;
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
  riskScore: number;
}

export default function SceneDescription({
  cameraOn,
  voiceOnlyMode = false,
}: SceneDescriptionProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentDescription, setCurrentDescription] = useState("");
  const [currentSummary, setCurrentSummary] = useState("");
  const [safetyAlert, setSafetyAlert] = useState(false);
  const [riskScore, setRiskScore] = useState(0);
  const [frameUrl, setFrameUrl] = useState<string | null>(null);
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [recordingLogs, setRecordingLogs] = useState<any[]>([]);
  const [expandedLogIdx, setExpandedLogIdx] = useState<number | null>(0);
  const [analysisCountdown, setAnalysisCountdown] = useState(0.5); // 2 FPS = 0.5s intervals
  const [elapsedTime, setElapsedTime] = useState(0);
  const [currentSessionEvents, setCurrentSessionEvents] = useState<
    SummaryEvent[]
  >([]);
  const [filledFrames, setFilledFrames] = useState<number[]>([]);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);

  // Email dropdown state
  const [isMailDropdownOpen, setIsMailDropdownOpen] = useState(false);
  const [emailSending, setEmailSending] = useState<string | null>(null);
  const [emailStatus, setEmailStatus] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  // Alert notification state for FAB
  const [alertNotification, setAlertNotification] = useState<{
    show: boolean;
    message: string;
    timestamp: number;
  } | null>(null);

  const frameIntervalRef = useRef<number | null>(null);
  const mailDropdownRef = useRef<HTMLDivElement | null>(null);
  const analysisIntervalRef = useRef<number | null>(null);
  const countdownIntervalRef = useRef<number | null>(null);
  const timerIntervalRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const lastSummaryRef = useRef<string>("");
  const frameCountRef = useRef(0);

  const BUFFER_MAX = 5; // 5 frames at 2 FPS = 2.5 seconds

  useEffect(() => {
    loadLogs();
  }, []);

  // Close mail dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        mailDropdownRef.current &&
        !mailDropdownRef.current.contains(event.target as Node)
      ) {
        setIsMailDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Clear email status after 3 seconds
  useEffect(() => {
    if (emailStatus) {
      const timer = setTimeout(() => setEmailStatus(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [emailStatus]);

  const handleSendEmail = async (type: string, isDummy: boolean) => {
    const sendingKey = `${type}-${isDummy ? "dummy" : "real"}`;
    setEmailSending(sendingKey);
    setEmailStatus(null);

    try {
      let result;
      switch (type) {
        case "test":
          result = await apiClient.sendTestEmail();
          break;
        case "alert":
          // Alerts are always "test" since real alerts are triggered automatically by detections
          result = await apiClient.sendTestAlert();
          break;
        case "daily":
          if (isDummy) {
            result = await apiClient.sendTestDaily();
          } else {
            result = await apiClient.sendRealDailySummary();
          }
          break;
        case "weekly":
          if (isDummy) {
            result = await apiClient.sendTestWeekly();
          } else {
            result = await apiClient.sendRealWeeklyReport();
          }
          break;
        default:
          throw new Error("Unknown email type");
      }

      setEmailStatus({
        type: "success",
        message: result.message || "Email sent!",
      });
    } catch (error: any) {
      setEmailStatus({
        type: "error",
        message: error.response?.data?.detail || "Failed to send email",
      });
    } finally {
      setEmailSending(null);
    }
  };

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

        // Check if an alert was sent (fall alert or risk-based alert)
        const alertWasSent =
          result.alert_sent || result.fall_alert_sent || false;
        if (alertWasSent) {
          // Show notification on the FAB
          const alertType = result.fall_alert_sent
            ? "Fall Alert"
            : "Safety Alert";
          const notificationTimestamp = Date.now();
          setAlertNotification({
            show: true,
            message: `${alertType} sent to guardian`,
            timestamp: notificationTimestamp,
          });

          // Auto-hide notification after 5 seconds
          setTimeout(() => {
            setAlertNotification((prev) => {
              // Only hide if it's the same notification (timestamp matches)
              if (prev && prev.timestamp === notificationTimestamp) {
                return { ...prev, show: false };
              }
              return prev;
            });
          }, 5000);
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
              riskScore: result.risk_score || 0,
            };
            setCurrentSessionEvents((prev) => [newEvent, ...prev]);

            // Reset frame buffer visualization
            setFilledFrames([]);
            frameCountRef.current = 0;
            setIsGeneratingSummary(false);
          }, 500);
        }

        setSafetyAlert(result.safety_alert || false);
        setRiskScore(result.risk_score || 0);
        setIsRecording(result.is_recording);
        setIsProcessing(false);
        setAnalysisCountdown(0.5); // Reset for 2 FPS
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
    // At 2 FPS, we update every 0.5 seconds - countdown shows time to next summary
    countdownIntervalRef.current = window.setInterval(() => {
      setAnalysisCountdown((prev) => (prev > 0.1 ? prev - 0.5 : 2.5)); // 2.5 seconds per summary cycle
    }, 500);
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
        setRiskScore(0);
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

          {/* Risk Score Bar (when recording) */}
          {isRecording && riskScore > 0 && (
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-dark-text-secondary uppercase tracking-wider">
                  Risk Level
                </span>
                <span
                  className={`text-xs font-medium ${
                    riskScore >= 0.7
                      ? "text-red-400"
                      : riskScore >= 0.5
                      ? "text-yellow-400"
                      : "text-green-400"
                  }`}
                >
                  {(riskScore * 100).toFixed(0)}%
                </span>
              </div>
              <div className="h-1.5 bg-dark-bg rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 rounded-full ${
                    riskScore >= 0.7
                      ? "bg-red-500"
                      : riskScore >= 0.5
                      ? "bg-yellow-500"
                      : "bg-green-500"
                  }`}
                  style={{ width: `${riskScore * 100}%` }}
                />
              </div>
            </div>
          )}

          {/* Current Summary */}
          <div className="bg-dark-bg rounded-lg p-3 min-h-[60px] transition-all">
            {safetyAlert && (
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-1.5 text-red-400 text-xs">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  Safety Alert
                </div>
                <span className="text-xs text-red-400/70">
                  Risk: {(riskScore * 100).toFixed(0)}%
                </span>
              </div>
            )}
            {currentSummary ? (
              <div>
                {/* Risk Score Badge */}
                {riskScore > 0 && (
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider ${
                        riskScore >= 0.7
                          ? "bg-red-500/20 text-red-400 border border-red-500/30"
                          : riskScore >= 0.5
                          ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30"
                          : riskScore >= 0.3
                          ? "bg-orange-500/20 text-orange-400 border border-orange-500/30"
                          : "bg-green-500/20 text-green-400 border border-green-500/30"
                      }`}
                    >
                      {riskScore >= 0.7
                        ? "High Risk"
                        : riskScore >= 0.5
                        ? "Moderate Risk"
                        : riskScore >= 0.3
                        ? "Low Risk"
                        : "Safe"}
                      {" · "}
                      {(riskScore * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
                <p className="text-dark-text-primary text-sm leading-relaxed">
                  {currentSummary}
                </p>
              </div>
            ) : (
              <p className="text-dark-text-secondary text-sm opacity-60">
                Summary will appear after {BUFFER_MAX} observations (~2.5s)
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
                        {/* Risk Score Badge */}
                        <span
                          className={`px-1.5 py-0.5 rounded text-[9px] font-medium ${
                            event.riskScore >= 0.7
                              ? "bg-red-500/20 text-red-400"
                              : event.riskScore >= 0.5
                              ? "bg-yellow-500/20 text-yellow-400"
                              : event.riskScore >= 0.3
                              ? "bg-orange-500/20 text-orange-400"
                              : "bg-green-500/20 text-green-400"
                          }`}
                        >
                          {(event.riskScore * 100).toFixed(0)}%
                        </span>
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

      {/* Floating Email Actions Button */}
      <div className="fixed bottom-6 right-6 z-50" ref={mailDropdownRef}>
        {/* Dropdown Menu - opens upward */}
        {isMailDropdownOpen && (
          <div className="absolute bottom-14 right-0 w-64 bg-dark-surface border border-dark-border rounded-xl shadow-2xl overflow-hidden animate-fadeIn">
            {/* Header */}
            <div className="px-4 py-3 border-b border-dark-border bg-dark-bg/50">
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-brand-gold" />
                <span className="text-sm font-semibold text-dark-text-primary">
                  Email Actions
                </span>
              </div>
            </div>

            {/* Status Message */}
            {emailStatus && (
              <div
                className={`px-4 py-2 text-xs flex items-center gap-2 ${
                  emailStatus.type === "success"
                    ? "bg-green-500/10 text-green-400"
                    : "bg-red-500/10 text-red-400"
                }`}
              >
                {emailStatus.type === "success" ? "✓" : "✕"}{" "}
                {emailStatus.message}
              </div>
            )}

            <div className="p-3 space-y-3">
              {/* Config Test */}
              <button
                onClick={() => handleSendEmail("test", false)}
                disabled={emailSending !== null}
                className="w-full flex items-center justify-between px-3 py-2.5 rounded-lg bg-dark-bg hover:bg-dark-border/50 transition-colors disabled:opacity-50"
              >
                <span className="text-sm text-dark-text-primary">
                  Send Config Test
                </span>
                {emailSending === "test-real" ? (
                  <Loader2 className="w-4 h-4 text-brand-gold animate-spin" />
                ) : (
                  <Send className="w-4 h-4 text-dark-text-secondary" />
                )}
              </button>

              <div className="border-t border-dark-border pt-3 space-y-2">
                {/* Alert */}
                <div>
                  <div className="flex items-center justify-between px-1 mb-1.5">
                    <span className="text-[10px] text-dark-text-secondary uppercase tracking-wider">
                      Safety Alert
                    </span>
                    <span className="text-[9px] text-dark-text-secondary/50">
                      Auto on detection
                    </span>
                  </div>
                  <button
                    onClick={() => handleSendEmail("alert", true)}
                    disabled={emailSending !== null}
                    className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors disabled:opacity-50"
                  >
                    {emailSending === "alert-dummy" ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <AlertTriangle className="w-3.5 h-3.5" />
                    )}
                    <span className="text-xs font-medium">Send Test Alert</span>
                  </button>
                </div>

                {/* Daily */}
                <div>
                  <span className="text-[10px] text-dark-text-secondary uppercase tracking-wider px-1 block mb-1.5">
                    Daily Summary
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleSendEmail("daily", true)}
                      disabled={emailSending !== null}
                      className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-dark-bg hover:bg-dark-border/50 transition-colors disabled:opacity-50"
                    >
                      {emailSending === "daily-dummy" ? (
                        <Loader2 className="w-3 h-3 animate-spin text-dark-text-secondary" />
                      ) : (
                        <TestTube className="w-3 h-3 text-dark-text-secondary" />
                      )}
                      <span className="text-xs text-dark-text-secondary">
                        Dummy
                      </span>
                    </button>
                    <button
                      onClick={() => handleSendEmail("daily", false)}
                      disabled={emailSending !== null}
                      className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-brand-gold/10 hover:bg-brand-gold/20 text-brand-gold transition-colors disabled:opacity-50"
                    >
                      {emailSending === "daily-real" ? (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      ) : (
                        <Calendar className="w-3 h-3" />
                      )}
                      <span className="text-xs font-medium">Real</span>
                    </button>
                  </div>
                </div>

                {/* Weekly */}
                <div>
                  <span className="text-[10px] text-dark-text-secondary uppercase tracking-wider px-1 block mb-1.5">
                    Weekly Report
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleSendEmail("weekly", true)}
                      disabled={emailSending !== null}
                      className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-dark-bg hover:bg-dark-border/50 transition-colors disabled:opacity-50"
                    >
                      {emailSending === "weekly-dummy" ? (
                        <Loader2 className="w-3 h-3 animate-spin text-dark-text-secondary" />
                      ) : (
                        <TestTube className="w-3 h-3 text-dark-text-secondary" />
                      )}
                      <span className="text-xs text-dark-text-secondary">
                        Dummy
                      </span>
                    </button>
                    <button
                      onClick={() => handleSendEmail("weekly", false)}
                      disabled={emailSending !== null}
                      className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-brand-gold/10 hover:bg-brand-gold/20 text-brand-gold transition-colors disabled:opacity-50"
                    >
                      {emailSending === "weekly-real" ? (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      ) : (
                        <FileText className="w-3 h-3" />
                      )}
                      <span className="text-xs font-medium">Real</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Alert Toast Notification */}
        {alertNotification?.show && (
          <div className="absolute bottom-16 right-0 mb-2 animate-alertToast">
            <div className="bg-red-600 text-white px-4 py-2.5 rounded-xl shadow-lg flex items-center gap-2 whitespace-nowrap">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span className="text-sm font-medium">
                {alertNotification.message}
              </span>
            </div>
            {/* Arrow pointing down to FAB */}
            <div className="absolute -bottom-1.5 right-5 w-3 h-3 bg-red-600 rotate-45"></div>
          </div>
        )}

        {/* Floating Action Button */}
        <button
          onClick={() => {
            setIsMailDropdownOpen(!isMailDropdownOpen);
            // Clear notification when clicking the FAB
            if (alertNotification?.show) {
              setAlertNotification(null);
            }
          }}
          className={`relative w-12 h-12 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 ${
            isMailDropdownOpen
              ? "bg-brand-gold text-brand-charcoal rotate-45"
              : alertNotification?.show
              ? "bg-red-600 text-white border-2 border-red-400 animate-pulse"
              : "bg-dark-surface border border-dark-border text-dark-text-secondary hover:border-brand-gold hover:text-brand-gold"
          }`}
        >
          {isMailDropdownOpen ? (
            <span className="text-xl font-light">+</span>
          ) : (
            <>
              <Mail className="w-5 h-5" />
              {/* Red notification dot */}
              {alertNotification?.show && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-white rounded-full flex items-center justify-center shadow-md">
                  <span className="w-2.5 h-2.5 bg-red-500 rounded-full animate-ping-slow"></span>
                </span>
              )}
            </>
          )}
        </button>
      </div>

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
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.2s ease-out forwards;
        }
        @keyframes alertToast {
          from {
            opacity: 0;
            transform: translateY(10px) scale(0.95);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
        .animate-alertToast {
          animation: alertToast 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        }
        @keyframes ping-slow {
          0% {
            transform: scale(1);
            opacity: 1;
          }
          50% {
            transform: scale(1.3);
            opacity: 0.7;
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }
        .animate-ping-slow {
          animation: ping-slow 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
      `}</style>
    </div>
  );
}
