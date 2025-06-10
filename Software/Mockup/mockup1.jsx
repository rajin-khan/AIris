import React, { useState, useEffect } from 'react';
import { Camera, CameraOff, Volume2, Activity, Clock, Eye, Zap } from 'lucide-react';

const AirisMockup = () => {
  const [cameraOn, setCameraOn] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastLatency, setLastLatency] = useState(1.2);
  const [stats, setStats] = useState({
    confidence: 94,
    objectsDetected: 7,
    processTime: 1.2
  });

  const mockTranscript = "Scene captured: A modern kitchen with white cabinets and granite countertops. On the left counter, there's a coffee maker and a small potted plant. The central island has a bowl of fresh fruit - apples and oranges. To the right, I can see a stainless steel refrigerator. The room is well-lit with natural light coming from a window above the sink. No immediate obstacles or hazards detected in your path.";

  const handleDescribe = () => {
    setIsProcessing(true);
    setLastLatency(Math.random() * 0.8 + 0.8); // Random latency between 0.8-1.6s
    
    setTimeout(() => {
      setIsProcessing(false);
      setStats({
        confidence: Math.floor(Math.random() * 15 + 85),
        objectsDetected: Math.floor(Math.random() * 8 + 3),
        processTime: lastLatency
      });
    }, 1200);
  };

  const playAudio = () => {
    // Mock TTS functionality
    console.log("Playing audio description");
  };

  return (
    <div className="w-full h-screen bg-[#FDFDFB] flex flex-col font-serif">
      {/* Header */}
      <header className="flex items-center justify-between px-8 py-6 border-b border-[#E9E9E6]">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Eye className="w-8 h-8 text-[#4B4E9E]" />
            <h1 className="text-3xl font-bold text-[#1D1D1D] tracking-wide" style={{fontFamily: 'Georgia, serif'}}>
              A<span className="text-xl">IRIS</span>
            </h1>
          </div>
        </div>
        
        <div className="flex items-center space-x-6 text-sm text-[#1D1D1D]">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="font-medium">System Active</span>
          </div>
          <div className="text-[#4B4E9E] font-medium">
            {new Date().toLocaleTimeString()}
          </div>
        </div>
      </header>

      <div className="flex-1 flex">
        {/* Left Panel - Camera Feed */}
        <div className="w-1/2 p-8 border-r border-[#E9E9E6]">
          <div className="h-full flex flex-col">
            {/* Camera Controls */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-[#1D1D1D]">Live View</h2>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setCameraOn(!cameraOn)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg border-2 transition-all ${
                    cameraOn 
                      ? 'border-[#4B4E9E] text-[#4B4E9E] bg-white hover:bg-[#4B4E9E] hover:text-white' 
                      : 'border-[#C9AC78] text-[#C9AC78] bg-white hover:bg-[#C9AC78] hover:text-white'
                  }`}
                >
                  {cameraOn ? <Camera className="w-4 h-4" /> : <CameraOff className="w-4 h-4" />}
                  <span className="font-medium text-sm uppercase tracking-wide">
                    {cameraOn ? 'ON' : 'OFF'}
                  </span>
                </button>
                
                <button
                  onClick={handleDescribe}
                  disabled={!cameraOn || isProcessing}
                  className={`px-6 py-2 rounded-lg font-bold text-sm uppercase tracking-wide transition-all ${
                    !cameraOn || isProcessing
                      ? 'bg-[#E9E9E6] text-gray-400 cursor-not-allowed'
                      : 'bg-[#4B4E9E] text-white hover:bg-[#3a3f8a] shadow-lg hover:shadow-xl'
                  }`}
                >
                  {isProcessing ? 'PROCESSING...' : 'DESCRIBE SCENE'}
                </button>
              </div>
            </div>

            {/* Camera Feed */}
            <div className="flex-1 bg-[#E9E9E6] rounded-xl overflow-hidden relative">
              {cameraOn ? (
                <div className="w-full h-full bg-gradient-to-br from-gray-300 to-gray-500 flex items-center justify-center relative">
                  {/* Mock camera feed */}
                  <div className="absolute inset-4 bg-gradient-to-br from-blue-100 to-gray-200 rounded-lg"></div>
                  <div className="absolute top-8 left-8 bg-black bg-opacity-50 text-white px-3 py-1 rounded text-sm">
                    1920×1080 • 30fps
                  </div>
                  <div className="z-10 text-[#1D1D1D] text-lg opacity-60">
                    📹 Live Camera Feed
                  </div>
                  {isProcessing && (
                    <div className="absolute inset-0 bg-[#4B4E9E] bg-opacity-20 flex items-center justify-center">
                      <div className="bg-white px-6 py-3 rounded-lg shadow-lg">
                        <div className="flex items-center space-x-3">
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-[#4B4E9E]"></div>
                          <span className="text-[#4B4E9E] font-medium">Analyzing scene...</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <CameraOff className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg">Camera Disabled</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Panel - Transcript & Stats */}
        <div className="w-1/2 p-8 flex flex-col">
          {/* Scene Description */}
          <div className="flex-1 flex flex-col">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-[#1D1D1D]">Scene Description</h2>
              <button
                onClick={playAudio}
                className="flex items-center space-x-2 px-4 py-2 border-2 border-[#C9AC78] text-[#C9AC78] rounded-lg hover:bg-[#C9AC78] hover:text-white transition-all"
              >
                <Volume2 className="w-4 h-4" />
                <span className="font-medium text-sm uppercase tracking-wide">Play Audio</span>
              </button>
            </div>

            <div className="flex-1 bg-white rounded-xl border border-[#E9E9E6] p-6 overflow-y-auto">
              <p className="text-[#1D1D1D] leading-relaxed font-sans text-base">
                {mockTranscript}
              </p>
            </div>
          </div>

          {/* Statistics Panel */}
          <div className="mt-8">
            <h3 className="text-lg font-bold text-[#1D1D1D] mb-4">System Performance</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white rounded-lg border border-[#E9E9E6] p-4 text-center">
                <div className="flex items-center justify-center mb-2">
                  <Clock className="w-5 h-5 text-[#4B4E9E]" />
                </div>
                <div className="text-2xl font-bold text-[#1D1D1D]">{stats.processTime.toFixed(1)}s</div>
                <div className="text-sm text-gray-600 font-sans">Latency</div>
              </div>

              <div className="bg-white rounded-lg border border-[#E9E9E6] p-4 text-center">
                <div className="flex items-center justify-center mb-2">
                  <Activity className="w-5 h-5 text-[#4B4E9E]" />
                </div>
                <div className="text-2xl font-bold text-[#1D1D1D]">{stats.confidence}%</div>
                <div className="text-sm text-gray-600 font-sans">Confidence</div>
              </div>

              <div className="bg-white rounded-lg border border-[#E9E9E6] p-4 text-center">
                <div className="flex items-center justify-center mb-2">
                  <Zap className="w-5 h-5 text-[#4B4E9E]" />
                </div>
                <div className="text-2xl font-bold text-[#1D1D1D]">{stats.objectsDetected}</div>
                <div className="text-sm text-gray-600 font-sans">Objects</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AirisMockup;