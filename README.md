# AI Assistant with Advanced Voice and Text Interface

An intelligent AI assistant built in Python that provides seamless interaction through both text and voice interfaces, powered by advanced language models and various API integrations.

## 🌟 Key Features

- **Dual Interaction Modes**
  - Text-based interface for precise input
  - Voice interface with wake word detection ("Jarvis")
  - Natural language processing capabilities

- **Advanced AI Integration**
  - Powered by LLaMA 3.2B Instruct model (Optional, can be changable)
  - Real-time speech-to-text using Whisper
  - Context-aware responses
  - Memory management for conversation history

- **API Integrations**
  - Weather information retrieval
  - Wikipedia knowledge access
  - Real-time news updates
  - Stock market data (via yfinance)

- **System Capabilities**
  - System command execution
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
  - lm_studio_completions_url: 'http://localhost:1234/v1/chat/completions'
  - llm_model: 'llama-3.2-3b-instruct'
  - whisper_model_type: 'base'
  - wake_words: ['jarvis']
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

3. **Available Commands**
- Weather queries: "What's the weather like in London?"
- Knowledge queries: "Tell me about quantum computing"
- News updates: "Show me the latest news about technology"
- Stock information: "Get stock price for AAPL"
- System commands: "Open Chrome" or "Create a new folder"

## 🧪 Testing

The assistant comes with a comprehensive set of test prompts to verify functionality. Here are some basic examples you can try:

### Basic Tests
```
# Simple Interaction
"Hello"
"What can you do?"
"Tell me a joke"

# Weather Queries
"What's the weather like in London?"
"Weather forecast for Istanbul"

# Knowledge Tests
"Tell me about Albert Einstein"
"Explain artificial intelligence"

# System Commands
"What time is it?"
"Open Calculator"
```

### Voice Mode Tests
```
"Jarvis"                      # Wake word
"Jarvis, what's the weather?" # Weather query
"Jarvis, tell me a joke"      # Entertainment
"Jarvis, open YouTube"        # System command
```

For a complete set of test prompts covering all features including:
- API Integration Tests
- Memory and Context Tests
- Complex Multi-Task Queries
- Error Handling Tests
- Stock Market Queries
- Language Processing Tests
- And more...

Check out the [`test_prompts.md`](test_prompts.md) file in the project root directory for a comprehensive set of test examples with detailed explanations.

## 📁 Project Structure

```
ai-agent-assistant/
├── main.py              # Main application entry point
├── config.yaml          # Configuration settings
├── requirements.txt     # Python dependencies
├── utils/
│   ├── execute_response.py  # Response execution logic
│   ├── query.py            # LLM query handling
│   ├── tool_utils.py       # Utility functions
│   ├── index.py           # Core utilities
│   └── memory_manager.py  # Conversation memory management
└── system_prompt.txt    # System prompt for AI model
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Submit issues for bug reports or feature requests
- Fork the repository
- Create pull requests for improvements

## ⚠️ Disclaimer

This software is provided "as is", without warranty of any kind. Users should exercise caution when using system commands and ensure proper configuration of API keys and dependencies.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.