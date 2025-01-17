import aiohttp
import json
import re
import xml.etree.ElementTree as ET
from typing import Optional

async def search_wikipedia(query):
    try:

        results = []
        async with aiohttp.ClientSession() as session:
            wiki_url = f"https://en.wikipedia.org/w/api.php"
            wiki_params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "utf8": 1,
                "srlimit": 5
            }
            
            async with session.get(wiki_url, params=wiki_params) as wiki_response:
                wiki_data = await wiki_response.json()
                
                if 'query' in wiki_data and 'search' in wiki_data['query']:
                    for article in wiki_data['query']['search']:
                        text = re.sub(r'<[^>]+>', '', article['snippet'])
                        results.append({
                            'title': article['title'],
                            'text': text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>'),
                            'url': f"https://en.wikipedia.org/wiki/{article['title'].replace(' ', '_')}"
                        })

        response_data = json.dumps({
            'query': query,
            'results': results,
            'total': len(results)
        })
        
        return response_data
        
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        return json.dumps({
            'query': query,
            'results': [],
            'total': 0,
            'error': str(e)
        })

async def fetch_feed(session, feed_url):
    try:
        async with session.get(feed_url, timeout=5) as response:
            content = await response.text()
            root = ET.fromstring(content)
            
            results = []
            items = root.findall('.//item')
            for item in items[:5]:
                title_elem = item.find('title')
                desc_elem = item.find('description')
                link_elem = item.find('link')
                
                title = title_elem.text if title_elem is not None and title_elem.text is not None else ''
                desc = desc_elem.text if desc_elem is not None and desc_elem.text is not None else ''
                link = link_elem.text if link_elem is not None and link_elem.text is not None else ''
                
                if not title and not desc:
                    continue
                    
                results.append({
                    'title': title,
                    'text': desc,
                    'url': link
                })
            return results
    except Exception as feed_error:
        print(f"Error fetching feed {feed_url}: {feed_error}")
        return []

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
    'search_wikipedia': search_wikipedia,
    'fetch_feed': fetch_feed,
    'get_weather': get_weather,
    'get_news': get_news
}