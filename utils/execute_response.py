import json
import subprocess
import webbrowser
from typing import Dict, Any

import utils.tool_utils as tool_utils
from utils.query import query_lm_studio
from utils.index import outputCleaner

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
                        print(result.stdout)
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
                        print(result.stdout)
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