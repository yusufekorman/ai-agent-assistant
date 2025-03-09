# AI Assistant: Voice and Text-Based Intelligent Assistant

An intelligent assistant built in Python that provides seamless interaction through both text and voice interfaces, powered by advanced language models and various API integrations.

## 🌟 Key Features

- **Dual Interaction Modes**
  - Text-based interface for precise input
  - Voice interface with "Jarvis" wake word
  - Real-time speech recognition using RealtimeSTT
  - Text-to-speech output using pyttsx3
  - Multi-language support

- **AI Integration**
  - LM Studio or OpenAI API support
  - Function calling based tool system
  - Context-aware responses
  - Advanced memory management with SQLite backend
  - Multi-turn conversation support
  - Configurable model parameters (temperature, max_tokens)

- **Tool System**
  - Weather information (OpenWeatherMap)
  - Wikipedia knowledge access
  - News updates
  - System command execution
  - Browser control
  - Secure execution with allowlists
  - Custom tool integration
  - Automatic result refinement

- **Memory Management**
  - SQLite-based persistent storage
  - Batch processing with ThreadPoolExecutor
  - Auto-save functionality
  - Configurable vector limits and cleanup

- **Security Features**
  - Secure command execution with allowlist
  - Domain restrictions for URL handling
  - Safe API key management
  - Input validation and sanitization
  - Error handling and logging
  - Timeout controls

## 🔧 Technical Requirements

- Python 3.8 or higher
- Required Python packages:
  - RealtimeSTT
  - pyttsx3
  - PyYAML
  - aiohttp
  - beautifulsoup4
  - numpy
  - Other dependencies in requirements.txt

## 📦 Installation

1. **Clone the Repository**
```bash
git clone git@github.com:yusufekorman/ai-agent-assistant.git
cd ai-agent-assistant
```

2. **Set Up Virtual Environment**
```bash
# For Windows:
python -m venv .venv
.venv\Scripts\activate

# For Linux/Mac:
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure the Application**
Copy `config.yaml.template` to `config.yaml` and edit it:
```yaml
config:
  - llm_provider: 'lm_studio'  # lm_studio or openai
  - model: 'llama-3.2-3b-instruct'
  - api_url: 'http://localhost:1234/v1'
  - whisper_model_type: 'base'
  - wake_words: 'jarvis'
  - auth_token: ''  # OpenAI API key (if needed)
  - temperature: 0.7
  - max_tokens: -1
  - batch_size: 100
  - max_vectors: 1000
  - auto_save: true
  - timeout: 30
secrets:
  - weather_api_key: 'your_openweathermap_api_key'
  - news_api_key: 'your_newsapi_key'
```

## 🚀 Usage

1. **Start the Application**
```bash
# For Windows:
python main.py

# For Linux/Mac:
python3 main.py
```

2. **Choose Input Mode**
- Press `1` for text input mode
- Press `2` for voice input mode with "Jarvis" wake word
  - Select your microphone from the list

3. **Available Tools**
- Weather queries: "What's the weather like in London?"
- Knowledge queries: "Tell me about quantum computing"
- News updates: "Show me the latest news about technology"
- System commands (Restricted):
  - Windows: "Show me running processes", "What's the current time?"
- Browser: "Open GitHub website"

## 📁 Project Structure

```
ai-assistant/
├── main.py              # Application entry point
├── config.yaml          # Configuration settings
├── requirements.txt     # Python dependencies
├── tests/              # Test suite
│   ├── run_tests.py
│   ├── test_execute_response.py
│   ├── test_memory_manager.py
│   └── test_query.py
├── utils/              # Core utilities
│   ├── execute_response.py  # Tool execution
│   ├── query.py            # LLM interaction
│   ├── memory_manager.py   # Memory management
│   ├── tool_utils.py       # API utilities
│   ├── logger.py           # Logging system
│   └── index.py            # Common utilities
├── logs/               # Log files directory
└── system_prompt.txt   # AI system prompt
```

## 🧪 Testing

Comprehensive test suite included:
```bash
python -m pytest tests/
```

## ⚠️ Disclaimer

This software is provided "as is", without warranty of any kind. Users should exercise caution when using system commands and ensure proper configuration of API keys and dependencies.

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
