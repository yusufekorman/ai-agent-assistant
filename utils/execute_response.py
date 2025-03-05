import json
import webbrowser
from typing import Dict, Optional, Any, Tuple, List
import asyncio
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from utils.logger import get_logger
import utils.tool_utils as tool_utils

logger = get_logger()

# Define safe command and domain lists
ALLOWED_COMMANDS = {
    'cmd': tuple([
        'taskmgr', 'calc', 'notepad', 'mspaint', 'ipconfig', 'dir',
        'echo', 'time', 'date', 'systeminfo', 'tasklist', 'netstat',
        'ping', 'cls', 'type', 'vol', 'chkdsk', 'tree', 'where',
        'ls', 'pwd', 'cat', 'ps', 'df', 'du', 'uptime', 'whoami',
        'uname', 'free', 'top', 'clear', 'which', 'code'
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
    'google.com', 'youtube.com', 'wikipedia.org', 'github.com',
    'stackoverflow.com', 'linkedin.com', 'twitter.com', 'facebook.com',
    'instagram.com', 'reddit.com', 'pinterest.com', 'x.com', 'whatsapp.com', 
    'web.whatsapp.com', 'discord.com', 'twitch.tv', 'amazon.com', 'ebay.com', 
    'aliexpress.com', 'microsoft.com', 'apple.com', 'yahoo.com', 'bing.com', 
    'duckduckgo.com', 'meet.google.com', 'zoom.us', 'slack.com', 'messenger.com'
])

@lru_cache(maxsize=1000)
def is_command_allowed(cmd_type: str, command: str) -> bool:
    """Check if command is in allowed list"""
    if cmd_type not in ALLOWED_COMMANDS:
        return False
    return any(command.strip().lower().startswith(cmd.lower()) 
              for cmd in ALLOWED_COMMANDS[cmd_type])

@lru_cache(maxsize=1000)
def is_domain_allowed(url: str) -> bool:
    """Check if domain is in allowed list"""
    import re
    domain = re.compile(r"https?://(?:www\.)?([a-zA-Z0-9.-]+)").search(url)
    return domain and domain.group(1) in ALLOWED_DOMAINS

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

async def handle_tool_call(tool_call: Any, context: Dict[str, Any], user_input: str) -> Tuple[str, str]:
    """
    Handle tool/function calls from OpenAI API
    Returns: Tuple of (tool_name, result)
    """
    try:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "get_weather":
            result = await tool_utils.get_weather(
                arguments["city"],
                context["secrets"].get("weather_api_key")
            )
            return function_name, result

        elif function_name == "search_wikipedia":
            result = await tool_utils.search_wikipedia(arguments["query"])
            return function_name, result

        elif function_name == "get_news":
            result = await tool_utils.get_news(
                arguments["query"],
                context["secrets"].get("news_api_key")
            )
            return function_name, result

        elif function_name == "execute_command":
            if not is_command_allowed(arguments["command_type"], arguments["command"]):
                return function_name, f"Command '{arguments['command']}' cannot be executed due to security restrictions."

            success, output = await (
                execute_shell_command(arguments["command"]) 
                if arguments["command_type"] == "cmd"
                else execute_powershell_command(arguments["command"])
            )

            if success:
                logger.info(f"Command executed successfully: {arguments['command']}")
                return function_name, output
            else:
                logger.error(f"Command execution failed: {output}")
                return function_name, f"Command error: {output}"

        elif function_name == "open_browser":
            if not is_domain_allowed(arguments["url"]):
                return function_name, f"URL '{arguments['url']}' cannot be opened due to security restrictions."

            try:
                with ThreadPoolExecutor() as executor:
                    await asyncio.get_event_loop().run_in_executor(
                        executor,
                        webbrowser.open,
                        arguments["url"]
                    )
                return function_name, "Browser opened successfully"
            except Exception as e:
                logger.error(f"Browser command error: {e}")
                return function_name, f"URL opening error: {str(e)}"

        return function_name, f"Unknown tool: {function_name}"

    except Exception as e:
        logger.error(f"Error handling tool call: {e}")
        return "unknown", f"Tool execution error: {str(e)}"

async def execute_response(
    llm_response: Any,
    user_input: str,
    context: Dict[str, Any],
    model: Optional[str] = None,
    config: Dict[str, Any] = {},
    dynamic_tools: Optional[List[str]] = None
) -> str:
    """Execute AI response with OpenAI function calling support"""
    from main import process_tool_result  # Import here to avoid circular dependency
    
    try:
        # Check for tool calls
        if hasattr(llm_response.choices[0].message, 'tool_calls') and llm_response.choices[0].message.tool_calls:
            for tool_call in llm_response.choices[0].message.tool_calls:
                # Get tool result
                tool_name, result = await handle_tool_call(tool_call, context, user_input)
                
                # If this is a dynamic tool, process the result through AI
                if dynamic_tools and tool_name in dynamic_tools:
                    return await process_tool_result(tool_name, result, user_input)
                
                return result

        # If we have content, return it
        if hasattr(llm_response.choices[0].message, 'content') and llm_response.choices[0].message.content:
            return llm_response.choices[0].message.content

        # Default empty response
        return ""

    except Exception as e:
        logger.error(f"Response processing error: {e}")
        return f"Response processing error: {str(e)}"

# Export
export = {
    "execute_response": execute_response,
    "handle_tool_call": handle_tool_call
}