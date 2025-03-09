TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather forecast for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city to get weather for"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Search Wikipedia for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Get news articles about a topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The news topic to search for"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Execute a system command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command_type": {
                        "type": "string",
                        "enum": ["cmd", "ps"],
                        "description": "Type of command (cmd or ps)"
                    },
                    "command": {
                        "type": "string",
                        "description": "The command to execute"
                    }
                },
                "required": ["command_type", "command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_browser",
            "description": "Open a URL in the default browser",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to open"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_memory",
            "description": "Add a new text to memory",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to add to memory"
                    }
                },
                "required": ["text"]
            }
        }
    }
]

DYNAMIC_TOOLS = [
    "get_weather",
    "search_wikipedia",
    "get_news",
    "add_memory"
]