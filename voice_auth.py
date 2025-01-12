import speech_recognition as sr

class VoiceAuthenticator:
    def __init__(self, wake_word="hey jarvis"):
        self.wake_word = wake_word.lower()
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 1000  # Increase sensitivity
        self.recognizer.dynamic_energy_threshold = False  # Disable dynamic adjustment
        
    async def wait_for_wake_word(self) -> bool:
        """Listen for wake word without voice validation"""
        try:
            with sr.Microphone() as source:
                print("\nListening for wake word...")
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                
                try:
                    text = self.recognizer.recognize_whisper(audio, model="base", language="english")
                    text = text.lower().strip()
                    print(f"Heard: {text}")
                    
                    return self.wake_word in text
                    
                except sr.UnknownValueError:
                    return False
                    
        except sr.WaitTimeoutError:
            return False
        except Exception as e:
            print(f"Error in wake word detection: {e}")
            return False 