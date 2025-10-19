#!/usr/bin/env python3
"""
Simple voice functionality test - TTS only (no microphone required)
"""

from gtts import gTTS
import pygame
import tempfile
import os
import time

def test_text_to_speech(text="Hello, this is a test of the text-to-speech functionality."):
    """Test text-to-speech functionality"""
    print(f"🔊 Testing Text-to-Speech with: '{text}'")
    
    try:
        # Create TTS object
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            
            # Play the audio using pygame
            pygame.mixer.init()
            pygame.mixer.music.load(tmp_file.name)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Clean up
            pygame.mixer.quit()
            os.unlink(tmp_file.name)
            
        print("✅ Text-to-speech completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Text-to-speech error: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 AIris Voice TTS Test (No Microphone Required)")
    print("=" * 50)
    
    # Test TTS with different messages
    test_messages = [
        "Hello, this is a test of the text-to-speech functionality.",
        "The AIris platform now supports voice guidance.",
        "You can speak your tasks and hear responses.",
        "Voice functionality is working correctly."
    ]
    
    success_count = 0
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing message: '{message}'")
        if test_text_to_speech(message):
            success_count += 1
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n📊 Test Results: {success_count}/{len(test_messages)} TTS tests passed")
    
    if success_count == len(test_messages):
        print("🎉 All TTS tests passed! Voice output is ready.")
    else:
        print("⚠️ Some TTS tests failed.")

if __name__ == "__main__":
    main()
