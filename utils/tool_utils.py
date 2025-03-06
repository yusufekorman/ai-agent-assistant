import aiohttp
import json
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Union
import datetime
import os
from functools import lru_cache
from aiohttp import ClientTimeout
from utils.logger import get_logger

logger = get_logger()

# Constants
DEFAULT_TIMEOUT = ClientTimeout(total=5)
WEATHER_UNITS = "metric"
NEWS_PAGE_SIZE = 5
WIKI_SEARCH_LIMIT = 5

class APIError(Exception):
    """Custom exception for API errors"""
    pass

async def make_api_request(
    session: aiohttp.ClientSession,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    General API request function
    
    Args:
        session: aiohttp session
        url: API endpoint URL
        params: Query parameters
        headers: HTTP headers
    
    Returns:
        API response
    
    Raises:
        APIError: When API request fails
    """
    try:
        async with session.get(url, params=params, headers=headers, timeout=DEFAULT_TIMEOUT) as response:
            if response.status != 200:
                raise APIError(f"API request failed with status {response.status}")
            return await response.json()
    except Exception as e:
        logger.error(f"API request error for {url}: {str(e)}")
        raise APIError(str(e))

@lru_cache(maxsize=100)
def clean_html(text: str) -> str:
    """Clean HTML tags and special characters"""
    text = re.sub(r'<[^>]+>', '', text)
    replacements = {
        '&quot;': '"',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&apos;': "'"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

async def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia
    
    Args:
        query: Search term
    
    Returns:
        Search results in JSON format
    """
    try:
        async with aiohttp.ClientSession() as session:
            wiki_params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "utf8": 1,
                "srlimit": WIKI_SEARCH_LIMIT
            }
            
            data = await make_api_request(
                session,
                "https://en.wikipedia.org/w/api.php",
                params=wiki_params
            )
            
            results = []
            if 'query' in data and 'search' in data['query']:
                for article in data['query']['search']:
                    results.append({
                        'title': article['title'],
                        'text': clean_html(article['snippet'])
                    })
            
            return json.dumps({
                'query': query,
                'results': results,
                'total': len(results)
            })
            
    except Exception as e:
        logger.error(f"Wikipedia search error: {e}")
        return json.dumps({
            'query': query,
            'results': [],
            'total': 0,
            'error': str(e)
        })

async def parse_feed_item(item: ET.Element) -> Optional[Dict[str, str]]:
    """Parse RSS feed item"""
    try:
        title = item.find('title')
        desc = item.find('description')
        link = item.find('link')
        
        if not (title is not None and title.text) and not (desc is not None and desc.text):
            return None
            
        return {
            'title': title.text if title is not None and title.text else '',
            'text': desc.text if desc is not None and desc.text else '',
            'url': link.text if link is not None and link.text else ''
        }
    except Exception as e:
        logger.error(f"Feed item parsing error: {e}")
        return None

async def fetch_feed(session: aiohttp.ClientSession, feed_url: str) -> List[Dict[str, str]]:
    """Fetch and parse RSS feed"""
    try:
        async with session.get(feed_url, timeout=DEFAULT_TIMEOUT) as response:
            content = await response.text()
            root = ET.fromstring(content)
            
            results = []
            items = root.findall('.//item')
            
            for item in items[:5]:
                if parsed_item := await parse_feed_item(item):
                    results.append(parsed_item)
                    
            return results
    except Exception as e:
        logger.error(f"Feed fetch error for {feed_url}: {e}")
        return []

async def get_weather(city: str, api_key: Optional[str]) -> str:
    """
    Get weather information
    
    Args:
        city: City name
        api_key: OpenWeather API key
    
    Returns:
        Weather information in JSON format
    """
    if not api_key:
        return "Weather API key not configured"
        
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                "q": city,
                "appid": api_key,
                "units": WEATHER_UNITS
            }
            
            data = await make_api_request(
                session,
                "https://api.openweathermap.org/data/2.5/forecast",
                params=params
            )
            
            if not data.get("list"):
                return "No weather data found"

            today = datetime.datetime.now()
            tomorrow = today + datetime.timedelta(days=1)
            
            weather_data = []
            for forecast in data["list"]:
                forecast_date = datetime.datetime.strptime(
                    forecast["dt_txt"],
                    "%Y-%m-%d %H:%M:%S"
                )
                
                if forecast_date.date() in (today.date(), tomorrow.date()): # Today and tomorrow
                    weather_data.append({
                        "datetime": forecast["dt_txt"],
                        "temperature": forecast["main"]["temp"],
                        "description": forecast["weather"][0]["description"]
                    })
                    
            return json.dumps(weather_data)
            
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return f"Error getting weather data: {str(e)}"

async def get_news(query: str, api_key: Optional[str]) -> str:
    """
    Get news data
    
    Args:
        query: Search term
        api_key: NewsAPI key
    
    Returns:
        News data in JSON format
    """
    if not api_key:
        return "News API key not configured"
        
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                "q": query,
                "apiKey": api_key,
                "pageSize": NEWS_PAGE_SIZE
            }
            
            data = await make_api_request(
                session,
                "https://newsapi.org/v2/everything",
                params=params
            )
            
            return json.dumps(data.get("articles", []))
            
    except Exception as e:
        logger.error(f"News API error: {e}")
        return f"Error getting news data: {str(e)}"

# Export
export = {
    'search_wikipedia': search_wikipedia,
    'fetch_feed': fetch_feed,
    'get_weather': get_weather,
    'get_news': get_news
}