import pyttsx3
from RealtimeSTT import AudioToTextRecorder
import asyncio
import aiohttp
import yaml
import speech_recognition as sr

from utils.execute_response import execute_response
from utils.query import query_llm
from utils.memory_manager import MemoryManager
from tools import DYNAMIC_TOOLS

# Initialize text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
engine.setProperty('voice', engine.getProperty('voices')[0].id)

# Initialize memory manager
memory_manager = MemoryManager()

# Read system prompt
with open("system_prompt.txt", "r") as file:
    system_prompt = file.read()

# Global variables
system_ip = None
input_mode = 1  # Default to text input

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

    _secrets = config.get("secrets", {})
    secrets = {key: value for secret in _secrets for key, value in secret.items()}

    _config = config.get("config", {})
    config = {key: value for secret in _config for key, value in secret.items()}

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

async def process_tool_result(tool_name: str, result: str, user_input: str):
    """Process tool result through AI if needed"""
    if tool_name in DYNAMIC_TOOLS:
        ai_response = await query_llm(
            prompt=user_input,
            answer=result,  # Pass the tool result as context
            system_ip=system_ip or "unknown",
            config=config,
            model=config.get('llm_model', 'gpt-3.5-turbo'),
            system_prompt=system_prompt,
            current_tool=tool_name
        )
        if ai_response:
            response = await execute_response(
                ai_response,
                user_input,
                {
                    "secrets": secrets,
                    "system_ip": system_ip or "unknown",
                },
                model=config.get('llm_model', 'gpt-3.5-turbo'),
                config=config,
                dynamic_tools=DYNAMIC_TOOLS
            )
            return response if response else result
    return result

async def handleAI(user_input):
    # Process input and get AI response
    all_texts = memory_manager.getItems(range(len(memory_manager.texts)))

    ai_response = await query_llm(
        prompt=user_input,
        memory_texts=all_texts,
        system_ip=system_ip or "unknown",
        config=config,
        model=config.get('llm_model', 'gpt-3.5-turbo'),
        system_prompt=system_prompt
    )

    # Handle AI response
    if ai_response:
        response = await execute_response(
            ai_response,
            user_input,
            {
                "secrets": secrets,
                "system_ip": system_ip or "unknown",
            },
            model=config.get('llm_model', 'gpt-3.5-turbo'),
            config=config,
            dynamic_tools=DYNAMIC_TOOLS  # Pass the dynamic tools list
        )
        if response:
            say(response)
    else:
        print("Failed to get response from AI.")

async def main():
    try:
        global input_mode, memory_manager
        
        # Initialize system
        await init_system()
        print("System initialized")
        print("\nAI Assistant is ready!")
        
        # Select input mode
        input_mode = select_input_mode()

        if input_mode == 2:
            print("Voice input mode selected. Please select the microphone you want to use.")
            for i, device in enumerate(sr.Microphone.list_microphone_names()):
                print(f"{i+1}. {device}")
            choice = int(input("Your choice: "))
        
        # Clean program exit with Ctrl+C
        while True:
            try:
                if input_mode == 1:
                    user_input = input("You: ").strip()
                    await handleAI(user_input)
                else:
                    print("Wait until it says 'say jarvis' before speaking.")
                    recorder = AudioToTextRecorder(
                        model=config.get("whisper_model_type", "base"), 
                        wake_words=config.get("wake_words", ["jarvis"]), 
                        language="en",
                        input_device_index=choice-1
                    )
                    await handleAI(recorder.text())
            except KeyboardInterrupt:
                print("\nShutting down program...")
                del memory_manager  # Call MemoryManager's __del__ method
                break
                    
    except Exception as e:
        print(f"An error occurred while starting the program: {e}")

if __name__ == "__main__":
    asyncio.run(main())
