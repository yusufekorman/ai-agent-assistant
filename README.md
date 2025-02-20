# AI Assistant with Advanced Voice and Text Interface

An intelligent AI assistant built in Python that provides seamless interaction through both text and voice interfaces, powered by advanced language models and various API integrations. Features comprehensive memory management, secure command execution, and multiple API integrations.

## 🌟 Key Features

- **Dual Interaction Modes**
  - Text-based interface for precise input
  - Voice interface with wake word detection ("Jarvis")
  - Real-time speech-to-text using RealtimeSTT
  - Text-to-speech output using pyttsx3

- **Advanced AI Integration**
  - Multiple LLM providers supported:
    - LM Studio (Local LLMs)
    - OpenAI
  - Asynchronous request handling with timeout and retry mechanisms
  - Context-aware responses using vector embeddings
  - Advanced memory management with SQLite backend
  - Multi-turn conversation support
  - Configurable model parameters (temperature, max_tokens)

- **Memory Management System**
  - Vector-based conversation storage using spaCy
  - Efficient similarity search with numpy
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
  - Timeout controls for commands

- **API Integrations**
  - Weather information (OpenWeatherMap)
  - Wikipedia knowledge access
  - Real-time news updates
  - Stock market data (yfinance)

## 🔧 Technical Requirements

- Python 3.8 or higher
- Required Python packages:
  - PyTorch (with CUDA support)
  - spaCy (with en_core_web_md model)
  - transformers
  - pyttsx3
  - RealtimeSTT
  - aiohttp
  - Other dependencies in requirements.txt

## 📦 Installation

1. **Clone the Repository**
```bash
git clone https://github.com/yusufekorman/ai-agent-assistant.git
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
python -m spacy download en_core_web_md
```

4. **Configure the Application**
Create a `config.yaml` file in the root directory:
```yaml
config:
  - llm_provider: 'lm_studio'  # Available: lm_studio, ollama, gpt, deepseek
  - model: 'llama-3.2-3b-instruct'  # Model name for selected provider
  - api_url: 'http://localhost:1234/v1/chat/completions'  # API endpoint URL
  - whisper_model_type: 'base'
  - wake_words: 'jarvis'
  - auth_token: ''  # Required for openai provider
  - temperature: 0.7  # Model temperature (0-1)
  - max_tokens: 2000  # Maximum tokens in response
  - batch_size: 100  # Size of processing batches
  - max_vectors: 1000  # Maximum vectors in memory
  - auto_save: true  # Enable auto-saving
  - timeout: 30  # Request timeout in seconds
secrets:
  - weather_api_key: 'your_openweathermap_api_key'
  - news_api_key: 'your_newsapi_key'
```

## 🚀 Usage

1. **Start the Application**
```bash
python main.py
```

2. **Choose Input Mode**
- Enter `1` for text input mode
- Enter `2` for voice input mode with wake word "Jarvis"
  - Select your microphone from the list

3. **Available Commands**
- Weather queries: "What's the weather like in London?"
- Knowledge queries: "Tell me about quantum computing"
- News updates: "Show me the latest news about technology"
- System commands (Restricted): 
  - Windows: "cmd:notepad", "ps:Get-Date"
  - Browser: "open_browser:https://google.com"

## 📋 System Architecture

### Memory Management
The application uses an advanced vector-based memory system:
- Vector embeddings using spaCy's en_core_web_md model
- Efficient similarity search with numpy vectorization
- SQLite backend for persistent storage
- Batch processing for large operations
- Auto-cleanup of old vectors
- Thread-safe operations

### Query System
Asynchronous query handling system:
- Multiple LLM provider support
- Timeout and retry mechanisms
- Context injection for better responses
- Memory vector integration
- Custom response formatting

### Response Execution
Secure command execution system:
- Allowlist-based command filtering
- Domain-restricted URL handling
- Asynchronous execution
- Timeout controls
- Comprehensive error handling

### Logging System
Robust logging implementation:
- Daily log rotation
- Multiple logging levels
- Both file and console logging
- UTF-8 encoding support
- Detailed error tracking

## 📁 Project Structure

```
ai-agent-assistant/
├── main.py              # Application entry point
├── config.yaml          # Configuration settings
├── requirements.txt     # Python dependencies
├── tests/              # Test suite
│   ├── run_tests.py    # Test runner
│   ├── test_execute_response.py
│   ├── test_memory_manager.py
│   └── test_query.py
├── utils/              # Core utilities
│   ├── execute_response.py  # Response execution
│   ├── query.py            # LLM interaction
│   ├── memory_manager.py   # Vector store
│   ├── tool_utils.py       # API utilities
│   ├── logger.py           # Logging system
│   └── index.py            # Common utilities
├── logs/               # Log files directory
└── system_prompt.txt   # AI system prompt
```

## 🧪 Testing

Comprehensive test suite included:
- Unit tests for core components
- Integration tests for API interactions
- Memory management tests
- Command execution tests
- Configuration tests

Run tests with:
```bash
python -m pytest tests/
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## ⚠️ Disclaimer

This software is provided "as is", without warranty of any kind. Users should exercise caution when using system commands and ensure proper configuration of API keys and dependencies.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.