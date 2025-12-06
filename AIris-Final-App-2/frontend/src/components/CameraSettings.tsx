import { useState } from "react";
import {
  X,
  Save,
  Wifi,
  Radio,
  Monitor,
  AlertCircle,
  CheckCircle2,
  Loader2,
} from "lucide-react";
import { apiClient } from "../services/api";

interface CameraSettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

type ESP32Mode = "live-stream" | "setup-wifi";

export default function CameraSettings({
  isOpen,
  onClose,
}: CameraSettingsProps) {
  const [sourceType, setSourceType] = useState<"webcam" | "esp32">("webcam");
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

  if (!isOpen) return null;

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await apiClient.setCameraConfig(sourceType, ipAddress);
      onClose();
    } catch (error) {
      console.error("Failed to save camera settings:", error);
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
        // Clear form after success
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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-dark-surface border border-dark-border rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto custom-scrollbar shadow-2xl">
        <div className="sticky top-0 bg-dark-surface border-b border-dark-border p-6 flex items-center justify-between z-10">
          <h2 className="text-2xl font-semibold text-dark-text-primary font-heading">
            Camera Settings
          </h2>
          <button
            onClick={onClose}
            className="text-dark-text-secondary hover:text-dark-text-primary transition-colors p-1 hover:bg-dark-bg rounded-lg"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Source Selection */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-dark-text-secondary uppercase tracking-wider">
              Camera Source
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => {
                  setSourceType("webcam");
                  setEsp32Mode("live-stream");
                  setProvisionStatus({ type: null, message: "" });
                }}
                className={`p-4 rounded-xl border-2 transition-all flex items-center justify-center gap-2 ${
                  sourceType === "webcam"
                    ? "border-brand-gold bg-brand-gold/10 text-brand-gold"
                    : "border-dark-border bg-dark-bg text-dark-text-secondary hover:border-dark-text-secondary hover:bg-dark-surface"
                }`}
              >
                <Monitor className="w-5 h-5" />
                <span className="font-medium">Webcam</span>
              </button>
              <button
                onClick={() => {
                  setSourceType("esp32");
                  setProvisionStatus({ type: null, message: "" });
                }}
                className={`p-4 rounded-xl border-2 transition-all flex items-center justify-center gap-2 ${
                  sourceType === "esp32"
                    ? "border-brand-gold bg-brand-gold/10 text-brand-gold"
                    : "border-dark-border bg-dark-bg text-dark-text-secondary hover:border-dark-text-secondary hover:bg-dark-surface"
                }`}
              >
                <Radio className="w-5 h-5" />
                <span className="font-medium">ESP32 WiFi Cam</span>
              </button>
            </div>
          </div>

          {/* ESP32 Settings */}
          {sourceType === "esp32" && (
            <div className="space-y-6 animate-in fade-in slide-in-from-top-2">
              {/* Mode Selection */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-dark-text-secondary uppercase tracking-wider">
                  ESP32 Mode
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

          {/* Actions - Only show Save for Live Stream mode */}
          {sourceType === "webcam" ||
          (sourceType === "esp32" && esp32Mode === "live-stream") ? (
            <div className="flex justify-end pt-4 border-t border-dark-border">
              <button
                onClick={handleSave}
                disabled={
                  isSaving || (sourceType === "esp32" && !ipAddress.trim())
                }
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
          ) : null}
        </div>
      </div>
    </div>
  );
}
