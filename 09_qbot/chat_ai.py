# chat_ai.py
import os
import httpx
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()


OPENROUTER_API_KEY1 = os.getenv("OPENROUTER_API_KEY1")
OPENROUTER_API_KEY2 = os.getenv("OPENROUTER_API_KEY2")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
DEEPSEEK = "deepseek/deepseek-chat-v3-0324:free"
QWEN = "qwen/qwen3-8b:free"

headers1 = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY1}",
    "HTTP-Referer": "https://domain1.com",
    "X-Title": "qqbot1",
    "Content-Type": "application/json"
}

headers2 = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY1}",
    "HTTP-Referer": "https://domain2.com",
    "X-Title": "qqbot2",
    "Content-Type": "application/json"
}

# 对话格式化
def format_messages(history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [
        {"role": "user", "content": f"{msg['username']}：{msg['message']}"}
        for msg in history
    ]

# 判断是否应该说话
async def should_ai_reply(history: List[Dict[str, str]]) -> bool:
    prompt = [
        {
            "role": "system",
            "content": (
                "你是的名字叫“小A”，你的QQ号是：3830345203，“[CQ:at,qq=3830345203]”即为@你的消息。大家也可能用AI/机器人之类的词语来指代你。你是一个热情的人。"
                "你会主动的应答大家的群聊消息。以下是最近的群聊记录，请判断你现在是否应该发言。只回答“y”或“n”。"
            )
        }
    ] + format_messages(history)

    payload = {
        "model": QWEN,
        "messages": prompt,
        "temperature": 0.3
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OPENROUTER_BASE_URL, headers=headers2, json=payload)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content'].lower()
            print("judge_result:", content)
            return "y" in content
    except Exception as e:
        print("[AI 判断失败]", e)
        return False

# 获取 AI 回复
async def get_ai_reply(history: List[Dict[str, str]]) -> str:
    prompt = [
        {"role": "system", "content": (
            "你是一个中文 AI 群聊助手，名叫“小A”。"
            "请根据以下群聊历史，智能生成一句回复。不要回复多句话，也不要自说自话。"
        )}
    ] + format_messages(history)

    payload = {
        "model": DEEPSEEK,
        "messages": prompt,
        "temperature": 0.7
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OPENROUTER_BASE_URL, headers=headers1, json=payload)
            response.raise_for_status()
            data = response.json()
            print(data['choices'][0]['message']['content'])
            return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"[AI Error] {e}")
        return "发生错误，无法获取 AI 回复。"
