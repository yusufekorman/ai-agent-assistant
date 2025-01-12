# AI Assistant with Voice Interface

A Python-based AI assistant that can interact through both text and voice, featuring memory management and various API integrations.

## Turkish

[Türkçe README](README-tr.md)

## ⚠️ Disclaimer

This software is provided "as is", without warranty of any kind. By using this software, you acknowledge and agree that:

- You are using it at your own risk
- The authors are not responsible for any damage to your computer, data, or any other property
- The authors are not liable for any misuse of the software or its commands
- System commands should be used with caution as they can modify your system

## Features

- Text and voice interaction modes
- Wake word detection ("Hey Jarvis")
- Memory management with SQLite database
- Integration with various APIs:
  - Weather information
  - Stock prices
  - Wikipedia summaries
  - News updates
- System command execution capability
- URL opening functionality

## Requirements

- Python 3.8+
- PyTorch
- transformers
- SpeechRecognition
- pyttsx3
- sentence-transformers
- Other dependencies in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yusufekorman/ai-assistant.git
cd ai-assistant
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API keys:
Create a `secrets.json` file with your API keys:
```json
{
    "weather_api_key": "your_openweathermap_key"
}
```

## Usage

1. Start the program:
```bash
python main.py
```

2. Select input mode:
   - Text mode (1): Type your queries directly
   - Voice mode (2): Use voice commands, starting with "Hey Jarvis"

3. Available commands:
   - Weather: "What's the weather in [city]?"
   - Stocks: "What's the price of [stock symbol]?"
   - Wikipedia: "Tell me about [topic]"
   - News: "Show me news about [topic]"
   - System: Various system commands and URL opening

## Project Structure

- `main.py`: Main application file
- `voice_auth.py`: Voice authentication and wake word detection
- `utils/`:
  - `database_pool.py`: SQLite database connection management
  - `vector_memory_manager.py`: Memory management with vector similarity
  - `execute_response.py`: Response execution and API integrations
  - `query.py`: LLM query handling

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 