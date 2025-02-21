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

async def query_llm(
    prompt: str,
    answer: Optional[str] = None,
    prompt2: Optional[str] = None,
    system_ip: str = "",
    model: str = "llama-3.2-3b-instruct",
    memory_vectors: List[str] = [],
    config: Dict[str, Any] = {},
    system_prompt: str = ""
) -> Optional[Dict[str, Any]]:
    """
    Sends a query using LM Studio or OpenAI API
    
    Args:
        prompt: Main query text
        answer: Previous response (optional)
        prompt2: Second query text (optional)
        system_ip: System IP address
        model: Model to be used
        memory_vectors: Memory vectors (not used)
        config: Configuration settings

    Returns:
        Response dictionary or None (in case of error)
    """
    start_time = time.time()
    config_manager = get_config_manager()

    print(json.dumps(memory_vectors, indent=2))
    
    try:
        # Get configuration values
        provider = config.get("llm_provider") or config_manager.get_config("llm_provider", "lm_studio")
        api_url = config.get("api_url") or config_manager.get_config("api_url")
        
        if not api_url:
            raise ValueError("API URL not configured")

        # Authentication required for OpenAI
        if provider == "openai":
            auth_token = config.get("auth_token") or config_manager.get_config("auth_token")
            if not auth_token:
                raise ValueError("Authentication token required for OpenAI")
            openai.api_key = auth_token
        
        # Get other configuration values
        temperature = float(config.get("temperature", config_manager.get_config("temperature", 0.7)))
        max_tokens = int(config.get("max_tokens", config_manager.get_config("max_tokens", 2000)))
        model_name = config_manager.get_config("model", model)

        # Create messages in OpenAI format
        messages: List[ChatCompletionMessageParam] = []


        messages.append({"role": "system", "content": system_prompt})
        
        # Context
        _datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        memory_context = "".join([f"<memory>{m}</memory>" for m in memory_vectors])

        context = f"""
My IP address is {system_ip} and the current time is {_datetime}.
<memories>
{memory_context}
</memories>
        """
        messages.append({"role": "user", "content": context})
            
        messages.append({"role": "user", "content": prompt})
        if answer:
            messages.append({"role": "assistant", "content": answer})
        if prompt2:
            messages.append({"role": "user", "content": prompt2})

        # OpenAI client configuration
        client = openai.OpenAI(
            api_key=auth_token if provider == "openai" else "lm-studio",
            base_url=api_url
        )

        # Send query
        completion_args = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature
        }
        
        # Add max_tokens parameter only when provider is not OpenAI
        if provider != "openai":
            completion_args["max_tokens"] = max_tokens
            response: ChatCompletion = client.chat.completions.create(**completion_args)
        else:
            response: ChatCompletion = client.chat.completions.create(**completion_args)

        # Convert response to appropriate format
        result = {
            "choices": [{
                "message": {
                    "content": response.choices[0].message.content
                }
            }]
        }

        print(json.dumps(result, indent=2))

        elapsed_time = round(time.time() - start_time, 2)
        logger.info(f"LLM response time: {elapsed_time} seconds")
        
        return result

    except Exception as e:
        elapsed_time = round(time.time() - start_time, 2)
        logger.error(f"Error in query_llm: {e}, time: {elapsed_time} seconds")
        return None

# Export
export = {
    "query_llm": query_llm
}