import { useState, useEffect } from "react";
import {
  X,
  Save,
  Wifi,
  Monitor,
  AlertCircle,
  CheckCircle2,
  Loader2,
  Laptop,
  Cpu,
} from "lucide-react";
import { apiClient } from "../services/api";

interface HardwareSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  cameraSource: "local" | "esp32";
  onCameraSourceChange: (source: "local" | "esp32") => void;
}

type ESP32Mode = "live-stream" | "setup-wifi";

export default function HardwareSettings({
  isOpen,
  onClose,
  cameraSource,
  onCameraSourceChange,
}: HardwareSettingsProps) {
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
    if (cameraSource === "local") {
      apiClient.setCameraConfig("webcam").catch(console.error);
    }
  }, [cameraSource]);

  if (!isOpen) return null;

  const handleSave = async () => {
    setIsSaving(true);
    try {
      if (cameraSource === "esp32") {
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

  const handleSourceChange = (source: "local" | "esp32") => {
    onCameraSourceChange(source);
    setProvisionStatus({ type: null, message: "" });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-dark-surface border border-dark-border rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto custom-scrollbar shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-dark-surface border-b border-dark-border p-5 flex items-center justify-between z-10">
          <h2 className="text-xl font-semibold text-dark-text-primary font-heading">
            Camera Settings
          </h2>
          <button
            onClick={onClose}
            className="text-dark-text-secondary hover:text-dark-text-primary transition-colors p-1 hover:bg-dark-bg rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 space-y-5">
          {/* Camera Source Selection */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-dark-text-secondary uppercase tracking-wider">
              Camera Source
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleSourceChange("local")}
                className={`p-4 rounded-xl border-2 transition-all flex flex-col items-center justify-center gap-2 ${
                  cameraSource === "local"
                    ? "border-brand-gold bg-brand-gold/10 text-brand-gold"
                    : "border-dark-border bg-dark-bg text-dark-text-secondary hover:border-dark-text-secondary hover:bg-dark-surface"
                }`}
              >
                <Laptop className="w-6 h-6" />
                <span className="font-medium">Local Camera</span>
                <span className="text-xs opacity-70">Laptop Webcam</span>
              </button>
              <button
                onClick={() => handleSourceChange("esp32")}
                className={`p-4 rounded-xl border-2 transition-all flex flex-col items-center justify-center gap-2 ${
                  cameraSource === "esp32"
                    ? "border-brand-gold bg-brand-gold/10 text-brand-gold"
                    : "border-dark-border bg-dark-bg text-dark-text-secondary hover:border-dark-text-secondary hover:bg-dark-surface"
                }`}
              >
                <Cpu className="w-6 h-6" />
                <span className="font-medium">ESP32-CAM</span>
                <span className="text-xs opacity-70">WiFi Module</span>
              </button>
            </div>
          </div>

          {/* Local Mode - Simple confirmation */}
          {cameraSource === "local" && (
            <div className="p-5 bg-dark-bg rounded-xl border border-dark-border text-center space-y-3">
              <div className="w-14 h-14 mx-auto rounded-full bg-brand-gold/10 flex items-center justify-center">
                <Laptop className="w-7 h-7 text-brand-gold" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-dark-text-primary font-heading">
                  Using Laptop Camera
                </h3>
                <p className="text-dark-text-secondary mt-1.5 text-sm">
                  The system will use your laptop's built-in webcam. No additional configuration required.
                </p>
              </div>
              <div className="flex items-center justify-center gap-2 text-green-400 text-sm">
                <CheckCircle2 className="w-4 h-4" />
                <span>Ready to use</span>
              </div>
            </div>
          )}

          {/* ESP32 Mode - Configuration */}
          {cameraSource === "esp32" && (
            <div className="space-y-4">
              {/* ESP32 Mode Selection */}
              <div className="flex gap-2 p-1 bg-dark-bg rounded-xl border border-dark-border">
                <button
                  onClick={() => {
                    setEsp32Mode("live-stream");
                    setProvisionStatus({ type: null, message: "" });
                  }}
                  className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    esp32Mode === "live-stream"
                      ? "bg-brand-gold text-brand-charcoal"
                      : "text-dark-text-secondary hover:text-dark-text-primary hover:bg-dark-surface"
                  }`}
                >
                  Connect to Stream
                </button>
                <button
                  onClick={() => {
                    setEsp32Mode("setup-wifi");
                    setProvisionStatus({ type: null, message: "" });
                  }}
                  className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    esp32Mode === "setup-wifi"
                      ? "bg-brand-gold text-brand-charcoal"
                      : "text-dark-text-secondary hover:text-dark-text-primary hover:bg-dark-surface"
                  }`}
                >
                  Setup WiFi
                </button>
              </div>

              {/* Live Stream Mode */}
              {esp32Mode === "live-stream" && (
                <div className="space-y-4 p-4 bg-dark-bg rounded-xl border border-dark-border">
                  <div className="flex items-center gap-2">
                    <Monitor className="w-5 h-5 text-brand-gold" />
                    <h3 className="text-base font-semibold text-dark-text-primary font-heading">
                      Connect to Camera
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
                        className="w-full pl-10 pr-4 py-2.5 bg-dark-surface border border-dark-border rounded-xl text-dark-text-primary placeholder-dark-text-secondary focus:outline-none focus:border-brand-gold transition-colors"
                      />
                    </div>
                    <p className="text-xs text-dark-text-secondary leading-relaxed">
                      Enter the IP address shown in the Arduino Serial Monitor. Make sure your PC and camera are on the same WiFi network.
                    </p>
                  </div>

                  {/* Save Button */}
                  <button
                    onClick={handleSave}
                    disabled={isSaving || !ipAddress.trim()}
                    className="w-full flex items-center justify-center gap-2 px-5 py-2.5 bg-brand-gold text-brand-charcoal rounded-xl font-semibold hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isSaving ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4" />
                        Save & Connect
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* WiFi Setup Mode */}
              {esp32Mode === "setup-wifi" && (
                <div className="space-y-4 p-4 bg-dark-bg rounded-xl border border-dark-border">
                  <div className="flex items-center gap-2">
                    <Wifi className="w-5 h-5 text-brand-gold" />
                    <h3 className="text-base font-semibold text-dark-text-primary font-heading">
                      WiFi Provisioning
                    </h3>
                  </div>

                  {/* Instructions */}
                  <div className="bg-brand-gold/10 border border-brand-gold/30 rounded-xl p-3.5 space-y-2">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-brand-gold flex-shrink-0 mt-0.5" />
                      <div className="space-y-1.5 text-sm text-dark-text-primary">
                        <p className="font-semibold">Setup Instructions:</p>
                        <ol className="list-decimal list-inside space-y-1 text-dark-text-secondary text-xs">
                          <li>Power on your ESP32-CAM</li>
                          <li>
                            Connect your PC to{" "}
                            <span className="font-semibold text-brand-gold">
                              ESP32-CAM-SETUP
                            </span>{" "}
                            WiFi network
                          </li>
                          <li>Enter your Home WiFi credentials below</li>
                          <li>Click "Send Configuration"</li>
                        </ol>
                      </div>
                    </div>
                  </div>

                  {/* WiFi Credentials Form */}
                  <div className="space-y-3">
                    <div className="space-y-1.5">
                      <label className="text-sm font-medium text-dark-text-secondary">
                        Home WiFi SSID
                      </label>
                      <input
                        type="text"
                        value={wifiSSID}
                        onChange={(e) => setWifiSSID(e.target.value)}
                        placeholder="Your WiFi network name"
                        className="w-full px-4 py-2.5 bg-dark-surface border border-dark-border rounded-xl text-dark-text-primary placeholder-dark-text-secondary focus:outline-none focus:border-brand-gold transition-colors"
                        disabled={isProvisioning}
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-sm font-medium text-dark-text-secondary">
                        WiFi Password
                      </label>
                      <input
                        type="password"
                        value={wifiPassword}
                        onChange={(e) => setWifiPassword(e.target.value)}
                        placeholder="Leave empty for open networks"
                        className="w-full px-4 py-2.5 bg-dark-surface border border-dark-border rounded-xl text-dark-text-primary placeholder-dark-text-secondary focus:outline-none focus:border-brand-gold transition-colors"
                        disabled={isProvisioning}
                      />
                    </div>

                    {/* Provision Status */}
                    {provisionStatus.type && (
                      <div
                        className={`rounded-xl p-3 border flex items-start gap-2.5 ${
                          provisionStatus.type === "success"
                            ? "bg-green-500/10 border-green-500/30"
                            : "bg-red-500/10 border-red-500/30"
                        }`}
                      >
                        {provisionStatus.type === "success" ? (
                          <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
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
                      className="w-full flex items-center justify-center gap-2 px-5 py-2.5 bg-brand-gold text-brand-charcoal rounded-xl font-semibold hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    >
                      {isProvisioning ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Sending...
                        </>
                      ) : (
                        <>
                          <Wifi className="w-4 h-4" />
                          Send Configuration
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
