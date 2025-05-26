import httpx

async def send_group_message(group_id: int, text: str):
    url = "http://localhost:3000/send_group_msg"
    payload = {
        "group_id": group_id,
        "message": [
            {
                "type": "text",
                "data": {
                    "text": text
                }
            }
        ]
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)
