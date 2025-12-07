import { useState, useEffect } from 'react';
import { Camera, CameraOff, Settings } from 'lucide-react';
import ActivityGuide from './components/ActivityGuide';
import SceneDescription from './components/SceneDescription';
import HardwareSettings from './components/HardwareSettings';
import { apiClient } from './services/api';

type Mode = 'Activity Guide' | 'Scene Description';
type CameraSource = 'local' | 'esp32';

function App() {
  const [mode, setMode] = useState<Mode>('Activity Guide');
  const [cameraOn, setCameraOn] = useState(false);
  const [cameraStatus, setCameraStatus] = useState({ is_running: false, is_available: false });
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showSettings, setShowSettings] = useState(false);
  const [cameraSource, setCameraSource] = useState<CameraSource>(() => {
    // Persist camera source preference in localStorage
    const saved = localStorage.getItem('airis-camera-source');
    return (saved === 'esp32' ? 'esp32' : 'local') as CameraSource;
  });

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    checkCameraStatus();
  }, []);

  // Persist camera source preference
  useEffect(() => {
    localStorage.setItem('airis-camera-source', cameraSource);
  }, [cameraSource]);

  // Auto-configure webcam when in local mode on initial load
  useEffect(() => {
    if (cameraSource === 'local') {
      apiClient.setCameraConfig('webcam').catch(console.error);
    }
  }, []);

  const handleCameraSourceChange = (newSource: CameraSource) => {
    setCameraSource(newSource);
    // If switching to local, auto-configure webcam
    if (newSource === 'local') {
      apiClient.setCameraConfig('webcam').catch(console.error);
    }
  };

  const checkCameraStatus = async () => {
    try {
      const status = await apiClient.getCameraStatus();
      setCameraStatus(status);
    } catch (error) {
      console.error('Failed to check camera status:', error);
    }
  };

  const handleCameraToggle = async () => {
    try {
      if (cameraOn) {
        await apiClient.stopCamera();
        setCameraOn(false);
      } else {
        await apiClient.startCamera();
        setCameraOn(true);
      }
      await checkCameraStatus();
    } catch (error) {
      console.error('Failed to toggle camera:', error);
      alert('Failed to toggle camera. Please check your camera permissions.');
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
          {/* Mode Selection */}
          <div className="flex items-center space-x-2 bg-dark-surface rounded-xl p-1 border border-dark-border">
            <button
              onClick={() => setMode('Activity Guide')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${mode === 'Activity Guide'
                  ? 'bg-brand-gold text-brand-charcoal'
                  : 'text-dark-text-secondary hover:text-dark-text-primary'
                }`}
            >
              Activity Guide
            </button>
            <button
              onClick={() => setMode('Scene Description')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${mode === 'Scene Description'
                  ? 'bg-brand-gold text-brand-charcoal'
                  : 'text-dark-text-secondary hover:text-dark-text-primary'
                }`}
            >
              Scene Description
            </button>
          </div>

          {/* Camera Settings */}
          <button
            onClick={() => setShowSettings(true)}
            title="Camera Settings"
            className="p-2.5 rounded-xl border-2 transition-all duration-300 border-dark-border bg-dark-surface text-dark-text-secondary hover:border-brand-gold hover:text-brand-gold"
          >
            <Settings className="w-5 h-5" />
          </button>

          {/* Camera Toggle */}
          <button
            onClick={handleCameraToggle}
            title={cameraOn ? 'Turn Camera Off' : 'Turn Camera On'}
            className={`p-2.5 rounded-xl border-2 transition-all duration-300 ${cameraOn
                ? 'border-dark-border text-dark-text-secondary hover:border-brand-gold hover:text-brand-gold'
                : 'border-dark-border bg-dark-surface text-dark-text-secondary'
              }`}
          >
            {cameraOn ? <Camera className="w-5 h-5" /> : <CameraOff className="w-5 h-5" />}
          </button>

          {/* Status Indicator */}
          <div className="flex items-center space-x-2">
            <div className={`w-2.5 h-2.5 rounded-full ${cameraStatus.is_running
                ? 'bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.5)]'
                : 'bg-gray-500'
              }`}></div>
            <span className="font-medium text-dark-text-secondary hidden sm:block text-sm">
              {cameraStatus.is_running ? 'System Active' : 'System Inactive'}
            </span>
          </div>

          {/* Time */}
          <div className="text-dark-text-primary font-medium text-base">
            {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        {mode === 'Activity Guide' ? (
          <ActivityGuide cameraOn={cameraOn} />
        ) : (
          <SceneDescription cameraOn={cameraOn} />
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
