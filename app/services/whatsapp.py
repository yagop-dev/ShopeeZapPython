import httpx
from app.config import settings

class WhatsAppService:
    def __init__(self):
        self.api_url = settings.EVOLUTION_API_URL
        self.instance_name = settings.EVOLUTION_INSTANCE_NAME
        self.api_key = settings.EVOLUTION_API_KEY
        self.default_destination = settings.DEFAULT_DESTINATION

    async def send_message(self, message: str, destination: Optional[str] = None) -> bool:

        target = destination or self.default_destination

        url = f"{self.api_url}/message/sendText/{self.instance_name}"

        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "number": target,
            "options": {
                "delay": 1200,
                "presence": "composing"
            },
            "textMessage":{
                "text": message
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=10.0)

                if response.status_code in [200, 201]:
                    print(f"✅ Mensagem enviada com sucesso para {target}!")
                    return True
                else:
                    print(f"❌ Falha no envio para {target}. Status: {response.status_code}. Resposta: {response.text}")
                    return False
        except Exception as e:
            print(f"🚨 Erro de conexão com a Evolution API: {e}")
            return False