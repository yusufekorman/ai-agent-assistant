# AI Assistant with Voice Interface

A Python-based AI assistant that can interact through both text and voice and various API integrations.

## ⚠️ Disclaimer

This software is provided "as is", without warranty of any kind. By using this software, you acknowledge and agree that:

- You are using it at your own risk
- The authors are not responsible for any damage to your computer, data, or any other property
- The authors are not liable for any misuse of the software or its commands
- System commands should be used with caution as they can modify your system

## Features

- Text and voice interaction modes
- Wake word detection ("Jarvis")
- Integration with various APIs:
  - Weather information
  - Wikipedia summaries
  - News updates
- System command execution capability
- URL opening functionality

## Requirements

- Python 3.8+
- PyTorch
- transformers
- pyttsx3
- RealtimeSTT ([GitHub](https://github.com/KoljaB/RealtimeSTT))
- Other dependencies in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yusufekorman/ai-agent-assistant.git
cd ai-agent-assistant
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
Create a `config.yaml` file:
```yaml
config:
  - llm_model: 'unsloth/llama-3.2-3b-instruct'
  - whisper_model_type: 'base'
  - wake_words: 'jarvis' # only RealtimeSTT supported
secrets:
  - weather_api_key: ''
```

## Usage

1. Start the program:
```bash
python main.py
```

2. Select input mode:
   - Text mode (1): Type your queries directly
   - Voice mode (2): Use voice commands, starting with "Jarvis"

3. Available commands:
   - Weather: "What's the weather in [city]?"
   - Wikipedia: "Tell me about [topic]"
   - News: "Show me news about [topic]"
   - System: Various system commands and URL opening

## Project Structure

- `main.py`: Main application file
- `utils/`:
  - `database_pool.py`: SQLite database connection management (Do not use in production)
  - `execute_response.py`: Response execution and API integrations
  - `query.py`: LLM query handling
  - `tool_utils.py`: Utility functions for tools

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 