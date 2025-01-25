import json
import subprocess
import webbrowser
from typing import Dict, Any, List
import os

import utils.tool_utils as tool_utils
from utils.query import query_lm_studio
from utils.index import outputCleaner

# List of allowed commands
ALLOWED_COMMANDS = {
    'cmd': [
        # Windows Commands
        'taskmgr',      # Task Manager
        'calc',         # Calculator
        'notepad',      # Notepad
        'mspaint',      # Paint
        'ipconfig',     # Network configuration
        'dir',          # List directory
        'echo',         # Echo text
        'time',         # Show time
        'date',         # Show date
        'systeminfo',   # System information
        'tasklist',     # List processes
        'netstat',      # Network statistics
        'ping',         # Network ping
        'cls',          # Clear screen
        'type',         # Show file content
        'vol',          # Disk volume
        'chkdsk',       # Check disk
        'tree',         # Directory tree
        'where',        # File location

        # Linux/Unix Commands
        'ls',           # List directory
        'pwd',          # Print working directory
        'cat',          # Show file content
        'ps',           # Process status
        'df',           # Disk usage
        'du',           # Directory usage
        'date',         # Show date
        'time',         # Show time
        'uptime',       # System uptime
        'whoami',       # Current user
        'uname',        # System information
        'free',         # Memory usage
        'top',          # System monitor
        'clear',        # Clear screen
        'which',        # Command location
        'echo'          # Print text
    ],
    'ps': [
        # PowerShell Commands
        'Get-Date',
        'Get-Process',
        'Get-Service',
        'Get-ComputerInfo',
        'Test-Connection',
        'Get-NetAdapter',
        'Get-Volume',
        'Get-Disk',
        'Get-PSDrive',
        'Get-Command',
        'Get-History',
        'Get-Location',
        'Get-Host',
        'Get-Random',
        'Get-EventLog',
        'Get-LocalUser',
        'Get-Module'
    ]
}

# Allowed domains for safe URL checks
ALLOWED_DOMAINS = [
    # General
    'github.com',
    'gitlab.com',
    'bitbucket.org',
    'google.com',
    'youtube.com',
    'wikipedia.org',
    'stackoverflow.com',
    'stackexchange.com',

    # Microsoft
    'microsoft.com',
    'azure.com',
    'office.com',
    'visualstudio.com',
    'docs.microsoft.com',

    # Social Media
    'twitter.com',
    'x.com',
    'linkedin.com',
    'instagram.com',
    'facebook.com',

    # Education
    'coursera.org',
    'udemy.com',
    'edx.org',
    'pluralsight.com',
    'freecodecamp.org',
    'w3schools.com',
    'mozilla.org',
    'python.org',

    # Research & Documentation
    'arxiv.org',
    'researchgate.net',
    'scholar.google.com',
    'medium.com',
    'dev.to',

    # News & Information
    'reuters.com',
    'bbc.com',
    'cnn.com',
    'bloomberg.com',
    'techcrunch.com',
    'thehackernews.com',

    # Technical
    'docker.com',
    'kubernetes.io',
    'aws.amazon.com',
    'digitalocean.com',
    'heroku.com',
    'npmjs.com',
    'pypi.org',
    'dev.to'
]

def is_command_allowed(cmd_type: str, command: str) -> bool:
    """Check if the command is in the allowed list"""
    if cmd_type not in ALLOWED_COMMANDS:
        return False
        
    # Check if the command starts with an allowed command
    return any(command.strip().lower().startswith(cmd.lower()) 
              for cmd in ALLOWED_COMMANDS[cmd_type])

def is_url_safe(url: str) -> bool:
    """Check if the URL is safe"""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return any(domain.endswith(allowed_domain) for allowed_domain in ALLOWED_DOMAINS)
    except:
        return False

async def execute_response(response_text: str, user_input: str, context: Dict[str, Any], model='llama-3.2-3b-instruct', config={}):
    """Execute the AI response and return the final response text"""
    try:
        response_data = json.loads(response_text)
        
        # Extract components
        response = response_data.get("response", "")
        need = response_data.get("need", "")
        commands = response_data.get("commands", "")
        
        # Handle data requests
        if need:
            try:
                request_type, query = need.split(":", 1)
            except ValueError:
                return "Error: Invalid need format"
            need_response = None

            if request_type == "input":
                print("[DEBUG] Getting user input")
                need_response = "<user_input>" + input(query) + "</user_input>"
            elif request_type == "weather_forecast":
                print("[DEBUG] Getting weather data")
                need_response = await tool_utils.get_weather(query, context["secrets"].get("weather_api_key"))
                    
            elif request_type == "wiki":
                print("[DEBUG] Searching Wikipedia")
                need_response = await tool_utils.search_wikipedia(query)
                    
            elif request_type == "news":
                print("[DEBUG] Getting news data")
                need_response = await tool_utils.get_news(query, context["secrets"].get("news_api_key"))

            if need_response:

                second_response = await query_lm_studio(
                    prompt=user_input,
                    answer=response_text,
                    prompt2=need_response,
                    system_ip=context.get("system_ip", "unknown"),
                    config=config,
                    model=model
                )

                if second_response and "choices" in second_response:
                    response = second_response["choices"][0]["message"]["content"]
                    response = outputCleaner(response)
                    try:
                        # execute response again
                        response = await execute_response(response, user_input, context, model)
                    except json.JSONDecodeError:
                        # If not JSON, use the response as is
                        pass
        
        # Handle system commands
        if commands:
            cmd_type, *cmd_args = commands.split(":", 1)
            
            if cmd_type in ["cmd", "ps"] and cmd_args:
                if not is_command_allowed(cmd_type, cmd_args[0]):
                    return f"Command '{cmd_args[0]}' cannot be executed due to security restrictions."
                
                try:
                    if cmd_type == "cmd":
                        result = subprocess.run(
                            cmd_args[0],
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=5  # Limit timeout to 5 seconds
                        )
                    else:  # PowerShell
                        result = subprocess.run(
                            ["powershell", "-Command", cmd_args[0]],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                    
                    if result.returncode == 0:
                        print(f"Command output: {result.stdout}")
                    else:
                        response += f"\nCommand error: {result.stderr}"
                        
                except subprocess.TimeoutExpired:
                    response += "\nCommand timed out."
                except Exception as e:
                    response += f"\nCommand execution error: {str(e)}"
                    
            elif cmd_type == "open_browser" and cmd_args:
                url = cmd_args[0]
                if not is_url_safe(url):
                    return f"Access to '{url}' blocked due to security restrictions."
                try:
                    webbrowser.open(url)
                except Exception as e:
                    response += f"\nURL opening error: {str(e)}"
        
        return response
        
    except json.JSONDecodeError:
        return "Error: Invalid response format"
    except Exception as e:
        return f"Response processing error: {str(e)}"


export = {
    "execute_response": execute_response
}