import { useState, useEffect } from "react";
import {
  X,
  Save,
  Wifi,
  Radio,
  Monitor,
  AlertCircle,
  CheckCircle2,
  Loader2,
  Laptop,
  Cpu,
  Camera,
  Mic,
  Speaker,
  Construction,
} from "lucide-react";
import { apiClient } from "../services/api";

interface HardwareSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  hardwareMode: "local" | "physical";
  onHardwareModeChange: (mode: "local" | "physical") => void;
}

type ESP32Mode = "live-stream" | "setup-wifi";
type SettingsTab = "camera" | "microphone" | "speaker";

export default function HardwareSettings({
  isOpen,
  onClose,
  hardwareMode,
  onHardwareModeChange,
}: HardwareSettingsProps) {
  const [activeTab, setActiveTab] = useState<SettingsTab>("camera");
  const [esp32Mode, setEsp32Mode] = useState<ESP32Mode>("live-stream");
  const [ipAddress, setIpAddress] = useState("");
  const [wifiSSID, setWifiSSID] = useState("");
  const [wifiPassword, setWifiPassword] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [isProvisioning, setIsProvisioning] = useState(false);
  const [provisionStatus, setProvisionStatus] = useState<{
    type: "success" | "error" | null;
    message: string;
  }>({ type: null, message: "" });

  // Auto-configure webcam when switching to local mode
  useEffect(() => {
    if (hardwareMode === "local") {
      apiClient.setCameraConfig("webcam").catch(console.error);
    }
  }, [hardwareMode]);

  if (!isOpen) return null;

  const handleSave = async () => {
    setIsSaving(true);
    try {
      if (hardwareMode === "physical") {
        await apiClient.setCameraConfig("esp32", ipAddress);
      }
      onClose();
    } catch (error) {
      console.error("Failed to save settings:", error);
      alert("Failed to save settings");
    } finally {
      setIsSaving(false);
    }
  };

  const handleWiFiProvisioning = async () => {
    if (!wifiSSID.trim()) {
      setProvisionStatus({
        type: "error",
        message: "Please enter a WiFi SSID",
      });
      return;
    }

    setIsProvisioning(true);
    setProvisionStatus({ type: null, message: "" });

    try {
      const result = await apiClient.provisionESP32WiFi(wifiSSID, wifiPassword);
      if (result.success) {
        setProvisionStatus({
          type: "success",
          message:
            "Credentials received! The camera is restarting. Please reconnect your PC to your Home WiFi now.",
        });
        setWifiSSID("");
        setWifiPassword("");
      } else {
        setProvisionStatus({
          type: "error",
          message: result.message || "Failed to send WiFi credentials",
        });
      }
    } catch (error: any) {
      console.error("WiFi provisioning error:", error);
      setProvisionStatus({
        type: "error",
        message:
          error.message ||
          "Connection failed. Are you connected to ESP32-CAM-SETUP network?",
      });
    } finally {
      setIsProvisioning(false);
    }
  };

  const handleModeChange = (mode: "local" | "physical") => {
    onHardwareModeChange(mode);
    setProvisionStatus({ type: null, message: "" });
  };

  const tabs: { id: SettingsTab; label: string; icon: React.ReactNode }[] = [
    { id: "camera", label: "Camera", icon: <Camera className="w-4 h-4" /> },
    { id: "microphone", label: "Microphone", icon: <Mic className="w-4 h-4" /> },
    { id: "speaker", label: "Speaker", icon: <Speaker className="w-4 h-4" /> },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-dark-surface border border-dark-border rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto custom-scrollbar shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-dark-surface border-b border-dark-border p-6 flex items-center justify-between z-10">
          <h2 className="text-2xl font-semibold text-dark-text-primary font-heading">
            Hardware Settings
          </h2>
          <button
            onClick={onClose}
            className="text-dark-text-secondary hover:text-dark-text-primary transition-colors p-1 hover:bg-dark-bg rounded-lg"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Hardware Mode Selection */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-dark-text-secondary uppercase tracking-wider">
              Hardware Mode
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleModeChange("local")}
                className={`p-4 rounded-xl border-2 transition-all flex flex-col items-center justify-center gap-2 ${
                  hardwareMode === "local"
                    ? "border-brand-gold bg-brand-gold/10 text-brand-gold"
                    : "border-dark-border bg-dark-bg text-dark-text-secondary hover:border-dark-text-secondary hover:bg-dark-surface"
                }`}
              >
                <Laptop className="w-6 h-6" />
                <span className="font-medium">Local</span>
                <span className="text-xs opacity-70">Laptop Camera, Mic, Speaker</span>
              </button>
              <button
                onClick={() => handleModeChange("physical")}
                className={`p-4 rounded-xl border-2 transition-all flex flex-col items-center justify-center gap-2 ${
                  hardwareMode === "physical"
                    ? "border-brand-gold bg-brand-gold/10 text-brand-gold"
                    : "border-dark-border bg-dark-bg text-dark-text-secondary hover:border-dark-text-secondary hover:bg-dark-surface"
                }`}
              >
                <Cpu className="w-6 h-6" />
                <span className="font-medium">Physical</span>
                <span className="text-xs opacity-70">ESP32 Cam, BT Mic/Speaker</span>
              </button>
            </div>
          </div>

          {/* Local Mode Content */}
          {hardwareMode === "local" && (
            <div className="p-6 bg-dark-bg rounded-xl border border-dark-border text-center space-y-4">
              <div className="w-16 h-16 mx-auto rounded-full bg-brand-gold/10 flex items-center justify-center">
                <Laptop className="w-8 h-8 text-brand-gold" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-dark-text-primary font-heading">
                  Using Local Hardware
                </h3>
                <p className="text-dark-text-secondary mt-2 text-sm">
                  The system will use your laptop's built-in camera, microphone, and speakers.
                  No additional configuration is required.
                </p>
              </div>
              <div className="flex items-center justify-center gap-2 text-green-400 text-sm">
                <CheckCircle2 className="w-4 h-4" />
                <span>Ready to use</span>
              </div>
            </div>
          )}

          {/* Physical Mode Content */}
          {hardwareMode === "physical" && (
            <div className="space-y-4">
              {/* Tab Navigation */}
              <div className="flex gap-1 p-1 bg-dark-bg rounded-xl border border-dark-border">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      activeTab === tab.id
                        ? "bg-brand-gold text-brand-charcoal"
                        : "text-dark-text-secondary hover:text-dark-text-primary hover:bg-dark-surface"
                    }`}
                  >
                    {tab.icon}
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Camera Tab */}
              {activeTab === "camera" && (
                <div className="space-y-4 animate-in fade-in slide-in-from-top-2">
                  {/* ESP32 Mode Selection */}
                  <div className="space-y-3">
                    <label className="text-sm font-medium text-dark-text-secondary uppercase tracking-wider">
                      ESP32 Camera Mode
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        onClick={() => {
                          setEsp32Mode("live-stream");
                          setProvisionStatus({ type: null, message: "" });
                        }}
                        className={`p-3 rounded-xl border-2 transition-all ${
                          esp32Mode === "live-stream"
                            ? "border-brand-gold bg-brand-gold/10 text-brand-gold"
                            : "border-dark-border bg-dark-bg text-dark-text-secondary hover:border-dark-text-secondary"
                        }`}
                      >
                        Live Stream
                      </button>
                      <button
                        onClick={() => {
                          setEsp32Mode("setup-wifi");
                          setProvisionStatus({ type: null, message: "" });
                        }}
                        className={`p-3 rounded-xl border-2 transition-all ${
                          esp32Mode === "setup-wifi"
                            ? "border-brand-gold bg-brand-gold/10 text-brand-gold"
                            : "border-dark-border bg-dark-bg text-dark-text-secondary hover:border-dark-text-secondary"
                        }`}
                      >
                        Setup WiFi
                      </button>
                    </div>
                  </div>

                  {/* Live Stream Mode */}
                  {esp32Mode === "live-stream" && (
                    <div className="space-y-4 p-4 bg-dark-bg rounded-xl border border-dark-border">
                      <div className="flex items-center gap-2 mb-2">
                        <Monitor className="w-5 h-5 text-brand-gold" />
                        <h3 className="text-lg font-semibold text-dark-text-primary font-heading">
                          Step 2: Live Monitor
                        </h3>
                      </div>

                      <div className="space-y-3">
                        <label className="text-sm font-medium text-dark-text-secondary">
                          Camera IP Address
                        </label>
                        <div className="relative">
                          <Wifi className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-text-secondary" />
                          <input
                            type="text"
                            value={ipAddress}
                            onChange={(e) => setIpAddress(e.target.value)}
                            placeholder="e.g. 192.168.1.100"
                            className="w-full pl-10 pr-4 py-3 bg-dark-surface border border-dark-border rounded-xl text-dark-text-primary placeholder-dark-text-secondary focus:outline-none focus:border-brand-gold transition-colors"
                          />
                        </div>
                        <div className="bg-dark-surface/50 rounded-lg p-3 border border-dark-border">
                          <p className="text-xs text-dark-text-secondary leading-relaxed">
                            <span className="font-semibold text-dark-text-primary">
                              Note:
                            </span>{" "}
                            Enter the IP address shown in the Arduino Serial
                            Monitor. Ensure your PC and the Camera are on the same
                            WiFi network for streaming.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* WiFi Setup Mode */}
                  {esp32Mode === "setup-wifi" && (
                    <div className="space-y-4 p-4 bg-dark-bg rounded-xl border border-dark-border">
                      <div className="flex items-center gap-2 mb-2">
                        <Wifi className="w-5 h-5 text-brand-gold" />
                        <h3 className="text-lg font-semibold text-dark-text-primary font-heading">
                          Step 1: WiFi Provisioning
                        </h3>
                      </div>

                      {/* Instructions */}
                      <div className="bg-brand-gold/10 border border-brand-gold/30 rounded-xl p-4 space-y-2">
                        <div className="flex items-start gap-2">
                          <AlertCircle className="w-5 h-5 text-brand-gold flex-shrink-0 mt-0.5" />
                          <div className="space-y-1.5 text-sm text-dark-text-primary">
                            <p className="font-semibold">Instructions:</p>
                            <ol className="list-decimal list-inside space-y-1 text-dark-text-secondary">
                              <li>Power on your ESP32-CAM.</li>
                              <li>
                                Connect your PC's WiFi to the network named{" "}
                                <span className="font-semibold text-brand-gold">
                                  ESP32-CAM-SETUP
                                </span>
                                .
                              </li>
                              <li>Enter your Home WiFi credentials below.</li>
                              <li>Click 'Send Configuration'.</li>
                            </ol>
                          </div>
                        </div>
                      </div>

                      {/* WiFi Credentials Form */}
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <label className="text-sm font-medium text-dark-text-secondary">
                            Home WiFi SSID
                          </label>
                          <input
                            type="text"
                            value={wifiSSID}
                            onChange={(e) => setWifiSSID(e.target.value)}
                            placeholder="Enter your WiFi network name"
                            className="w-full px-4 py-3 bg-dark-surface border border-dark-border rounded-xl text-dark-text-primary placeholder-dark-text-secondary focus:outline-none focus:border-brand-gold transition-colors"
                            disabled={isProvisioning}
                          />
                        </div>

                        <div className="space-y-2">
                          <label className="text-sm font-medium text-dark-text-secondary">
                            WiFi Password
                          </label>
                          <input
                            type="password"
                            value={wifiPassword}
                            onChange={(e) => setWifiPassword(e.target.value)}
                            placeholder="Enter your WiFi password (optional)"
                            className="w-full px-4 py-3 bg-dark-surface border border-dark-border rounded-xl text-dark-text-primary placeholder-dark-text-secondary focus:outline-none focus:border-brand-gold transition-colors"
                            disabled={isProvisioning}
                          />
                        </div>

                        {/* Provision Status */}
                        {provisionStatus.type && (
                          <div
                            className={`rounded-xl p-4 border-2 flex items-start gap-3 ${
                              provisionStatus.type === "success"
                                ? "bg-green-500/10 border-green-500/30"
                                : "bg-red-500/10 border-red-500/30"
                            }`}
                          >
                            {provisionStatus.type === "success" ? (
                              <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                            ) : (
                              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                            )}
                            <p
                              className={`text-sm ${
                                provisionStatus.type === "success"
                                  ? "text-green-300"
                                  : "text-red-300"
                              }`}
                            >
                              {provisionStatus.message}
                            </p>
                          </div>
                        )}

                        {/* Send Configuration Button */}
                        <button
                          onClick={handleWiFiProvisioning}
                          disabled={isProvisioning || !wifiSSID.trim()}
                          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-brand-gold text-brand-charcoal rounded-xl font-semibold hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                          {isProvisioning ? (
                            <>
                              <Loader2 className="w-5 h-5 animate-spin" />
                              Sending Configuration...
                            </>
                          ) : (
                            <>
                              <Wifi className="w-5 h-5" />
                              Send Configuration
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Microphone Tab - Placeholder */}
              {activeTab === "microphone" && (
                <div className="p-8 bg-dark-bg rounded-xl border border-dark-border text-center space-y-4">
                  <div className="w-16 h-16 mx-auto rounded-full bg-dark-surface flex items-center justify-center">
                    <Construction className="w-8 h-8 text-dark-text-secondary" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-dark-text-primary font-heading">
                      Microphone Configuration
                    </h3>
                    <p className="text-dark-text-secondary mt-2 text-sm">
                      Bluetooth microphone settings will be available here once hardware integration is complete.
                    </p>
                  </div>
                  <div className="p-4 bg-dark-surface rounded-lg border border-dark-border">
                    <p className="text-xs text-dark-text-secondary">
                      <span className="font-semibold text-brand-gold">Coming Soon:</span> Connect and configure your Arduino Bluetooth microphone for voice commands and speech-to-text.
                    </p>
                  </div>
                </div>
              )}

              {/* Speaker Tab - Placeholder */}
              {activeTab === "speaker" && (
                <div className="p-8 bg-dark-bg rounded-xl border border-dark-border text-center space-y-4">
                  <div className="w-16 h-16 mx-auto rounded-full bg-dark-surface flex items-center justify-center">
                    <Construction className="w-8 h-8 text-dark-text-secondary" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-dark-text-primary font-heading">
                      Speaker Configuration
                    </h3>
                    <p className="text-dark-text-secondary mt-2 text-sm">
                      Bluetooth speaker settings will be available here once hardware integration is complete.
                    </p>
                  </div>
                  <div className="p-4 bg-dark-surface rounded-lg border border-dark-border">
                    <p className="text-xs text-dark-text-secondary">
                      <span className="font-semibold text-brand-gold">Coming Soon:</span> Connect and configure your Arduino Bluetooth speaker for text-to-speech guidance output.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Save Button - Only show for Physical mode with Live Stream */}
          {hardwareMode === "physical" && activeTab === "camera" && esp32Mode === "live-stream" && (
            <div className="flex justify-end pt-4 border-t border-dark-border">
              <button
                onClick={handleSave}
                disabled={isSaving || !ipAddress.trim()}
                className="flex items-center gap-2 px-6 py-3 bg-brand-gold text-brand-charcoal rounded-xl font-semibold hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Save Settings
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

