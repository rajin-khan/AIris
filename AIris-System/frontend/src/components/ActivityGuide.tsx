import { useState, useEffect, useRef } from 'react';
import { Volume2, CheckCircle, XCircle, Play, Loader2, Mic, MicOff } from 'lucide-react';
import { apiClient, type TaskRequest } from '../services/api';

// Web Speech API type definitions
interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any) | null;
  onend: ((this: SpeechRecognition, ev: Event) => any) | null;
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
  isFinal: boolean;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

declare global {
  interface Window {
    SpeechRecognition: {
      new (): SpeechRecognition;
    };
    webkitSpeechRecognition: {
      new (): SpeechRecognition;
    };
  }
}

interface ActivityGuideProps {
  cameraOn: boolean;
}

export default function ActivityGuide({ cameraOn }: ActivityGuideProps) {
  const [taskInput, setTaskInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentInstruction, setCurrentInstruction] = useState('Start the camera and enter a task.');
  const [instructionHistory, setInstructionHistory] = useState<string[]>([]);
  const [stage, setStage] = useState('IDLE');
  const [awaitingFeedback, setAwaitingFeedback] = useState(false);
  const [frameUrl, setFrameUrl] = useState<string | null>(null);
  const [detectedObjects, setDetectedObjects] = useState<Array<{ name: string; box: number[] }>>([]);
  const [handDetected, setHandDetected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [useWebSpeech, setUseWebSpeech] = useState(true); // Try Web Speech API first
  const [fallbackToOffline, setFallbackToOffline] = useState(false);
  const frameIntervalRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    if (cameraOn) {
      startFrameProcessing();
    } else {
      stopFrameProcessing();
      setFrameUrl(null);
    }
    return () => stopFrameProcessing();
  }, [cameraOn, stage]);

  // Initialize Web Speech API first, fallback to MediaRecorder if not available
  useEffect(() => {
    // Check for Web Speech API support
    const SpeechRecognitionClass = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognitionClass) {
      setSpeechSupported(true);
      setUseWebSpeech(true);
      
      const recognition = new SpeechRecognitionClass();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        setFallbackToOffline(false);
      };

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        if (event.results && event.results.length > 0 && event.results[0].length > 0) {
          const transcript = event.results[0][0].transcript.trim();
          if (transcript) {
            setTaskInput(prev => prev + (prev ? ' ' : '') + transcript);
          }
        }
        setIsListening(false);
      };

      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error('Web Speech API error:', event.error, event.message);
        
        // If network error or service unavailable, fall back to offline method
        if (event.error === 'network' || event.error === 'service-not-allowed') {
          console.log('Web Speech API network error, falling back to offline Whisper model...');
          setUseWebSpeech(false);
          setFallbackToOffline(true);
          setIsListening(false);
          
          // Automatically start offline recording if we have MediaRecorder support
          if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            setTimeout(() => {
              startRecording();
            }, 500);
          } else {
            alert('Web Speech API failed and offline mode not available. Please check your internet connection.');
          }
        } else if (event.error === 'not-allowed') {
          // Permission denied - don't auto-fallback, just show error
          setIsListening(false);
          alert('Microphone permission denied. Please enable microphone access in your browser settings.');
        } else if (event.error === 'no-speech') {
          // Normal - user didn't speak
          setIsListening(false);
        } else if (event.error === 'aborted') {
          // User or system aborted
          setIsListening(false);
        } else {
          setIsListening(false);
          console.warn('Web Speech API error:', event.error);
        }
      };

      recognition.onend = () => {
        // Don't set listening to false here - let error/result handlers do it
      };

      recognitionRef.current = recognition;
    } else {
      // No Web Speech API, use offline method
      console.log('Web Speech API not available, using offline Whisper model');
      setUseWebSpeech(false);
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        setSpeechSupported(true);
      } else {
        setSpeechSupported(false);
        console.warn('No speech recognition available in this browser');
      }
    }

    return () => {
      // Cleanup Web Speech API
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
          recognitionRef.current.abort();
        } catch (e) {
          // Ignore errors during cleanup
        }
      }
      // Cleanup MediaRecorder
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        try {
          mediaRecorderRef.current.stop();
        } catch (e) {
          // Ignore errors during cleanup
        }
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    };
  }, []);

  const startFrameProcessing = () => {
    if (frameIntervalRef.current) return;
    
    const processFrame = async () => {
      try {
        // Always use process-frame endpoint to get annotated frames with YOLO boxes and hand tracking
        const result = await apiClient.processActivityFrame();
        setFrameUrl(`data:image/jpeg;base64,${result.frame}`);
        setCurrentInstruction(result.instruction);
        setStage(result.stage);
        setDetectedObjects(result.detected_objects || []);
        setHandDetected(result.hand_detected || false);
        
        if (result.instruction && !instructionHistory.includes(result.instruction)) {
          setInstructionHistory(prev => [result.instruction, ...prev].slice(0, 20));
        }
        
        if (result.stage === 'AWAITING_FEEDBACK') {
          setAwaitingFeedback(true);
        }
      } catch (error) {
        console.error('Error processing frame:', error);
      }
    };
    
    processFrame();
    frameIntervalRef.current = window.setInterval(processFrame, 100); // Update every 100ms for smooth video (~10 FPS)
  };

  const stopFrameProcessing = () => {
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }
  };

  const handleStartTask = async () => {
    if (!taskInput.trim() || !cameraOn) {
      alert('Please start the camera and enter a task.');
      return;
    }

    setIsProcessing(true);
    try {
      const request: TaskRequest = { goal: taskInput };
      const response = await apiClient.startTask(request);
      
      if (response.status === 'success') {
        setCurrentInstruction(response.message);
        setStage(response.stage);
        setTaskInput('');
        setInstructionHistory([response.message]);
      } else {
        alert('Failed to start task: ' + response.message);
      }
    } catch (error) {
      console.error('Error starting task:', error);
      alert('Failed to start task. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFeedback = async (confirmed: boolean) => {
    try {
      const response = await apiClient.submitFeedback({ confirmed });
      setAwaitingFeedback(false);
      setStage(response.next_stage);
      setCurrentInstruction(response.message);
      
      if (confirmed && response.next_stage === 'DONE') {
        // Task completed
        setInstructionHistory(prev => ['Task Completed Successfully!', ...prev]);
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const handlePlayAudio = async () => {
    if (!currentInstruction) return;
    
    try {
      const audioData = await apiClient.generateSpeech(currentInstruction);
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

  const handleToggleListening = async () => {
    if (!speechSupported) {
      alert('Microphone access not available in this browser.');
      return;
    }

    if (isListening) {
      // Stop recording/listening
      if (useWebSpeech && recognitionRef.current) {
        try {
          recognitionRef.current.stop();
          recognitionRef.current.abort();
        } catch (e) {
          // Ignore errors
        }
      } else {
        await stopRecording();
      }
      setIsListening(false);
    } else {
      // Start recording - try Web Speech API first, fallback to offline
      if (useWebSpeech && recognitionRef.current) {
        startWebSpeechRecognition();
      } else {
        await startRecording();
      }
    }
  };

  const startWebSpeechRecognition = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition not initialized.');
      return;
    }

    try {
      // Abort any existing recognition
      try {
        recognitionRef.current.abort();
      } catch (e) {
        // Ignore
      }

      // Start Web Speech API
      setTimeout(() => {
        if (recognitionRef.current) {
          try {
            recognitionRef.current.start();
          } catch (error: any) {
            const errorMsg = error.message || error.toString() || '';
            if (errorMsg.includes('already started')) {
              // Already running
              setIsListening(true);
            } else {
              console.error('Web Speech API start error:', error);
              // Fall back to offline
              setUseWebSpeech(false);
              startRecording();
            }
          }
        }
      }, 100);
    } catch (error) {
      console.error('Error starting Web Speech API:', error);
      // Fall back to offline
      setUseWebSpeech(false);
      startRecording();
    }
  };

  const startRecording = async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Create MediaRecorder with WAV format (better compatibility)
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/wav'
      });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Convert audio chunks to blob
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: mediaRecorder.mimeType || 'audio/webm' 
        });
        
        // Convert to base64
        const reader = new FileReader();
        reader.onloadend = async () => {
          const base64Audio = (reader.result as string).split(',')[1];
          
          // Transcribe using backend
          setIsTranscribing(true);
          try {
            const result = await apiClient.transcribeAudio(base64Audio);
            if (result.success && result.text) {
              setTaskInput(prev => prev + (prev ? ' ' : '') + result.text.trim());
            }
          } catch (error) {
            console.error('Transcription error:', error);
            alert('Failed to transcribe audio. Please try again.');
          } finally {
            setIsTranscribing(false);
          }
        };
        reader.readAsDataURL(audioBlob);

        // Stop all tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
      };

      // Start recording
      mediaRecorder.start();
      setIsListening(true);
    } catch (error: any) {
      console.error('Error starting recording:', error);
      setIsListening(false);
      
      if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        alert('Microphone permission denied. Please enable microphone access in your browser settings.');
      } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
        alert('No microphone found. Please connect a microphone and try again.');
      } else {
        alert('Failed to access microphone. Please check your browser settings and try again.');
      }
    }
  };

  const stopRecording = async () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try {
        mediaRecorderRef.current.stop();
      } catch (error) {
        console.error('Error stopping recording:', error);
      }
    }
    setIsListening(false);
  };

  return (
    <div className="flex-1 flex flex-col lg:flex-row p-6 md:p-10 gap-6 md:gap-10 overflow-hidden h-full">
      {/* Left Panel - Camera Feed */}
      <div className="flex-1 flex flex-col min-h-0 lg:min-h-0 lg:h-full">
        <div className="flex-1 bg-black rounded-3xl overflow-hidden relative border-2 border-dark-border shadow-2xl shadow-black/50 min-h-0 h-full">
          {cameraOn && frameUrl ? (
            <img 
              src={frameUrl} 
              alt="Camera feed" 
              className="w-full h-full object-contain"
              style={{ display: 'block', maxWidth: '100%', maxHeight: '100%' }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-dark-text-secondary bg-dark-surface">
              <div className="text-center">
                <p className="text-lg">Camera feed will appear here</p>
                {!cameraOn && <p className="text-sm mt-2">Please start the camera</p>}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right Panel - Controls and Logs */}
      <div className="lg:w-[38%] flex flex-col flex-shrink-0 gap-6 min-h-0 lg:h-full">
        {/* Task Input */}
        <div className="bg-dark-surface rounded-2xl border border-dark-border p-5">
          <h2 className="text-xl font-semibold font-heading text-dark-text-primary mb-4">
            Task Input
          </h2>
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <input
                type="text"
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleStartTask()}
                placeholder="Enter a task (e.g., 'find my watch')"
                disabled={!cameraOn || isProcessing || (stage !== 'IDLE' && stage !== 'DONE')}
                className="w-full px-4 py-2 pr-12 bg-dark-bg border border-dark-border rounded-xl text-dark-text-primary placeholder-dark-text-secondary focus:outline-none focus:border-brand-gold disabled:opacity-50"
              />
              {speechSupported && (
                <button
                  onClick={handleToggleListening}
                  disabled={!cameraOn || isProcessing || (stage !== 'IDLE' && stage !== 'DONE')}
                  className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all ${
                    isListening
                      ? 'bg-red-600 text-white animate-pulse'
                      : 'text-dark-text-secondary hover:text-brand-gold hover:bg-dark-surface'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                  title={isListening ? 'Stop listening' : 'Start voice input'}
                >
                  {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </button>
              )}
            </div>
            <button
              onClick={handleStartTask}
              disabled={!cameraOn || isProcessing || (stage !== 'IDLE' && stage !== 'DONE')}
              className="px-5 py-2 bg-brand-gold text-brand-charcoal rounded-xl font-semibold hover:bg-opacity-85 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isProcessing ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Start'}
            </button>
          </div>
          {speechSupported && (
            <p className="text-xs text-dark-text-secondary mt-2">
              {isTranscribing ? (
                <span className="text-blue-400">⏳ Transcribing with offline model...</span>
              ) : isListening ? (
                <span className="text-red-400">
                  {useWebSpeech ? (
                    <>🎤 Listening (Web Speech API)... Speak your task now.</>
                  ) : (
                    <>🎤 Recording (offline)... Speak your task now. Click mic again to stop.</>
                  )}
                </span>
              ) : (
                <span>
                  💡 Click the microphone icon to use voice input
                  {useWebSpeech ? ' (Web Speech API)' : ' (offline Whisper)'}
                </span>
              )}
            </p>
          )}
        </div>

        {/* Current Instruction */}
        <div className="bg-dark-surface rounded-2xl border border-dark-border p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold font-heading text-dark-text-primary">
              Current Instruction
            </h2>
            <button
              onClick={handlePlayAudio}
              className="p-2 border-2 border-dark-border text-dark-text-secondary rounded-xl hover:border-brand-gold hover:text-brand-gold transition-all"
            >
              <Volume2 className="w-5 h-5" />
            </button>
          </div>
          <div className="bg-dark-bg rounded-xl p-4 min-h-[100px]">
            <p className="text-dark-text-primary leading-relaxed">
              {currentInstruction}
            </p>
          </div>

          {/* Feedback Buttons */}
          {awaitingFeedback && (
            <div className="mt-4 flex gap-3">
              <button
                onClick={() => handleFeedback(true)}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 transition-all"
              >
                <CheckCircle className="w-5 h-5" />
                Yes
              </button>
              <button
                onClick={() => handleFeedback(false)}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-red-600 text-white rounded-xl font-semibold hover:bg-red-700 transition-all"
              >
                <XCircle className="w-5 h-5" />
                No
              </button>
            </div>
          )}
        </div>

        {/* Instruction History */}
        <div className="flex-1 bg-dark-surface rounded-2xl border border-dark-border p-5 overflow-y-auto custom-scrollbar min-h-0">
          <h3 className="text-lg font-semibold font-heading text-dark-text-primary mb-4 flex-shrink-0">
            Guidance Log
          </h3>
          <div className="space-y-2">
            {instructionHistory.length === 0 ? (
              <p className="text-dark-text-secondary text-sm">No instructions yet</p>
            ) : (
              instructionHistory.map((instruction, index) => (
                <div key={index} className="text-sm text-dark-text-primary bg-dark-bg rounded-lg p-3">
                  <span className="font-semibold text-brand-gold">{instructionHistory.length - index}.</span> {instruction}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Detection Info */}
        <div className="bg-dark-surface rounded-2xl border border-dark-border p-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-dark-text-secondary">Objects Detected:</span>
              <span className="ml-2 text-dark-text-primary font-semibold">
                {detectedObjects.length}
              </span>
            </div>
            <div>
              <span className="text-dark-text-secondary">Hand Detected:</span>
              <span className={`ml-2 font-semibold ${handDetected ? 'text-green-400' : 'text-gray-400'}`}>
                {handDetected ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Hidden audio element */}
      <audio ref={audioRef} />
    </div>
  );
}

