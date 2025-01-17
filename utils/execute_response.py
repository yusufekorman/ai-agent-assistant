import json
import subprocess
import webbrowser
from typing import Dict, Any
import utils.tool_utils as tool_utils

async def execute_response(response_text: str, user_input: str, context: Dict[str, Any]) -> str:
    """Execute the AI response and return the final response text"""
    try:
        response_data = json.loads(response_text)
        
        # Extract components
        response = response_data.get("response", "")
        need = response_data.get("need", "")
        commands = response_data.get("commands", "")
        
        # Handle data requests
        if need:
            request_type, query = need.split(":", 1)
            
            if request_type == "weather_forecast":
                print("[DEBUG] Getting weather data")
                weather_data = await tool_utils.get_weather(query, context["secrets"].get("weather_api_key"))
                if weather_data:
                    response = weather_data
                    
            elif request_type == "wiki":
                print("[DEBUG] Searching Wikipedia")
                wiki_data = await tool_utils.search_wikipedia(query)
                if wiki_data:
                    response = wiki_data
                    
            elif request_type == "news":
                print("[DEBUG] Getting news data")
                news_data = await tool_utils.get_news(query, context["secrets"].get("news_api_key"))
                if news_data:
                    response = news_data
        
        # Handle system commands
        if commands:
            cmd_type, *cmd_args = commands.split(":", 1)
            
            if cmd_type == "cmd" and cmd_args:
                try:
                    result = subprocess.run(
                        cmd_args[0],
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0 and not result.stderr and result.stdout:
                        #response += f"\nCommand executed successfully with response"
                        # debug
                        # print(result.stdout)
                        pass
                    elif result.stderr:
                        response += f"\nCommand failed: {result.stderr}"
                except Exception as e:
                    response += f"\nError executing command: {str(e)}"
                    
            elif cmd_type == "ps" and cmd_args:
                try:
                    result = subprocess.run(
                        ["powershell", "-Command", cmd_args[0]],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0 and not result.stderr and result.stdout:
                        # response += f"\nPowerShell command executed successfully with response"
                        # debug
                        # print(result.stdout)
                        pass
                    elif result.stderr:
                        response += f"\nPowerShell command failed: {result.stderr}"
                except Exception as e:
                    response += f"\nError executing PowerShell command: {str(e)}"
                    
            elif cmd_type == "open_browser" and cmd_args:
                try:
                    webbrowser.open(cmd_args[0])
                    # debug
                    #response += f"\nOpened URL: {cmd_args[0]}"
                except Exception as e:
                    response += f"\nError opening URL: {str(e)}"
        
        return response
        
    except json.JSONDecodeError:
        return "Error: Invalid response format"
    except Exception as e:
        return f"Error executing response: {str(e)}"


export = {
    "execute_response": execute_response
}