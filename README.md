# AI Assistant with Advanced Voice and Text Interface

An intelligent AI assistant built in Python that provides seamless interaction through both text and voice interfaces, powered by advanced language models and various API integrations.

## 🌟 Key Features

- **Dual Interaction Modes**
  - Text-based interface for precise input
  - Voice interface with wake word detection ("Jarvis")
  - Natural language processing capabilities

- **Advanced AI Integration**
  - Supports multiple LLM providers:
    - LM Studio (Local LLMs)
    - Ollama (Local LLMs)
    - GPT (OpenAI)
    - Deepseek (Cloud API)
  - Real-time speech-to-text using Whisper
  - Context-aware responses
  - Memory management for conversation history

- **API Integrations**
  - Weather information retrieval
  - Wikipedia knowledge access
  - Real-time news updates
  - Stock market data (via yfinance)

- **System Capabilities**
  - System command execution with security restrictions
  - URL handling and web browsing
  - Text-to-speech output
  - Configurable settings via YAML

## 🔧 Technical Requirements

- Python 3.8 or higher
- CUDA-compatible GPU (recommended for optimal performance)
- Required Python packages:
  - PyTorch (with CUDA support)
  - transformers
  - pyttsx3
  - RealtimeSTT
  - aiohttp
  - Other dependencies listed in requirements.txt

## 📦 Installation

1. **Clone the Repository**
```bash
git clone https://github.com/yusufekorman/ai-agent-assistant.git
cd ai-agent-assistant
```

2. **Set Up Virtual Environment**
```bash
python -m venv .venv
# For Windows:
.venv\Scripts\activate
# For Linux/Mac:
source .venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
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
  - temperature: 0.7  # Model temperature (0-1)
  - max_tokens: -1  # Maximum tokens in response
secrets:
  - auth_token: ''  # Required for GPT and Deepseek
  - weather_api_key: 'your_openweathermap_api_key'
  - news_api_key: 'your_newsapi_key'
```

## 🤖 LLM Configuration

The assistant supports multiple LLM providers that can be configured in `config.yaml`:

### LM Studio (Local)
```yaml
config:
  - llm_provider: 'lm_studio'
  - api_url: 'http://localhost:1234/v1/chat/completions'
  - model: 'llama-3.2-3b-instruct'
```

### Ollama (Local)
```yaml
config:
  - llm_provider: 'ollama'
  - api_url: 'http://localhost:11434/api/chat'
  - model: 'llama2'
```

### GPT (OpenAI)
```yaml
config:
  - llm_provider: 'gpt'
  - api_url: 'https://api.openai.com/v1/chat/completions'
  - model: 'gpt-3.5-turbo'
secrets:
  - auth_token: 'your-openai-api-key'
```

### Deepseek
```yaml
config:
  - llm_provider: 'deepseek'
  - api_url: 'https://api.deepseek.com/v1/chat/completions'
  - model: 'deepseek-chat'
secrets:
  - auth_token: 'your-deepseek-api-key'
```

## 🚀 Usage

1. **Start the Application**
```bash
python main.py
```

2. **Choose Input Mode**
- Enter `1` for text input mode
- Enter `2` for voice input mode with wake word "Jarvis"

3. **Available Commands**
- Weather queries: "What's the weather like in London?"
- Knowledge queries: "Tell me about quantum computing"
- News updates: "Show me the latest news about technology"
- Stock information: "Get stock price for AAPL"
- System commands: "Open Chrome" or "Create a new folder"

## 📋 System Architecture

### Logging System
The application uses a robust logging system implemented in `utils/logger.py`:
- Logs are stored in the `logs` directory with daily rotation
- Log files follow the format: `assistant_YYYY-MM-DD.log`
- Multiple logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Both file and console logging with different levels
- UTF-8 encoding support for international character handling

### Query System
The LM Studio client (`utils/query.py`) handles AI model interactions:
- Asynchronous request handling with retry mechanism
- Session management with connection pooling
- Configurable timeout and retry settings
- Memory vector integration for context awareness
- Structured error handling and logging

### Response Execution
The response execution system (`utils/execute_response.py`) provides:
- Secure command execution with allowlist
- Safe URL handling with domain restrictions
- Async execution of system commands
- Integrated browser command handling
- Need-based request processing for weather, wiki, and news

## 📁 Project Structure

```
ai-agent-assistant/
├── main.py              # Main application entry point
├── config.yaml          # Configuration settings
├── requirements.txt     # Python dependencies
├── tests/               # Test suite directory
│   ├── run_tests.py     # Test runner script
│   ├── test_execute_response.py  # Response execution tests
│   ├── test_memory_manager.py    # Memory management tests
│   ├── test_query.py     # Query handling tests
├── utils/
│   ├── benchmark.py        # Performance benchmarking
│   ├── execute_response.py  # Response execution logic
│   ├── query.py            # LLM query handling
│   ├── tool_utils.py       # Utility functions
│   ├── logger.py          # Logging system
│   ├── index.py           # Core utilities
│   └── memory_manager.py  # Conversation memory management
├── logs/                # Log files directory
├── test_prompts.md      # Test prompts and instructions
└── system_prompt.txt    # System prompt for AI model
```

## 🧪 Testing

The assistant comes with a comprehensive test suite in the `tests` directory:
- Unit tests for core functionality
- Integration tests for API interactions
- Memory management tests
- Response execution tests

For a complete set of test prompts and instructions, see [`test_prompts.md`](test_prompts.md).

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Submit issues for bug reports or feature requests
- Fork the repository
- Create pull requests for improvements

## ⚠️ Disclaimer

This software is provided "as is", without warranty of any kind. Users should exercise caution when using system commands and ensure proper configuration of API keys and dependencies.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.