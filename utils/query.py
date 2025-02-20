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
    LM Studio veya OpenAI API kullanarak sorgu gönderir
    
    Args:
        prompt: Ana sorgu metni
        answer: Önceki yanıt (opsiyonel)
        prompt2: İkinci sorgu metni (opsiyonel) 
        system_ip: Sistem IP adresi
        model: Kullanılacak model
        memory_vectors: Bellek vektörleri (kullanılmıyor)
        config: Yapılandırma ayarları

    Returns:
        Yanıt sözlüğü veya None (hata durumunda)
    """
    start_time = time.time()
    config_manager = get_config_manager()

    print(json.dumps(memory_vectors, indent=2))
    
    try:
        # Yapılandırma değerlerini al
        provider = config.get("llm_provider") or config_manager.get_config("llm_provider", "lm_studio")
        api_url = config.get("api_url") or config_manager.get_config("api_url")
        
        if not api_url:
            raise ValueError("API URL yapılandırılmamış")

        # OpenAI için kimlik doğrulama gerekiyor
        if provider == "openai":
            auth_token = config.get("auth_token") or config_manager.get_config("auth_token")
            if not auth_token:
                raise ValueError("OpenAI için kimlik doğrulama token'ı gerekli")
            openai.api_key = auth_token
        
        # Diğer yapılandırma değerlerini al
        temperature = float(config.get("temperature", config_manager.get_config("temperature", 0.7)))
        max_tokens = int(config.get("max_tokens", config_manager.get_config("max_tokens", 2000)))
        model_name = config_manager.get_config("model", model)

        # Mesajları OpenAI formatında oluştur
        messages: List[ChatCompletionMessageParam] = []


        messages.append({"role": "system", "content": system_prompt})
        
        # Context
        _datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context = f"""
My IP address is {system_ip} and the current time is {_datetime}.
{memory_vectors if memory_vectors else ""}
        """
        messages.append({"role": "user", "content": context})
            
        messages.append({"role": "user", "content": prompt})
        if answer:
            messages.append({"role": "assistant", "content": answer})
        if prompt2:
            messages.append({"role": "user", "content": prompt2})

        # OpenAI client yapılandırması
        client = openai.OpenAI(
            api_key=auth_token if provider == "openai" else "lm-studio",
            base_url=api_url
        )

        # Sorguyu gönder
        completion_args = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature
        }
        
        # max_tokens parametresini sadece OpenAI provider'ı olmadığında ekle
        if provider != "openai":
            completion_args["max_tokens"] = max_tokens
            response: ChatCompletion = client.chat.completions.create(**completion_args)
        else:
            response: ChatCompletion = client.chat.completions.create(**completion_args)

        # Yanıtı uygun formata dönüştür
        result = {
            "choices": [{
                "message": {
                    "content": response.choices[0].message.content
                }
            }]
        }

        print(json.dumps(result, indent=2))

        elapsed_time = round(time.time() - start_time, 2)
        logger.info(f"LLM yanıt süresi: {elapsed_time} saniye")
        
        return result

    except Exception as e:
        elapsed_time = round(time.time() - start_time, 2)
        logger.error(f"query_llm'de hata: {e}, süre: {elapsed_time} saniye")
        return None

# Export
export = {
    "query_llm": query_llm
}