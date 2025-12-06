#!/usr/bin/env python3
"""
Voice functionality test script for AIris platform.
Tests both speech-to-text and text-to-speech capabilities.
"""

import speech_recognition as sr
from gtts import gTTS
import os
import time
import tempfile
import pygame

def test_speech_to_text():
    """Test speech recognition functionality"""
    print("🎤 Testing Speech-to-Text...")
    
    # Initialize recognizer
    r = sr.Recognizer()
    
    # Test with microphone
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("Listening... Speak now!")
            
            # Listen for audio with timeout
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Processing speech...")
            try:
                # Use Google's speech recognition
                text = r.recognize_google(audio)
                print(f"✅ Speech recognized: '{text}'")
                return text
            except sr.UnknownValueError:
                print("❌ Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {e}")
                return None
                
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return None

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

def test_voice_integration():
    """Test complete voice integration workflow"""
    print("\n🔄 Testing Voice Integration Workflow...")
    
    # Step 1: Speech to text
    print("\n1. Please speak a task (e.g., 'drink water', 'read a book'):")
    spoken_text = test_speech_to_text()
    
    if spoken_text:
        print(f"\n2. Converting speech to text: '{spoken_text}'")
        
        # Step 2: Text to speech confirmation
        confirmation = f"I heard you say: {spoken_text}. Is this correct?"
        print(f"\n3. Playing confirmation: '{confirmation}'")
        test_text_to_speech(confirmation)
        
        # Step 3: Simulate task processing
        task_response = f"Great! I'll help you with: {spoken_text}. Let me find the objects you need."
        print(f"\n4. Playing task response: '{task_response}'")
        test_text_to_speech(task_response)
        
        return True
    else:
        print("❌ Voice integration test failed - no speech recognized")
        return False

def main():
    """Main test function"""
    print("🎯 AIris Voice Functionality Test")
    print("=" * 40)
    
    # Test individual components
    print("\n📋 Testing Individual Components:")
    print("-" * 30)
    
    # Test TTS first (doesn't require microphone)
    tts_success = test_text_to_speech("Testing text to speech functionality.")
    
    # Test STT
    stt_success = test_speech_to_text() is not None
    
    # Test integration
    print("\n🔗 Testing Integration:")
    print("-" * 20)
    integration_success = test_voice_integration()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 25)
    print(f"Text-to-Speech: {'✅ PASS' if tts_success else '❌ FAIL'}")
    print(f"Speech-to-Text: {'✅ PASS' if stt_success else '❌ FAIL'}")
    print(f"Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    if all([tts_success, stt_success, integration_success]):
        print("\n🎉 All voice tests passed! Voice functionality is ready.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
