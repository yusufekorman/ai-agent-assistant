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

async def query_lm_studio(prompt, answer=None, prompt2=None, system_ip="", model='unsloth/llama-3.2-3b-instruct', memory_vectors=[], config={}):
    start_time = time.time()
    # print(config["lm_studio_completions_url"])
    url = config["lm_studio_completions_url"]
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

    # Format context
    context_prompt = f"""Current Context:
    Time: {context['timestamp']} ({context['day']})
    System IP: {context['system_info']['ip']}
    """

    if memory_vectors:
        context_prompt += f"Memory Vector: \n"
        for memoryVector in memory_vectors:
            context_prompt += f"- {memoryVector}\n"

    messages = [
        {"role": "user", "content": context_prompt},
        {"role": "user", "content": prompt}
    ]

    if answer:
        messages.append({"role": "assistant", "content": answer})

    if prompt2:
        messages.append({"role": "user", "content": prompt2})

    payload = {
        "model": model,
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

                # for debugging
                """
                with open("ai_logs.log", "a") as f:
                    f.write(f"Request: {payload}\n")
                    f.write(f"Response: {await response.text()}\n\n")
                """
                return await response.json()
    except Exception as e:
        print(f"LM Studio error: {e}")
        elapsed_time = round(time.time() - start_time, 2)
        print(f"LM Studio response time: {elapsed_time} seconds")
        return None

export = {
    "query_lm_studio": query_lm_studio
}