import json
import subprocess
import webbrowser
from typing import Dict, List, Optional, Any, Tuple, Coroutine
import os
import asyncio
from urllib.parse import urlparse
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from utils.logger import get_logger
import utils.tool_utils as tool_utils
from utils.query import query_llm
from utils.index import outputCleaner

logger = get_logger()

# Define safe command and domain lists as tuples (immutable and faster)
ALLOWED_COMMANDS = {
    'cmd': tuple([
        'taskmgr', 'calc', 'notepad', 'mspaint', 'ipconfig', 'dir',
        'echo', 'time', 'date', 'systeminfo', 'tasklist', 'netstat',
        'ping', 'cls', 'type', 'vol', 'chkdsk', 'tree', 'where',
        'ls', 'pwd', 'cat', 'ps', 'df', 'du', 'uptime', 'whoami',
        'uname', 'free', 'top', 'clear', 'which'
    ]),
    'ps': tuple([
        'Get-Date', 'Get-Process', 'Get-Service', 'Get-ComputerInfo',
        'Test-Connection', 'Get-NetAdapter', 'Get-Volume', 'Get-Disk',
        'Get-PSDrive', 'Get-Command', 'Get-History', 'Get-Location',
        'Get-Host', 'Get-Random', 'Get-EventLog', 'Get-LocalUser',
        'Get-Module'
    ])
}

ALLOWED_DOMAINS = tuple([
    # List of safe domains
    'github.com', 'gitlab.com', 'bitbucket.org', 'google.com',
    'youtube.com', 'wikipedia.org', 'stackoverflow.com', 'microsoft.com',
    'azure.com', 'office.com', 'visualstudio.com', 'python.org',
    'youtube.com', 'facebook.com', 'twitter.com', 'linkedin.com',
    'x.com'
])

@lru_cache(maxsize=1000)
def is_command_allowed(cmd_type: str, command: str) -> bool:
    """Check if command is in allowed list"""
    if cmd_type not in ALLOWED_COMMANDS:
        return False
    return any(command.strip().lower().startswith(cmd.lower()) 
              for cmd in ALLOWED_COMMANDS[cmd_type])

@lru_cache(maxsize=1000)
def is_url_safe(url: str) -> bool:
    """Check if URL is safe"""
    try:
        domain = urlparse(url).netloc
        return any(domain.endswith(allowed_domain) for allowed_domain in ALLOWED_DOMAINS)
    except Exception as e:
        logger.error(f"URL parsing error: {e}")
        return False

async def execute_shell_command(command: str, timeout: int = 5) -> Tuple[bool, str]:
    """Execute shell command asynchronously"""
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            if process.returncode == 0:
                return True, stdout.decode()
            return False, stderr.decode()
        except asyncio.TimeoutError:
            return False, "Command execution timed out"

    except Exception as e:
        logger.error(f"Shell command execution error: {e}")
        return False, str(e)

async def execute_powershell_command(command: str, timeout: int = 5) -> Tuple[bool, str]:
    """Execute PowerShell command asynchronously"""
    try:
        process = await asyncio.create_subprocess_exec(
            "powershell",
            "-Command",
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            if process.returncode == 0:
                return True, stdout.decode()
            return False, stderr.decode()
        except asyncio.TimeoutError:
            return False, "PowerShell command execution timed out"

    except Exception as e:
        logger.error(f"PowerShell command execution error: {e}")
        return False, str(e)

async def handle_system_command(cmd_type: str, command: str) -> Optional[str]:
    """Handle system command"""
    if not is_command_allowed(cmd_type, command):
        return f"Command '{command}' cannot be executed due to security restrictions."

    success, output = await (
        execute_shell_command(command) if cmd_type == "cmd"
        else execute_powershell_command(command)
    )

    if success:
        logger.info(f"Command executed successfully: {command}")
        return output
    else:
        logger.error(f"Command execution failed: {output}")
        return f"Command error: {output}"

async def handle_browser_command(url: str) -> Optional[str]:
    """Handle browser command"""
    if not is_url_safe(url):
        return f"Access to '{url}' blocked due to security restrictions."

    try:
        # Run browser open operation in thread pool
        with ThreadPoolExecutor() as executor:
            await asyncio.get_event_loop().run_in_executor(
                executor,
                webbrowser.open,
                url
            )
        return None
    except Exception as e:
        logger.error(f"Browser command error: {e}")
        return f"URL opening error: {str(e)}"

async def handle_need_request(
    need_type: str,
    query: str,
    context: Dict[str, Any]
) -> Optional[str]:
    """Handle need requests asynchronously"""
    try:
        if need_type == "input":
            # Run input operation in thread pool
            with ThreadPoolExecutor() as executor:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    input,
                    query
                )
            return f"<user_input>{user_input}</user_input>"

        # Run API calls in parallel
        if need_type == "weather_forecast":
            return await tool_utils.get_weather(
                query,
                context["secrets"].get("weather_api_key")
            )
        elif need_type == "wiki":
            return await tool_utils.search_wikipedia(query)
        elif need_type == "news":
            return await tool_utils.get_news(
                query,
                context["secrets"].get("news_api_key")
            )

        return None

    except Exception as e:
        logger.error(f"Error handling need request: {e}")
        return None

async def process_second_response(
    response_text: str,
    user_input: str,
    context: Dict[str, Any],
    model: Optional[str],
    config: Dict[str, Any]
) -> str:
    from utils.config_manager import get_config_manager
    config_manager = get_config_manager()

    # Use provided model or get from config
    model_name = model if model else config_manager.get_config("model", "llama-3.2-3b-instruct")
    
    # Update API configuration
    current_config = config.copy()
    current_config.update({
        key: config_manager.get_config(key)
        for key in ["temperature", "max_tokens", "timeout"]
        if config_manager.get_config(key) is not None
    })
    """Process second response"""
    try:
        second_response = await query_llm(
            prompt=user_input,
            answer=response_text,
            system_ip=context.get("system_ip", "unknown"),
            config=current_config,
            model=str(model_name)  # Convert to str for type safety
        )

        if second_response and "choices" in second_response:
            response = second_response["choices"][0]["message"]["content"]
            response = outputCleaner(response)
            try:
                response = await execute_response(
                    response,
                    user_input,
                    context,
                    model
                )
            except json.JSONDecodeError:
                pass
            return response

    except Exception as e:
        logger.error(f"Error processing second response: {e}")

    return response_text

async def execute_response(
    response_text: str,
    user_input: str,
    context: Dict[str, Any],
    model: Optional[str] = None,
    config: Dict[str, Any] = {}
) -> str:
    from utils.config_manager import get_config_manager
    config_manager = get_config_manager()

    # Get configuration values
    model = model or config_manager.get_config("model")
    
    # Add API keys to context
    if "secrets" not in context:
        context["secrets"] = {}
    context["secrets"].update({
        "weather_api_key": config.get("weather_api_key") or config_manager.get_secret("weather_api_key"),
        "news_api_key": config.get("news_api_key") or config_manager.get_secret("news_api_key")
    })
    """
    Execute AI response asynchronously
    
    Args:
        response_text: AI response
        user_input: User input
        context: Context information
        model: Model to use
        config: Configuration settings
    
    Returns:
        Processed response text
    """
    try:
        # Parse response
        response_data = json.loads(response_text)
        response = response_data.get("response", "")
        need = response_data.get("need", "")
        commands = response_data.get("commands", "")

        # Process need requests
        if need:
            try:
                need_type, query = need.split(":", 1)
                need_response = await handle_need_request(need_type, query, context)

                if need_response:
                    response = await process_second_response(
                        response_text,
                        user_input,
                        context,
                        model,
                        config
                    )

            except ValueError:
                logger.error("Invalid need format")
                return "Error: Invalid need format"

        # Process system commands
        if commands:
            parts = commands.split(":", 1)
            if len(parts) != 2:
                return "Error: Invalid command format"

            cmd_type, command = parts

            if cmd_type in ["cmd", "ps"]:
                output = await handle_system_command(cmd_type, command)
                if output:
                    response += f"\n{output}"

            elif cmd_type == "open_browser":
                output = await handle_browser_command(command)
                if output:
                    response += f"\n{output}"

        return response

    except json.JSONDecodeError:
        logger.error("Invalid response format")
        return "Error: Invalid response format"
    except Exception as e:
        logger.error(f"Response processing error: {e}")
        return f"Response processing error: {str(e)}"

# Export
export = {
    "execute_response": execute_response,
    "handle_system_command": handle_system_command,
    "handle_browser_command": handle_browser_command,
    "handle_need_request": handle_need_request
}