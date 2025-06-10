import React, { useState, useEffect } from 'react';
import { Camera, CameraOff, Volume2, Activity, Clock, Zap, Power } from 'lucide-react';

const AirisMockup = () => {
  const [cameraOn, setCameraOn] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [stats, setStats] = useState({
    latency: 1.2,
    confidence: 94,
    objectsDetected: 7,
  });

  // --- NEW MOCK TRANSCRIPT ---
  const mockTranscript = "You are facing a wooden cafe counter. A barista is standing behind it, operating a large, chrome espresso machine. To your left, on the counter, is a glass display case filled with pastries, including croissants and muffins. The area appears to be active, with other patrons visible in the background. The path directly in front of you is clear up to the counter.";

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleDescribe = () => {
    if (!cameraOn || isProcessing) return;
    
    setIsProcessing(true);
    const newLatency = Math.random() * 0.8 + 0.8;
    
    setTimeout(() => {
      setStats({
        latency: newLatency,
        confidence: Math.floor(Math.random() * 15 + 85),
        objectsDetected: Math.floor(Math.random() * 8 + 12), // Increased object count for a richer scene
      });
      setIsProcessing(false);
    }, 1500);
  };

  const playAudio = () => {
    console.log("Playing audio description:", mockTranscript);
  };

  const StatCard = ({ icon: Icon, value, label }: { icon: React.ElementType, value: string | number, label: string }) => (
    <div className="bg-dark-surface rounded-2xl border border-dark-border p-4 flex flex-col items-center justify-center text-center transition-all duration-300 hover:border-brand-gold/50 hover:bg-dark-border">
      <Icon className="w-5 h-5 mb-3 text-brand-gold" />
      <div className="text-2xl font-semibold font-heading text-dark-text-primary">{value}</div>
      <div className="text-xs text-dark-text-secondary font-sans uppercase tracking-wider mt-1">{label}</div>
    </div>
  );

  return (
    <div className="w-full h-screen bg-dark-bg flex flex-col font-sans text-dark-text-primary overflow-hidden">
      {/* Header */}
      <header className="flex items-center justify-between px-6 md:px-10 py-5 border-b border-dark-border flex-shrink-0">
        <h1 className="text-3xl font-semibold text-dark-text-primary tracking-logo font-heading">
          A<span className="text-2xl align-middle opacity-80">IRIS</span>
        </h1>
        
        <div className="flex items-center space-x-4 md:space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-2.5 h-2.5 bg-green-400 rounded-full shadow-[0_0_8px_rgba(74,222,128,0.5)]"></div>
            <span className="font-medium text-dark-text-secondary hidden sm:block">System Active</span>
          </div>
          <div className="text-dark-text-primary font-medium text-base">
            {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </header>

      <main className="flex-1 flex flex-col lg:flex-row p-6 md:p-10 gap-6 md:gap-10 overflow-y-auto">
        {/* Left Panel - Camera Feed */}
        <div className="flex-1 flex flex-col min-h-[450px] lg:min-h-0">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-xl font-semibold font-heading text-dark-text-primary">Live View</h2>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setCameraOn(!cameraOn)}
                title={cameraOn ? 'Turn Camera Off' : 'Turn Camera On'}
                className={`p-2.5 rounded-xl border-2 transition-all duration-300 ${
                  cameraOn 
                    ? 'border-dark-border text-dark-text-secondary hover:border-brand-gold hover:text-brand-gold' 
                    : 'border-dark-border bg-dark-surface text-dark-text-secondary'
                }`}
              >
                {cameraOn ? <Camera className="w-5 h-5" /> : <CameraOff className="w-5 h-5" />}
              </button>
              
              <button
                onClick={handleDescribe}
                disabled={!cameraOn || isProcessing}
                className={`px-5 py-2.5 rounded-xl font-semibold text-sm uppercase tracking-wider transition-all duration-300 flex items-center space-x-2.5 shadow-lg
                  ${isProcessing ? 'animate-subtle-pulse' : ''}
                  bg-brand-gold text-brand-charcoal hover:bg-opacity-85 shadow-brand-gold/10
                  disabled:bg-dark-surface disabled:text-dark-text-secondary disabled:cursor-not-allowed disabled:shadow-none`}
              >
                <Power className="w-4 h-4"/>
                <span>{isProcessing ? 'ANALYZING...' : 'DESCRIBE SCENE'}</span>
              </button>
            </div>
          </div>

          <div className="flex-1 bg-black rounded-3xl overflow-hidden relative border-2 border-dark-border shadow-2xl shadow-black/50 transition-all duration-500">
            {cameraOn ? (
              // --- NEW BACKGROUND IMAGE URL ---
              <div className="w-full h-full bg-[url('https://images.unsplash.com/photo-1559925393-8be0ec4767c8?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center flex items-center justify-center relative">
                <div className={`absolute inset-0 transition-all duration-500 ${isProcessing ? 'border-4 border-brand-gold animate-subtle-pulse' : 'border-0 border-transparent'}`}></div>
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20"></div>
                <div className="absolute top-4 left-5 bg-black/50 backdrop-blur-sm text-white px-3 py-1 rounded-full text-xs font-mono">
                  1920×1080 • 30fps
                </div>
              </div>
            ) : (
              <div className="w-full h-full flex items-center justify-center text-dark-text-secondary bg-dark-surface">
                <div className="text-center">
                  <CameraOff className="w-16 h-16 mx-auto mb-4 opacity-30" />
                  <p className="text-lg">Camera is Disabled</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Transcript & Stats */}
        <div className="lg:w-[38%] flex flex-col flex-shrink-0">
          <div className="flex-1 flex flex-col min-h-[300px] lg:min-h-0">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-xl font-semibold font-heading text-dark-text-primary">Scene Description</h2>
              <button
                onClick={playAudio}
                title="Play Audio Description"
                className="flex items-center space-x-2 px-4 py-2 border-2 border-dark-border text-dark-text-secondary rounded-xl hover:border-brand-gold hover:text-brand-gold transition-all duration-300"
              >
                <Volume2 className="w-5 h-5" />
                <span className="font-medium text-sm uppercase tracking-wider hidden sm:block">Play</span>
              </button>
            </div>

            <div className="flex-1 bg-dark-surface rounded-2xl border border-dark-border p-5 md:p-6 overflow-y-auto custom-scrollbar">
              <p className="text-dark-text-primary leading-relaxed text-base font-sans transition-opacity duration-500" style={{ opacity: isProcessing ? 0.5 : 1 }}>
                {isProcessing ? 'Awaiting new description...' : mockTranscript}
              </p>
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
      </main>
    </div>
  );
};

export default AirisMockup;