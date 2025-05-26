import asyncio
import json
import websockets
from chat_ai import get_ai_reply, should_ai_reply
from qq_sender import send_group_message

async def handle_event(msg):
    data = json.loads(msg)
    if data.get("post_type") == "message" and data.get("message_type") == "group":
        group_id = data["group_id"]
        raw_message = data["raw_message"]
        user_id = data["user_id"]
        print(f"收到消息：{raw_message}")
        
        if should_ai_reply():
            reply = await get_ai_reply(raw_message, user_id)
        await send_group_message(group_id, reply)

async def listen():
    uri = "ws://localhost:3001/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            msg = await websocket.recv()
            await handle_event(msg)

if __name__ == "__main__":
    asyncio.run(listen())
