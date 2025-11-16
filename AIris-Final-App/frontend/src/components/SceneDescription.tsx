import { useState, useEffect, useRef } from 'react';
import { Volume2, Play, Square, Clock, Activity, Zap, AlertTriangle } from 'lucide-react';
import { apiClient } from '../services/api';

interface SceneDescriptionProps {
  cameraOn: boolean;
}

export default function SceneDescription({ cameraOn }: SceneDescriptionProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentDescription, setCurrentDescription] = useState('');
  const [currentSummary, setCurrentSummary] = useState('');
  const [safetyAlert, setSafetyAlert] = useState(false);
  const [frameUrl, setFrameUrl] = useState<string | null>(null);
  const [stats, setStats] = useState({
    latency: 1.2,
    confidence: 94,
    objectsDetected: 7,
  });
  const [recordingLogs, setRecordingLogs] = useState<any[]>([]);
  const frameIntervalRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    loadLogs();
  }, []);

  useEffect(() => {
    if (cameraOn) {
      startFrameProcessing();
    } else {
      stopFrameProcessing();
      setFrameUrl(null);
    }
    return () => stopFrameProcessing();
  }, [cameraOn, isRecording]);

  const loadLogs = async () => {
    try {
      const logs = await apiClient.getRecordingLogs();
      setRecordingLogs(logs);
    } catch (error) {
      console.error('Error loading logs:', error);
    }
  };

  const startFrameProcessing = () => {
    // Stop existing interval if any
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }
    
    const processFrame = async () => {
      try {
        if (isRecording) {
          // If recording, process frame with scene description
          setIsProcessing(true);
          const result = await apiClient.processSceneFrame();
          setFrameUrl(`data:image/jpeg;base64,${result.frame}`);
          
          if (result.description) {
            setCurrentDescription(result.description);
          }
          if (result.summary) {
            setCurrentSummary(result.summary);
          }
          setSafetyAlert(result.safety_alert || false);
          setIsRecording(result.is_recording);
          
          // Update stats (mock for now)
          setStats(prev => ({
            latency: Math.random() * 0.8 + 0.8,
            confidence: Math.floor(Math.random() * 15 + 85),
            objectsDetected: Math.floor(Math.random() * 8 + 12),
          }));
          setIsProcessing(false);
        } else {
          // If not recording, just show raw camera feed
          const frameUrl = await apiClient.getCameraFrame();
          setFrameUrl(frameUrl);
        }
      } catch (error) {
        console.error('Error processing frame:', error);
        setIsProcessing(false);
      }
    };
    
    processFrame();
    // Update more frequently when not recording for smooth video, less frequently when recording
    const interval = isRecording ? 10000 : 100; // 10s when recording, 100ms when idle
    frameIntervalRef.current = window.setInterval(processFrame, interval);
  };

  const stopFrameProcessing = () => {
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }
  };

  const handleStartRecording = async () => {
    if (!cameraOn) {
      alert('Please start the camera first!');
      return;
    }

    try {
      const response = await apiClient.startRecording();
      if (response.status === 'success') {
        setIsRecording(true);
        setCurrentDescription('');
        setCurrentSummary('');
        setSafetyAlert(false);
      }
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Failed to start recording');
    }
  };

  const handleStopRecording = async () => {
    try {
      const response = await apiClient.stopRecording();
      if (response.status === 'success') {
        setIsRecording(false);
        await loadLogs();
      }
    } catch (error) {
      console.error('Error stopping recording:', error);
      alert('Failed to stop recording');
    }
  };

  const handlePlayAudio = async () => {
    const textToSpeak = currentSummary || currentDescription;
    if (!textToSpeak) return;
    
    try {
      const audioData = await apiClient.generateSpeech(textToSpeak);
      const audioBlob = new Blob([
        Uint8Array.from(atob(audioData.audio_base64), c => c.charCodeAt(0))
      ], { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);
      
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
      }
    } catch (error) {
      console.error('Error generating speech:', error);
    }
  };

  const StatCard = ({ icon: Icon, value, label }: { icon: any, value: string | number, label: string }) => (
    <div className="bg-dark-surface rounded-2xl border border-dark-border p-4 flex flex-col items-center justify-center text-center transition-all duration-300 hover:border-brand-gold/50 hover:bg-dark-border">
      <Icon className="w-5 h-5 mb-3 text-brand-gold" />
      <div className="text-2xl font-semibold font-heading text-dark-text-primary">{value}</div>
      <div className="text-xs text-dark-text-secondary font-sans uppercase tracking-wider mt-1">{label}</div>
    </div>
  );

  return (
    <div className="flex-1 flex flex-col lg:flex-row p-6 md:p-10 gap-6 md:gap-10 overflow-hidden">
      {/* Left Panel - Camera Feed */}
      <div className="flex-1 flex flex-col min-h-[450px] lg:min-h-0">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-xl font-semibold font-heading text-dark-text-primary">Live View</h2>
          <div className="flex items-center space-x-3">
            {!isRecording ? (
              <button
                onClick={handleStartRecording}
                disabled={!cameraOn || isProcessing}
                className={`px-5 py-2.5 rounded-xl font-semibold text-sm uppercase tracking-wider transition-all duration-300 flex items-center space-x-2.5 shadow-lg
                  ${isProcessing ? 'animate-subtle-pulse' : ''}
                  bg-brand-gold text-brand-charcoal hover:bg-opacity-85 shadow-brand-gold/10
                  disabled:bg-dark-surface disabled:text-dark-text-secondary disabled:cursor-not-allowed disabled:shadow-none`}
              >
                <Play className="w-4 h-4"/>
                <span>START RECORDING</span>
              </button>
            ) : (
              <button
                onClick={handleStopRecording}
                disabled={isProcessing}
                className="px-5 py-2.5 rounded-xl font-semibold text-sm uppercase tracking-wider transition-all duration-300 flex items-center space-x-2.5 bg-red-600 text-white hover:bg-red-700 disabled:opacity-50"
              >
                <Square className="w-4 h-4"/>
                <span>STOP & SAVE</span>
              </button>
            )}
          </div>
        </div>

        <div className="flex-1 bg-black rounded-3xl overflow-hidden relative border-2 border-dark-border shadow-2xl shadow-black/50 transition-all duration-500">
          {cameraOn && frameUrl ? (
            <>
              <img 
                src={frameUrl} 
                alt="Camera feed" 
                className="w-full h-full object-contain"
              />
              {isProcessing && (
                <div className="absolute inset-0 border-4 border-brand-gold animate-subtle-pulse"></div>
              )}
            </>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-dark-text-secondary bg-dark-surface">
              <div className="text-center">
                <p className="text-lg">Camera feed will appear here</p>
                {!cameraOn && <p className="text-sm mt-2">Please start the camera</p>}
              </div>
            </div>
          )}
          {isRecording && (
            <div className="absolute top-4 left-5 bg-red-600/80 backdrop-blur-sm text-white px-3 py-1 rounded-full text-xs font-mono flex items-center gap-2">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              RECORDING
            </div>
          )}
        </div>
      </div>

      {/* Right Panel - Description & Stats */}
      <div className="lg:w-[38%] flex flex-col flex-shrink-0">
        <div className="flex-1 flex flex-col min-h-[300px] lg:min-h-0">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-xl font-semibold font-heading text-dark-text-primary">Scene Description</h2>
            <button
              onClick={handlePlayAudio}
              disabled={!currentSummary && !currentDescription}
              className="flex items-center space-x-2 px-4 py-2 border-2 border-dark-border text-dark-text-secondary rounded-xl hover:border-brand-gold hover:text-brand-gold transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Volume2 className="w-5 h-5" />
              <span className="font-medium text-sm uppercase tracking-wider hidden sm:block">Play</span>
            </button>
          </div>

          <div className="flex-1 bg-dark-surface rounded-2xl border border-dark-border p-5 md:p-6 overflow-y-auto custom-scrollbar">
            {safetyAlert && (
              <div className="mb-4 p-3 bg-red-600/20 border border-red-600/50 rounded-xl flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                <span className="text-red-400 font-semibold">Safety Alert Triggered!</span>
              </div>
            )}
            {currentSummary ? (
              <div>
                <p className="text-dark-text-primary leading-relaxed text-base font-sans mb-4">
                  {currentSummary}
                </p>
                {currentDescription && (
                  <p className="text-dark-text-secondary text-sm italic">
                    Latest observation: {currentDescription}
                  </p>
                )}
              </div>
            ) : currentDescription ? (
              <p className="text-dark-text-primary leading-relaxed text-base font-sans">
                {currentDescription}
              </p>
            ) : (
              <p className="text-dark-text-secondary text-sm">
                {isRecording ? 'Awaiting new description...' : 'Start recording to begin scene description'}
              </p>
            )}
          </div>
        </div>

        <div className="mt-6 md:mt-10">
          <h3 className="text-lg font-semibold font-heading text-dark-text-primary mb-4">System Performance</h3>
          <div className="grid grid-cols-3 gap-4">
            <StatCard icon={Clock} value={`${stats.latency.toFixed(1)}s`} label="Latency" />
            <StatCard icon={Activity} value={`${stats.confidence}%`} label="Confidence" />
            <StatCard icon={Zap} value={stats.objectsDetected} label="Objects" />
          </div>
        </div>
      </div>

      {/* Hidden audio element */}
      <audio ref={audioRef} />
    </div>
  );
}

