import json
import speech_recognition as sr
import pyttsx3
from transformers import pipeline
import torch
import asyncio
from voice_auth import VoiceAuthenticator
import aiohttp

from utils.database_pool import DatabasePool
from utils.vector_memory_manager import SimpleVectorMemory
from utils.execute_response import execute_response
from utils.query import query_lm_studio

# Initialize components
voice_auth = VoiceAuthenticator()
db_pool = DatabasePool()
memory_manager = SimpleVectorMemory()

# Initialize text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
engine.setProperty('voice', engine.getProperty('voices')[0].id)

# Global variables
system_ip = None
input_mode = 1  # Default to text input

# Load Whisper model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base.en",
    device=device,
    model_kwargs={"weights_only": True}
)

async def init_system():
    """Initialize system components"""
    global system_ip
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.ipify.org") as response:
                system_ip = await response.text()
    except Exception as e:
        print(f"Error getting IP: {e}")
        system_ip = "unknown"
    
    # Initialize database
    conn = await db_pool.get_connection()
    try:
        await db_pool._initialize_tables(conn)
    finally:
        await db_pool.release_connection(conn)

def select_input_mode():
    """Select between text and voice input modes"""
    while True:
        print("\nSelect input mode:")
        print("1. Text input")
        print("2. Voice input")
        choice = input("Your choice (1/2): ").strip()
        if choice in ["1", "2"]:
            return int(choice)
        print("Invalid choice, please try again.")

async def listen():
    """Get user input based on selected mode"""
    if input_mode == 1:  # Text mode
        return input("You: ")
    
    # Voice mode
    try:
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 1000
        recognizer.dynamic_energy_threshold = False
        
        with sr.Microphone() as source:
            print("\nI'm listening...")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
            
            print("Processing audio...")
            text = recognizer.recognize_whisper(audio, model="base", language="english")
            
            if text:
                print(f"I understood: {text}")
                return text.strip()
            return ""
            
    except Exception as e:
        print(f"Speech recognition error: {e}")
        return ""

def say(text):
    """Output text response and speak it"""
    print(f"AI: {text}")
    engine.say(text)
    engine.runAndWait()

async def main():
    try:
        global input_mode
        
        # Initialize system
        await init_system()
        print("System initialized")
        print("\nAI Assistant is ready!")
        
        with open("secrets.json", "r") as file:
            secrets = json.load(file)
        
        # Select input mode
        input_mode = select_input_mode()
        
        while True:
            try:
                # Handle voice mode wake word
                if input_mode == 2 and not await voice_auth.wait_for_wake_word():
                    continue
                
                # Get user input
                user_input = await listen()
                if not user_input:
                    print("Please try again.")
                    continue
                
                # Process input and get AI response
                ai_response = await query_lm_studio(
                    prompt=user_input,
                    memory_manager=memory_manager,
                    system_ip=system_ip or "unknown",
                )
                
                # Handle AI response
                if ai_response and "choices" in ai_response:
                    ai_response = ai_response["choices"][0]["message"]["content"].replace("\n", "")
                    response = await execute_response(ai_response, user_input, memory_manager, {
                        "secrets": secrets,
                        "system_ip": system_ip or "unknown",
                    })
                    say(response)
                else:
                    print("AI did not respond or returned an invalid response.")
                
                # Handle voice mode sleep
                if input_mode == 2:
                    await asyncio.sleep(1)
                    engine.say("Going back to sleep mode")
                    engine.runAndWait()
                    
            except Exception as e:
                print(f"Error in interaction loop: {e}")
                if input_mode == 2:
                    await asyncio.sleep(1)
                    
    except Exception as e:
        print(f"An error occurred while starting the program: {e}")

if __name__ == "__main__":
    asyncio.run(main())
