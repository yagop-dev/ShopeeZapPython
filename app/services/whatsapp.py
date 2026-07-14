import asyncio

class WhatsAppService:
    async def send_message(self, message: str) -> bool:
        await asyncio.sleep(0.5)
        return True