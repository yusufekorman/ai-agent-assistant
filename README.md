# AI Assistant with Advanced Voice and Text Interface

An intelligent AI assistant built in Python that provides seamless interaction through both text and voice interfaces, powered by advanced language models and various API integrations. Features comprehensive memory management, secure command execution, and multiple API integrations.

## 🌟 Key Features

- **Dual Interaction Modes**
  - Text-based interface for precise input
  - Voice interface with wake word detection ("Jarvis")
  - Real-time speech-to-text using RealtimeSTT
  - Text-to-speech output using pyttsx3

- **Advanced AI Integration**
  - OpenAI's function calling API integration
  - Dynamic tool result processing
  - Asynchronous request handling
  - Context-aware responses using vector embeddings
  - Advanced memory management with SQLite backend
  - Multi-turn conversation support
  - Configurable model parameters (temperature, max_tokens)

- **Tool System**
  - Function calling based tool execution
  - Dynamic tool result processing for natural responses
  - Built-in tools:
    - Weather information (OpenWeatherMap)
    - Wikipedia knowledge access
    - News updates
    - System command execution
    - Browser control
  - Secure execution with allowlists
  - Automatic result refinement through AI

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

## 🔧 Technical Requirements

- Python 3.8 or higher
- Required Python packages:
  - OpenAI SDK
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
  - llm_provider: 'openai'
  - model: 'gpt-4o-mini'
  - api_url: 'https://api.openai.com/v1'
  - whisper_model_type: 'base'
  - wake_words: 'jarvis'
  - auth_token: 'your_openai_api_key'
  - temperature: 0.7
  - max_tokens: 2000
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
python main.py
```

2. **Choose Input Mode**
- Enter `1` for text input mode
- Enter `2` for voice input mode with wake word "Jarvis"
  - Select your microphone from the list

3. **Available Tools**
- Weather queries: "What's the weather like in London?"
- Knowledge queries: "Tell me about quantum computing"
- News updates: "Show me the latest news about technology"
- System commands (Restricted): 
  - Windows: "Show me running processes", "What's the current time?"
- Browser: "Open GitHub website"

## 📋 System Architecture

### Tool System
The application uses OpenAI's function calling API for tool execution:
- Function definitions for each tool capability
- Dynamic tool result processing
- Natural language refinement of tool outputs
- Secure execution with allowlists
- Error handling and timeouts

### Memory Management
The application uses an advanced vector-based memory system:
- Vector embeddings using spaCy's en_core_web_md model
- Efficient similarity search with numpy vectorization
- SQLite backend for persistent storage
- Batch processing for large operations
- Auto-cleanup of old vectors
- Thread-safe operations

### Query System
Function calling based query handling:
- OpenAI API integration
- Tool execution framework
- Context injection for better responses
- Memory vector integration
- Dynamic response processing

### Response Execution
Secure tool execution system:
- Function calling based execution
- Allowlist-based filtering
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
│   ├── execute_response.py  # Tool execution
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
- Tool execution tests
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

This project is licensed under the GPL 3.0 License - see the [LICENSE](LICENSE) file for details.
