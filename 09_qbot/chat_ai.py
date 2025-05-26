import httpx
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-chat-v3-0324:free"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://mydomain.com",
    "X-Title": "qqbot",
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
                "你是一个热心群友，但也不会在别人未发言完毕或者别人正跟特定的人交流时毫无理由的插话。"
                "以下是最近的群聊记录，请判断你现在是否应该发言。只回答“是”或“否”。"
            )
        }
    ] + format_messages(history)

    payload = {
        "model": MODEL,
        "messages": prompt,
        "temperature": 0.3
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content'].lower()
            return "是" in content
    except Exception as e:
        print("[AI 判断失败]", e)
        return False

# 获取 AI 回复
async def get_ai_reply(message: str, user_id: int) -> str:
    messages = [
        {"role": "system", "content": "你是一个有礼貌的中文助手，请简洁地回答问题。"},
        {"role": "user", "content": message}
    ]

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是一个中文助手"},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7
    }


    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"[AI Error] {e}")
            return "发生错误，无法获取 AI 回复。"
