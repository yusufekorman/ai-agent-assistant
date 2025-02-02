import aiohttp
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import asyncio
from functools import lru_cache
from aiohttp import ClientTimeout, ClientSession
from utils.logger import get_logger

logger = get_logger()

DAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
)

class LLMClient:
    def __init__(self, base_url: str, auth_token: Optional[str] = None, timeout_seconds: int = 30):
        """
        Initialize LLM Client
        
        Args:
            base_url: API endpoint URL
            auth_token: Authentication token (required for GPT and Deepseek)
            timeout_seconds: Request timeout duration (seconds)
        """
        self.base_url = base_url
        self.auth_token = auth_token
        self.timeout = ClientTimeout(total=timeout_seconds)
        self._session: Optional[ClientSession] = None
        self._lock = asyncio.Lock()
        self._closed = False

    async def _create_session(self) -> None:
        """Create a new session"""
        if self._session is None or self._session.closed:
            self._session = ClientSession(timeout=self.timeout)

    async def ensure_session(self) -> None:
        """Ensure session exists"""
        if self._closed:
            raise RuntimeError("Client is closed")
            
        if self._session is None or self._session.closed:
            async with self._lock:
                await self._create_session()

    async def close(self) -> None:
        """Close session"""
        self._closed = True
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> 'LLMClient':
        """Context manager entry"""
        await self.ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        await self.close()

    def get_headers(self) -> Dict[str, str]:
        """Get request headers based on provider"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def query(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send query to LLM provider
        
        Args:
            payload: Query payload
            
        Returns:
            API response or None (in case of error)
        """
        if self._closed:
            raise RuntimeError("Client is closed")

        max_retries = 3
        retry_count = 0
        headers = self.get_headers()

        while retry_count < max_retries:
            try:
                await self.ensure_session()
                if not self._session:
                    raise RuntimeError("Failed to create session")

                async with self._session.post(
                    self.base_url,
                    json=payload,
                    headers=headers
                ) as response:
                    response.raise_for_status()
                    return await response.json()

            except aiohttp.ClientError as e:
                logger.error(f"LLM request error (attempt {retry_count + 1}): {e}")
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(1)  # Wait before retrying
                    if self._session:
                        await self.close()  # Close current session
                else:
                    return None

            except Exception as e:
                logger.error(f"Unexpected error in LLM query: {e}")
                return None

        return None

@lru_cache(maxsize=100)
def _format_context(timestamp: str, day: str, system_ip: str, memory_str: str = "") -> str:
    """Cache context formatting"""
    return f"""Current Context:
    Time: {timestamp} ({day})
    System IP: {system_ip}
    {memory_str}"""

def _format_memory_vectors(vectors: List[str]) -> str:
    """Format memory vectors"""
    if not vectors:
        return ""
    return "Memory Vector:\n" + "\n".join(f"- {vector}" for vector in vectors)

async def query_llm(
    prompt: str,
    answer: Optional[str] = None,
    prompt2: Optional[str] = None,
    system_ip: str = "",
    model: str = "llama-3.2-3b-instruct",
    memory_vectors: List[str] = [],
    config: Dict[str, Any] = {}
) -> Optional[Dict[str, Any]]:
    """
    Send query to configured LLM provider
    
    Args:
        prompt: Main query text
        answer: Previous response (optional)
        prompt2: Second query text (optional)
        system_ip: System IP address
        model: Model to use
        memory_vectors: Memory vectors
        config: Configuration settings

    Returns:
        Response dictionary or None (in case of error)
    """
    start_time = time.time()

    from utils.config_manager import get_config_manager
    config_manager = get_config_manager()
    
    try:
        # Get configuration values
        provider = config.get("llm_provider") or config_manager.get_config("llm_provider", "lm_studio")
        url = config.get("api_url") or config_manager.get_config("api_url")
        auth_token = None

        if not url:
            raise ValueError("API URL not configured")

        if provider in ["gpt", "deepseek"]:
            auth_token = config.get("auth_token") or config_manager.get_config("auth_token")
            if not auth_token:
                raise ValueError(f"Authentication token required for {provider}")

        # Get other configuration values
        temperature = config.get("temperature") or config_manager.get_config("temperature")
        max_tokens = config.get("max_tokens") or config_manager.get_config("max_tokens")
        timeout = config_manager.get_config("timeout", 30)
        model_name = config_manager.get_config("model", model)

        # Create context
        dt = datetime.now()
        memory_str = _format_memory_vectors(memory_vectors)
        context_prompt = _format_context(
            dt.strftime("%Y-%m-%dT%H:%M:%S"),
            DAYS[dt.weekday()],
            system_ip,
            memory_str
        )

        # Create messages
        messages = [
            {"role": "user", "content": context_prompt},
            {"role": "user", "content": prompt}
        ]

        if answer:
            messages.append({"role": "assistant", "content": answer})
        if prompt2:
            messages.append({"role": "user", "content": prompt2})

        # Create payload
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "stream": False
        }

        # Send query
        async with LLMClient(url, auth_token, timeout_seconds=timeout) as client:
            response = await client.query(payload)

        elapsed_time = round(time.time() - start_time, 2)
        logger.info(f"LLM response time: {elapsed_time} seconds")

        return response

    except Exception as e:
        elapsed_time = round(time.time() - start_time, 2)
        logger.error(f"Error in query_llm: {e}, took {elapsed_time} seconds")
        return None

# Export
export = {
    "query_llm": query_llm  # Renamed from query_lm_studio
}