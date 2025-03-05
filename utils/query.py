from typing import Dict, List, Optional, Any
import time
from datetime import date, datetime
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import openai
from utils.logger import get_logger
from utils.config_manager import get_config_manager
import json

logger = get_logger()

# Define available tools/functions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather forecast for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city to get weather for"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Search Wikipedia for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Get news articles about a topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The news topic to search for"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a system command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command_type": {
                        "type": "string",
                        "enum": ["cmd", "ps"],
                        "description": "Type of command (cmd or ps)"
                    },
                    "command": {
                        "type": "string",
                        "description": "The command to execute"
                    }
                },
                "required": ["command_type", "command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_browser",
            "description": "Open a URL in the default browser",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to open"
                    }
                },
                "required": ["url"]
            }
        }
    }
]

async def query_llm(
    prompt: str,
    answer: Optional[str] = None,
    prompt2: Optional[str] = None,
    system_ip: str = "",
    model: str = "gpt-3.5-turbo",
    memory_vectors: List[str] = [],
    config: Dict[str, Any] = {},
    system_prompt: str = ""
) -> Optional[Dict[str, Any]]:
    """
    Sends a query using OpenAI API with tool/function calling support
    """
    start_time = time.time()
    config_manager = get_config_manager()

    try:
        # Get configuration values
        provider = config.get("llm_provider") or config_manager.get_config("llm_provider", "openai")
        api_url = config.get("api_url") or config_manager.get_config("api_url")
        
        if not api_url:
            raise ValueError("API URL not configured")

        # Authentication for OpenAI
        auth_token = config.get("auth_token") or config_manager.get_config("auth_token")
        if not auth_token:
            raise ValueError("Authentication token required for OpenAI")
        openai.api_key = auth_token
        
        # Get other configuration values
        temperature = float(config.get("temperature", config_manager.get_config("temperature", 0.7)))
        model_name = config_manager.get_config("model", model)

        # Create messages
        messages: List[ChatCompletionMessageParam] = []
        messages.append({"role": "system", "content": system_prompt})
        
        # Add context
        _datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        memory_context = "".join([f"<memory>{m}</memory>" for m in memory_vectors])
        context = f"My IP address is {system_ip} and the current time is {_datetime}.\n<memories>\n{memory_context}\n</memories>"
        messages.append({"role": "user", "content": context})
            
        messages.append({"role": "user", "content": prompt})
        if answer:
            messages.append({"role": "assistant", "content": answer})
        if prompt2:
            messages.append({"role": "user", "content": prompt2})

        # OpenAI client configuration
        client = openai.OpenAI(
            api_key=auth_token,
            base_url=api_url
        )

        # Send query with tools/functions
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            tools=TOOLS,
            tool_choice="auto"
        )

        elapsed_time = round(time.time() - start_time, 2)
        logger.info(f"LLM response time: {elapsed_time} seconds")
        
        return response

    except Exception as e:
        elapsed_time = round(time.time() - start_time, 2)
        logger.error(f"Error in query_llm: {e}, time: {elapsed_time} seconds")
        return None

# Export
export = {
    "query_llm": query_llm
}