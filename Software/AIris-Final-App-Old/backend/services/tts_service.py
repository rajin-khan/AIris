"""
Text-to-Speech Service
"""

from gtts import gTTS
import io
from typing import Optional

class TTSService:
    def __init__(self):
        self.default_lang = 'en'
    
    async def generate(self, text: str, lang: str = 'en') -> Optional[bytes]:
        """Generate speech from text"""
        if not text:
            return None
        
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer.read()
        except Exception as e:
            print(f"TTS generation failed: {e}")
            return None
    
    def estimate_duration(self, text: str) -> float:
        """Estimate audio duration based on text length"""
        # Average speaking rate: ~150 words per minute = 2.5 words per second
        word_count = len(text.split())
        duration = (word_count / 2.5) + 0.5  # +0.5 seconds buffer
        return max(duration, 2.0)  # Minimum 2 seconds


