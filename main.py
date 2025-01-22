import pyttsx3
from RealtimeSTT import AudioToTextRecorder
import asyncio
import aiohttp
import yaml

from utils.execute_response import execute_response
from utils.query import query_lm_studio
from utils.index import outputCleaner

# Initialize text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
engine.setProperty('voice', engine.getProperty('voices')[0].id)

# Global variables
system_ip = None
input_mode = 1  # Default to text input

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

    _secrets = config.get("secrets", {})
    secrets = {key: value for secret in _secrets for key, value in secret.items()}

    _config = config.get("config", {})
    config = {key: value for secret in _config for key, value in secret.items()}

    print("Config loaded")
    print(f"Config: {config}")

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

def say(text):
    """Output text response and speak it"""
    print(f"AI: {text}")
    engine.say(text)
    engine.runAndWait()

async def handleAI(user_input):
    # Process input and get AI response
    ai_response = await query_lm_studio(
        prompt=user_input,
        system_ip=system_ip or "unknown",
        model=config.get('llm_model', 'llama-3.2-3b-instruct')
    )

    # Handle AI response
    if ai_response and "choices" in ai_response:
        ai_response = ai_response["choices"][0]["message"]["content"]

        ai_response = outputCleaner(ai_response)
        
        response = await execute_response(ai_response, user_input, {
            "secrets": secrets,
            "system_ip": system_ip or "unknown",
        }, model=config.get('llm_model', 'llama-3.2-3b-instruct'))
        say(response)
    else:
        print("AI did not respond or returned an invalid response.")

async def main():
    try:
        global input_mode
        
        # Initialize system
        await init_system()
        print("System initialized")
        print("\nAI Assistant is ready!")
        
        # Select input mode
        input_mode = select_input_mode()
        
        # Get user input
        while True:
            if input_mode == 1:
                await handleAI(input("You: ").strip())
            else:
                print("Wait until it says 'say jarvis' before speaking.")
                recorder = AudioToTextRecorder(model=config.get("whisper_model_type", "base"), wake_words=config.get("wake_words", ["jarvis"]), language="en")
                await handleAI(recorder.text())
                    
    except Exception as e:
        print(f"An error occurred while starting the program: {e}")

if __name__ == "__main__":
    asyncio.run(main())
