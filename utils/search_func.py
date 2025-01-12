import aiohttp
import asyncio
import json
import re
import xml.etree.ElementTree as ET


async def search_web(query):
    try:
        results = []
        async with aiohttp.ClientSession() as session:
            # Wikipedia araması
            wiki_url = f"https://en.wikipedia.org/w/api.php"
            wiki_params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "utf8": 1,
                "srlimit": 3
            }
            
            async with session.get(wiki_url, params=wiki_params) as wiki_response:
                wiki_data = await wiki_response.json()
                
                if 'query' in wiki_data and 'search' in wiki_data['query']:
                    for article in wiki_data['query']['search']:
                        text = re.sub(r'<[^>]+>', '', article['snippet'])
                        results.append({
                            'source': 'Wikipedia',
                            'type': 'article',
                            'title': article['title'],
                            'text': text,
                            'url': f"https://en.wikipedia.org/wiki/{article['title'].replace(' ', '_')}"
                        })
            
            # DuckDuckGo araması
            ddg_url = f"https://api.duckduckgo.com/?q={query}&format=json"
            async with session.get(ddg_url) as ddg_response:
                ddg_data = await ddg_response.json()
                
                if ddg_data.get('Abstract'):
                    results.append({
                        'source': 'DuckDuckGo',
                        'type': 'summary',
                        'text': ddg_data['Abstract'],
                        'url': ddg_data.get('AbstractURL', '')
                    })

        response_data = json.dumps({
            'query': query,
            'results': results,
            'total': len(results)
        })
        
        return response_data
        
    except Exception as e:
        print(f"Search error: {e}")
        return json.dumps({
            'query': query,
            'results': [],
            'total': 0,
            'error': str(e)
        })

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
                            'text': text,
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

async def search_news(query):
    try:

        results = []
        rss_feeds = [
            "http://rss.cnn.com/rss/edition.rss",
            "https://news.google.com/rss"
        ]
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for feed_url in rss_feeds:
                tasks.append(fetch_feed(session, feed_url, query))
            
            feed_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in feed_results:
                if isinstance(result, list):
                    results.extend(result)

        response_data = json.dumps({
            'query': query,
            'results': results,
            'total': len(results)
        })
        return response_data
        
    except Exception as e:
        print(f"News search error: {e}")
        return json.dumps({
            'query': query,
            'results': [],
            'total': 0,
            'error': str(e)
        })

async def fetch_feed(session, feed_url, query):
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
                    
                if query.lower() in title.lower() or query.lower() in desc.lower():
                    results.append({
                        'title': title,
                        'text': desc,
                        'url': link
                    })
            return results
    except Exception as feed_error:
        print(f"Error fetching feed {feed_url}: {feed_error}")
        return []


export = {
    'search_web': search_web,
    'search_wikipedia': search_wikipedia,
    'search_news': search_news,
    'fetch_feed': fetch_feed
}