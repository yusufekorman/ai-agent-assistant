import json
import subprocess
import webbrowser
import aiohttp
from typing import Dict, Any, Optional

async def execute_response(response_text: str, user_input: str, memory_manager, context: Dict[str, Any]) -> str:
    """Execute the AI response and return the final response text"""
    try:
        response_data = json.loads(response_text)
        
        # Extract components
        response = response_data.get("response", "")
        need = response_data.get("need", "")
        commands = response_data.get("commands", "")
        memory = response_data.get("memory", "")
        
        # Handle memory storage
        if memory:
            await memory_manager.save_memory(memory)
        
        # Handle data requests
        if need:
            request_type, query = need.split(":", 1)
            
            if request_type == "weather_forecast":
                weather_data = await get_weather(query, context["secrets"].get("weather_api_key"))
                if weather_data:
                    response = weather_data
                    
            elif request_type == "stock_price":
                stock_data = await get_stock_price(query, context["secrets"].get("alpha_vantage_key"))
                if stock_data:
                    response = stock_data
                    
            elif request_type == "wiki":
                wiki_data = await get_wiki_summary(query)
                if wiki_data:
                    response = wiki_data
                    
            elif request_type == "news":
                news_data = await get_news(query, context["secrets"].get("news_api_key"))
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
                    if result.returncode == 0:
                        response += f"\nCommand executed successfully: {result.stdout}"
                    else:
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
                    if result.returncode == 0:
                        response += f"\nPowerShell command executed successfully: {result.stdout}"
                    else:
                        response += f"\nPowerShell command failed: {result.stderr}"
                except Exception as e:
                    response += f"\nError executing PowerShell command: {str(e)}"
                    
            elif cmd_type == "start" and cmd_args:
                try:
                    webbrowser.open(cmd_args[0])
                    response += f"\nOpened URL: {cmd_args[0]}"
                except Exception as e:
                    response += f"\nError opening URL: {str(e)}"
        
        return response
        
    except json.JSONDecodeError:
        return "Error: Invalid response format"
    except Exception as e:
        return f"Error executing response: {str(e)}"

async def get_weather(city: str, api_key: Optional[str]) -> str:
    """Get weather data for a city"""
    if not api_key:
        return "Weather API key not configured"
        
    try:
        async with aiohttp.ClientSession() as session:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = data["main"]["temp"]
                    desc = data["weather"][0]["description"]
                    return f"It's currently {temp}°C with {desc} in {city}"
                else:
                    return "Could not fetch weather data"
    except Exception as e:
        return f"Error getting weather data: {str(e)}"

async def get_stock_price(symbol: str, api_key: Optional[str]) -> str:
    """Get stock price data"""
    if not api_key:
        return "Alpha Vantage API key not configured"
        
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "Global Quote" in data:
                        price = data["Global Quote"]["05. price"]
                        return f"{symbol} is currently trading at ${price}"
                    else:
                        return "Could not fetch stock data"
                else:
                    return "Could not fetch stock data"
    except Exception as e:
        return f"Error getting stock data: {str(e)}"

async def get_wiki_summary(query: str) -> str:
    """Get Wikipedia summary"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("extract", "No summary available")
                else:
                    return "Could not fetch Wikipedia data"
    except Exception as e:
        return f"Error getting Wikipedia data: {str(e)}"

async def get_news(query: str, api_key: Optional[str]) -> str:
    """Get news data"""
    if not api_key:
        return "News API key not configured"
        
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}&pageSize=5"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["articles"]:
                        articles = data["articles"][:3]
                        news_text = "Here are the latest news:\n"
                        for i, article in enumerate(articles, 1):
                            news_text += f"{i}. {article['title']}\n"
                        return news_text
                    else:
                        return "No news found"
                else:
                    return "Could not fetch news data"
    except Exception as e:
        return f"Error getting news data: {str(e)}"

export = {
    "execute_response": execute_response
}