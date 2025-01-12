import aiohttp
import time
from datetime import datetime

days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

async def query_lm_studio(prompt, prompt2=None, memory_manager=None, system_ip=""):
    start_time = time.time()
    url = "http://localhost:6666/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    dt = datetime.now()

    # Create context
    context = {
        "timestamp": dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "day": days[dt.weekday()],
        "system_info": {
            "ip": system_ip
        }
    }

    # Get memory context
    memory_context = ""
    if memory_manager:
        results = await memory_manager.search(prompt)
        best_outputs = []
        for result in sorted(results, key=lambda x: x["similarity"], reverse=True)[:3]:
            best_outputs.append(result)

        for output in best_outputs:
            memory_context += f"{output['text']}\n"

    # Format context
    context_prompt = f"""Current Context:
    Time: {context['timestamp']} ({context['day']})
    System: 
    IP: {context['system_info']['ip']}

    Memory Context:
    {memory_context}
    """

    messages = [
        {"role": "user", "content": context_prompt},
        {"role": "user", "content": prompt}
    ]

    if prompt2:
        messages.append({"role": "user", "content": prompt2})

    payload = {
        "model": "unsloth/llama-3.2-3b-instruct",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                elapsed_time = round(time.time() - start_time, 2)
                print(f"LM Studio response time: {elapsed_time} seconds")
                return await response.json()
    except Exception as e:
        print(f"LM Studio error: {e}")
        elapsed_time = round(time.time() - start_time, 2)
        print(f"LM Studio response time: {elapsed_time} seconds")
        return None

export = {
    "query_lm_studio": query_lm_studio
}