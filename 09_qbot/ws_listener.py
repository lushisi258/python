# ws_listener.py
import asyncio
import json
import websockets
from chat_ai import get_ai_reply, should_ai_reply
from qq_sender import send_group_message

group_histories = {}  # { group_id: [ {username, message}, ... ] }
MAX_HISTORY = 20

async def handle_event(msg):
    data = json.loads(msg)
    if data.get("post_type") == "message" and data.get("message_type") == "group":
        group_id = data["group_id"]
        raw_message = data["raw_message"]
        user_id = data["user_id"]
        sender_name = data["sender"].get("nickname", str(user_id))  # 获取用户名

        print(f"收到消息：{sender_name}：{raw_message}")

        # 维护历史记录
        if group_id not in group_histories:
            group_histories[group_id] = []
        group_histories[group_id].append({"username": sender_name, "message": raw_message})
        group_histories[group_id] = group_histories[group_id][-MAX_HISTORY:]

        # 判断是否应回复
        history = group_histories[group_id]
        if await should_ai_reply(history):
            reply = await get_ai_reply(history)
            await send_group_message(group_id, reply)


async def listen():
    uri = "ws://localhost:3001/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            msg = await websocket.recv()
            await handle_event(msg)

if __name__ == "__main__":
    asyncio.run(listen())
