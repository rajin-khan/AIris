import { useState, useEffect, useRef } from "react";
import { Camera, CameraOff, Settings, Mic, MicOff } from "lucide-react";
import ActivityGuide from "./components/ActivityGuide";
import SceneDescription from "./components/SceneDescription";
import HardwareSettings from "./components/HardwareSettings";
import { apiClient } from "./services/api";
import { getVoiceControlService } from "./services/voiceControl";

type Mode = "Activity Guide" | "Scene Description";
type CameraSource = "local" | "esp32";

function App() {
  const [mode, setMode] = useState<Mode>("Activity Guide");
  const [cameraOn, setCameraOn] = useState(false);
  const [cameraStatus, setCameraStatus] = useState({
    is_running: false,
    is_available: false,
  });
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showSettings, setShowSettings] = useState(false);
  const [cameraSource, setCameraSource] = useState<CameraSource>(() => {
    const saved = localStorage.getItem("airis-camera-source");
    return (saved === "esp32" ? "esp32" : "local") as CameraSource;
  });
  const [voiceOnlyMode, setVoiceOnlyMode] = useState(false); // Always default to OFF
  const voiceControlRef = useRef(getVoiceControlService());
  const modeButtonRefs = {
    "Activity Guide": useRef<HTMLButtonElement>(null),
    "Scene Description": useRef<HTMLButtonElement>(null),
  };
  const cameraButtonRef = useRef<HTMLButtonElement>(null);
  const lastCameraAnnouncementRef = useRef<{
    state: boolean | null;
    timestamp: number;
  }>({ state: null, timestamp: 0 });
  const lastModeAnnouncementRef = useRef<{
    mode: Mode | null;
    timestamp: number;
  }>({ mode: null, timestamp: 0 });

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    checkCameraStatus();
  }, []);

  useEffect(() => {
    localStorage.setItem("airis-camera-source", cameraSource);
  }, [cameraSource]);

  // Note: Voice-only mode always defaults to OFF and is not persisted to localStorage
  // This ensures a clean state on every page load

  // Voice control setup - only active when voiceOnlyMode is ON
  useEffect(() => {
    const voiceControl = voiceControlRef.current;

    if (!voiceOnlyMode) {
      // Voice-only mode is OFF - stop all voice/TTS activity
      console.log(
        `[App] Voice-only mode disabled, stopping all voice/TTS activity`
      );
      voiceControl.stopListening();
      voiceControl.stopSpeaking();
      return;
    }

    // Voice-only mode is ON - start listening
    console.log(
      `[App] Starting voice control listening. Mode: ${mode}, Camera: ${cameraOn}`
    );
    voiceControl.startListening((command, transcript) => {
      console.log(
        `[App] Voice command received: ${command} - "${transcript}"`,
        {
          mode,
          cameraOn,
          hasActivityGuideButton: !!modeButtonRefs["Activity Guide"].current,
          hasSceneDescriptionButton:
            !!modeButtonRefs["Scene Description"].current,
          hasCameraButton: !!cameraButtonRef.current,
        }
      );

      switch (command) {
        case "switch_mode":
          console.log(`[App] Processing switch_mode command`);
          if (transcript.includes("activity guide")) {
            if (
              mode !== "Activity Guide" &&
              modeButtonRefs["Activity Guide"].current
            ) {
              console.log(`[App] Switching to Activity Guide mode`);
              modeButtonRefs["Activity Guide"].current?.click();
            } else {
              console.log(`[App] Cannot switch to Activity Guide:`, {
                currentMode: mode,
                hasButton: !!modeButtonRefs["Activity Guide"].current,
              });
            }
          } else if (transcript.includes("scene description")) {
            if (
              mode !== "Scene Description" &&
              modeButtonRefs["Scene Description"].current
            ) {
              console.log(`[App] Switching to Scene Description mode`);
              modeButtonRefs["Scene Description"].current?.click();
            } else {
              console.log(`[App] Cannot switch to Scene Description:`, {
                currentMode: mode,
                hasButton: !!modeButtonRefs["Scene Description"].current,
              });
            }
          }
          break;

        case "camera_on":
          console.log(`[App] Processing camera_on command`);
          if (!cameraOn && cameraButtonRef.current) {
            console.log(`[App] Turning camera on`);
            cameraButtonRef.current.click();
          } else {
            console.log(`[App] Cannot turn camera on:`, {
              cameraOn,
              hasButton: !!cameraButtonRef.current,
            });
          }
          break;

        case "camera_off":
          console.log(`[App] Processing camera_off command`);
          if (cameraOn && cameraButtonRef.current) {
            console.log(`[App] Turning camera off`);
            cameraButtonRef.current.click();
          } else {
            console.log(`[App] Cannot turn camera off:`, {
              cameraOn,
              hasButton: !!cameraButtonRef.current,
            });
          }
          break;

        default:
          console.log(`[App] Unhandled command: ${command}`);
      }
    });

    return () => {
      // Cleanup: stop listening when voice-only mode is disabled or component unmounts
      voiceControl.stopListening();
    };
  }, [voiceOnlyMode, mode, cameraOn]);

  // Announce mode changes in voice-only mode
  useEffect(() => {
    if (!voiceOnlyMode) {
      return; // Don't announce if voice-only mode is off
    }

    const now = Date.now();
    const timeSinceLastAnnouncement =
      now - lastModeAnnouncementRef.current.timestamp;
    const lastAnnouncedMode = lastModeAnnouncementRef.current.mode;

    // Only announce if:
    // 1. We haven't announced this mode before, OR
    // 2. The last announcement was for a different mode, OR
    // 3. It's been more than 2 seconds since the last announcement
    if (lastAnnouncedMode !== mode || timeSinceLastAnnouncement > 2000) {
      voiceControlRef.current.markUserInteracted(); // Ensure audio can play
      const message =
        mode === "Activity Guide"
          ? "Activity Guide mode"
          : "Scene Description mode";
      voiceControlRef.current.speakText(message, false);
      lastModeAnnouncementRef.current = { mode, timestamp: now };
    }
  }, [mode, voiceOnlyMode]);

  useEffect(() => {
    if (cameraSource === "local") {
      apiClient.setCameraConfig("webcam").catch(console.error);
    }
  }, []);

  const handleCameraSourceChange = (newSource: CameraSource) => {
    setCameraSource(newSource);
    if (newSource === "local") {
      apiClient.setCameraConfig("webcam").catch(console.error);
    }
  };

  const checkCameraStatus = async () => {
    try {
      const status = await apiClient.getCameraStatus();
      setCameraStatus(status);
    } catch (error) {
      console.error("Failed to check camera status:", error);
    }
  };

  const handleCameraToggle = async () => {
    try {
      const newCameraState = !cameraOn;
      const now = Date.now();

      if (cameraOn) {
        await apiClient.stopCamera();
        setCameraOn(false);
      } else {
        await apiClient.startCamera();
        setCameraOn(true);
      }
      await checkCameraStatus();

      // Audio cue: Only announce if we haven't announced this state recently (within 2 seconds)
      // This prevents duplicate announcements from multiple rapid calls
      if (voiceOnlyMode) {
        const timeSinceLastAnnouncement =
          now - lastCameraAnnouncementRef.current.timestamp;
        const lastAnnouncedState = lastCameraAnnouncementRef.current.state;

        // Only announce if:
        // 1. We haven't announced this state before, OR
        // 2. The last announcement was for a different state, OR
        // 3. It's been more than 2 seconds since the last announcement
        if (
          lastAnnouncedState !== newCameraState ||
          timeSinceLastAnnouncement > 2000
        ) {
          voiceControlRef.current.markUserInteracted(); // Ensure audio can play
          const message = newCameraState ? "Camera is on" : "Camera is off";
          voiceControlRef.current.speakText(message, false);
          lastCameraAnnouncementRef.current = {
            state: newCameraState,
            timestamp: now,
          };
        }
      }
    } catch (error) {
      console.error("Failed to toggle camera:", error);
      alert("Failed to toggle camera. Please check your camera permissions.");
      // Audio cue for error (only in voice-only mode)
      if (voiceOnlyMode) {
        const now = Date.now();
        const timeSinceLastAnnouncement =
          now - lastCameraAnnouncementRef.current.timestamp;
        if (timeSinceLastAnnouncement > 2000) {
          voiceControlRef.current.markUserInteracted();
          voiceControlRef.current.speakText("Failed to toggle camera", false);
          lastCameraAnnouncementRef.current = { state: null, timestamp: now };
        }
      }
    }
  };

  return (
    <div className="w-full h-screen bg-dark-bg flex flex-col font-sans text-dark-text-primary overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between px-6 md:px-10 py-5 border-b border-dark-border flex-shrink-0">
        <h1 className="text-3xl font-semibold text-dark-text-primary tracking-logo font-heading">
          A<span className="text-2xl align-middle opacity-80">IRIS</span>
        </h1>

        <div className="flex items-center space-x-4 md:space-x-6">
          {/* Voice Only Mode Toggle */}
          <button
            onClick={() => {
              const newMode = !voiceOnlyMode;
              setVoiceOnlyMode(newMode);
              // Mark user interaction for audio playback when enabling voice mode
              if (newMode) {
                // Mark interaction FIRST, then speak
                voiceControlRef.current.markUserInteracted();

                // Speak welcome message and instructions after a short delay
                setTimeout(() => {
                  const modeName =
                    mode === "Activity Guide"
                      ? "Activity Guide"
                      : "Scene Description";
                  let welcomeMessage = `Voice mode enabled. You are in ${modeName} mode. `;

                  if (cameraOn) {
                    welcomeMessage += `Camera is on. `;
                  } else {
                    welcomeMessage += `Say "turn on camera" to start the camera. `;
                  }

                  if (mode === "Activity Guide") {
                    welcomeMessage += `Say "input task" to enter a task. Say "start task" to begin a task.`;
                  } else {
                    welcomeMessage += `Say "start recording" to begin scene description.`;
                  }

                  console.log(
                    "[App] Speaking welcome message:",
                    welcomeMessage
                  );
                  voiceControlRef.current.speakText(welcomeMessage, false);
                }, 500); // Delay to ensure everything is initialized
              } else {
                // When disabling, stop all voice/TTS activity
                voiceControlRef.current.stopListening();
                voiceControlRef.current.stopSpeaking();
              }
            }}
            title={
              voiceOnlyMode
                ? "Disable Voice Only Mode"
                : "Enable Voice Only Mode"
            }
            className={`p-2.5 rounded-xl border-2 transition-all duration-300 ${
              voiceOnlyMode
                ? "bg-brand-gold text-brand-charcoal border-brand-gold"
                : "border-dark-border bg-dark-surface text-dark-text-secondary hover:border-brand-gold hover:text-brand-gold"
            }`}
          >
            {voiceOnlyMode ? (
              <Mic className="w-5 h-5" />
            ) : (
              <MicOff className="w-5 h-5" />
            )}
          </button>

          {/* Mode Selection */}
          <div className="flex items-center space-x-2 bg-dark-surface rounded-xl p-1 border border-dark-border">
            <button
              ref={modeButtonRefs["Activity Guide"]}
              onClick={() => setMode("Activity Guide")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                mode === "Activity Guide"
                  ? "bg-brand-gold text-brand-charcoal"
                  : "text-dark-text-secondary hover:text-dark-text-primary"
              }`}
            >
              Activity Guide
            </button>
            <button
              ref={modeButtonRefs["Scene Description"]}
              onClick={() => setMode("Scene Description")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                mode === "Scene Description"
                  ? "bg-brand-gold text-brand-charcoal"
                  : "text-dark-text-secondary hover:text-dark-text-primary"
              }`}
            >
              Scene Description
            </button>
          </div>

          {/* Camera Settings */}
          <button
            onClick={() => setShowSettings(true)}
            title="Camera Settings"
            className="p-2.5 rounded-xl border-2 border-dark-border bg-dark-surface text-dark-text-secondary hover:border-brand-gold hover:text-brand-gold transition-all duration-300"
          >
            <Settings className="w-5 h-5" />
          </button>

          {/* Camera Toggle */}
          <button
            ref={cameraButtonRef}
            onClick={handleCameraToggle}
            title={cameraOn ? "Turn Camera Off" : "Turn Camera On"}
            className={`p-2.5 rounded-xl border-2 transition-all duration-300 ${
              cameraOn
                ? "border-dark-border text-dark-text-secondary hover:border-brand-gold hover:text-brand-gold"
                : "border-dark-border bg-dark-surface text-dark-text-secondary"
            }`}
          >
            {cameraOn ? (
              <Camera className="w-5 h-5" />
            ) : (
              <CameraOff className="w-5 h-5" />
            )}
          </button>

          {/* Status Indicator */}
          <div className="flex items-center space-x-2">
            <div
              className={`w-2.5 h-2.5 rounded-full ${
                cameraStatus.is_running
                  ? "bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.5)]"
                  : "bg-gray-500"
              }`}
            ></div>
            <span className="font-medium text-dark-text-secondary hidden sm:block text-sm">
              {cameraStatus.is_running ? "System Active" : "System Inactive"}
            </span>
          </div>

          {/* Time */}
          <div className="text-dark-text-primary font-medium text-base">
            {currentTime.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        {mode === "Activity Guide" ? (
          <ActivityGuide cameraOn={cameraOn} voiceOnlyMode={voiceOnlyMode} />
        ) : (
          <SceneDescription cameraOn={cameraOn} voiceOnlyMode={voiceOnlyMode} />
        )}
      </main>

      {/* Settings Modal */}
      <HardwareSettings
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        cameraSource={cameraSource}
        onCameraSourceChange={handleCameraSourceChange}
      />
    </div>
  );
}

export default App;
