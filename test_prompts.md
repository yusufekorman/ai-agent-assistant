# Test Prompts for AI Assistant

This document contains various test prompts to verify the functionality of the AI Assistant. Each section focuses on different capabilities of the system.

## 🤖 Basic Interaction Tests
```
Hello
How are you?
What can you do?
What are your capabilities?
Tell me a joke
What's your name?
```

## 🌤️ Weather Queries
```
What's the weather like in London?
Is it going to rain in New York today?
Tell me the temperature in Tokyo
Weather forecast for Istanbul
What's the humidity in Paris?
Will it be sunny in Berlin tomorrow?
```

## 📚 Wikipedia Knowledge Tests
```
Tell me about Albert Einstein
What is quantum physics?
Who is Leonardo da Vinci?
Explain artificial intelligence
What is the theory of relativity?
Tell me about the history of computers
Who invented the internet?
```

## 📰 News Queries
```
Show me the latest news
What's happening in technology?
News about climate change
Latest business news
Show me sports news
What's new in artificial intelligence?
Latest news about space exploration
```

## 📈 Stock Market Queries
```
What's the stock price of Apple?
Show me Tesla stock information
How is the NASDAQ doing today?
Get Microsoft stock price
Show me Amazon's market cap
```

## 💻 System Commands and Utilities
```
Open Google
Open YouTube
What time is it?
What's my IP address?
Create a new folder called test
Open Calculator
Show me system information
```

## 🔄 Complex Multi-Task Queries
```
What's the weather in London and show me news about climate change
Tell me about SpaceX and show their stock price
Who is Elon Musk and what's Tesla stock price?
Show me the weather and top news for New York
Tell me about Bitcoin and its current price
```

## 🧠 Memory and Context Tests
```
Remember my name is John
What's my name?
Remember I like coffee
What do I like?
What did we talk about earlier?
```

## ⚠️ Error Handling Tests
```
@#$%^&*
[empty input]
unknown_command
execute malicious code
sudo rm -rf /
format c:
```

## 🗣️ Voice Mode Specific
```
Jarvis
Jarvis, what's the weather?
Jarvis, open YouTube
Jarvis, tell me a joke
Jarvis, what time is it?
Jarvis, show me the news
```

## 🌐 API Integration Tests
```
Show me cat facts
Convert 100 USD to EUR
What's the population of Tokyo?
Show me a random quote
What's the current phase of the moon?
```

## 🌍 Language Processing Tests
```
你好 (Hello in Chinese)
Bonjour (Hello in French)
Hola (Hello in Spanish)
こんにちは (Hello in Japanese)
```

## 📝 Notes
- All commands can be used in both text and voice mode (prefixed with "Jarvis")
- Some commands may require API keys to be configured in `config.yaml`
- Error handling tests should be handled gracefully by the system
- Complex queries demonstrate the system's ability to handle multiple tasks in a single request