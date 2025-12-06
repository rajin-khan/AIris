"""
Speech-to-Text Service - Free offline-capable solution
Uses Whisper via transformers for offline speech recognition
"""

import os
import io
import torch
import numpy as np
from typing import Optional
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import warnings
warnings.filterwarnings("ignore")

class STTService:
    def __init__(self):
        self.processor: Optional[WhisperProcessor] = None
        self.model: Optional[WhisperForConditionalGeneration] = None
        self.device: str = "cpu"
        self.model_loaded = False
        
    async def initialize(self):
        """Initialize Whisper model (lazy loading)"""
        if self.model_loaded:
            return
        
        try:
            print("Loading Whisper model for speech-to-text...")
            self.device = "cpu"  # Use CPU for compatibility, can use MPS on M1 Mac if needed
            
            # Use tiny model for fast, free inference
            model_id = "openai/whisper-tiny"
            
            print(f"Loading {model_id}...")
            self.processor = WhisperProcessor.from_pretrained(model_id)
            self.model = WhisperForConditionalGeneration.from_pretrained(model_id)
            
            # Move to device if available
            if torch.backends.mps.is_available():
                try:
                    self.model = self.model.to("mps")
                    self.device = "mps"
                    print("Using MPS (Apple Silicon GPU) for Whisper")
                except Exception as e:
                    print(f"MPS not available for Whisper, using CPU: {e}")
                    self.device = "cpu"
            
            self.model_loaded = True
            print("✓ Whisper model loaded successfully for speech-to-text")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            print("Speech-to-text will use fallback method")
            self.model_loaded = False
    
    async def transcribe(self, audio_data: bytes, sample_rate: int = 16000) -> Optional[str]:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Raw audio bytes (WAV format expected)
            sample_rate: Audio sample rate (default 16000 Hz)
        
        Returns:
            Transcribed text or None if failed
        """
        if not self.model_loaded:
            await self.initialize()
        
        if not self.model_loaded or self.processor is None or self.model is None:
            return None
        
        try:
            # Convert bytes to numpy array
            # Handle WebM and WAV formats
            from io import BytesIO
            import tempfile
            import os
            
            audio_io = BytesIO(audio_data)
            audio_np = None
            
            # Try using pydub with ffmpeg (best for WebM support)
            # Note: pydub requires ffmpeg to be installed on the system
            try:
                from pydub import AudioSegment
                
                # Load audio from bytes - try to auto-detect format first
                audio_io.seek(0)
                try:
                    # Try auto-detection
                    audio_segment = AudioSegment.from_file(audio_io)
                except:
                    # If auto-detection fails, try WebM explicitly
                    audio_io.seek(0)
                    audio_segment = AudioSegment.from_file(audio_io, format="webm")
                
                # Convert to mono and 16kHz (Whisper's preferred format)
                audio_segment = audio_segment.set_channels(1).set_frame_rate(16000)
                sample_rate = 16000
                # Convert to numpy array
                audio_np = np.array(audio_segment.get_array_of_samples()).astype(np.float32) / 32768.0
                print(f"Successfully loaded audio with pydub: {len(audio_np)} samples at {sample_rate}Hz")
            except ImportError:
                print("pydub not installed, trying torchaudio...")
                # Fallback to torchaudio
                try:
                    import torchaudio
                    audio_io.seek(0)
                    # Try loading as WebM explicitly
                    waveform, sr = torchaudio.load(audio_io, format="webm")
                    # Convert to mono if stereo
                    if waveform.shape[0] > 1:
                        waveform = torch.mean(waveform, dim=0, keepdim=True)
                    # Resample to 16kHz if needed
                    if sr != 16000:
                        resampler = torchaudio.transforms.Resample(sr, 16000)
                        waveform = resampler(waveform)
                    # Convert to numpy and normalize
                    audio_np = waveform.squeeze().numpy().astype(np.float32)
                    sample_rate = 16000
                    print(f"Successfully loaded audio with torchaudio: {len(audio_np)} samples at {sample_rate}Hz")
                except Exception as e:
                    print(f"Error loading audio with torchaudio: {e}, trying wave...")
                    # Final fallback to wave module (WAV only)
                    try:
                        import wave
                        audio_io.seek(0)
                        with wave.open(audio_io, 'rb') as wav_file:
                            frames = wav_file.getnframes()
                            sample_rate = wav_file.getframerate()
                            audio_bytes = wav_file.readframes(frames)
                            audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                        print(f"Successfully loaded audio with wave: {len(audio_np)} samples at {sample_rate}Hz")
                    except Exception as e2:
                        print(f"Error loading audio with wave: {e2}")
                        return None
            except Exception as e:
                print(f"Error loading audio with pydub: {e}")
                # Try torchaudio as fallback
                try:
                    import torchaudio
                    audio_io.seek(0)
                    waveform, sr = torchaudio.load(audio_io, format="webm")
                    if waveform.shape[0] > 1:
                        waveform = torch.mean(waveform, dim=0, keepdim=True)
                    if sr != 16000:
                        resampler = torchaudio.transforms.Resample(sr, 16000)
                        waveform = resampler(waveform)
                    audio_np = waveform.squeeze().numpy().astype(np.float32)
                    sample_rate = 16000
                except Exception as e2:
                    print(f"All audio loading methods failed: {e2}")
                    return None
            
            if audio_np is None or len(audio_np) == 0:
                print("Failed to decode audio data - no valid audio samples")
                return None
            
            # Process audio
            inputs = self.processor(audio_np, sampling_rate=sample_rate, return_tensors="pt")
            
            # Move inputs to device
            if self.device == "mps":
                inputs = {k: v.to("mps") for k, v in inputs.items()}
            
            # Generate transcription
            with torch.no_grad():
                generated_ids = self.model.generate(inputs["input_features"])
            
            # Decode transcription
            transcription = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            return transcription.strip()
            
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def is_available(self) -> bool:
        """Check if STT service is available"""
        return self.model_loaded

