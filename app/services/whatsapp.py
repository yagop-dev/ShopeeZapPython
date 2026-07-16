import httpx

class WhatsAppService:
    def __init__(self):
        self.api_url = "http://localhost:8080"
        self.instance_name = "GrupoOfertas"
        self.api_key = "SenhaDoGrupo999"

        self.default_destination = "NUMERO_WHATS_DESTINATARIO"

    async def send_message(self, message: str) -> bool:
        url = f"{self.api_url}/message/sendText/{self.instance_name}"

        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "number": self.default_destination,
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
                    print("✅ Mensagem enviada via Evolution API com sucesso!")
                    return True
                else:
                    print(f"❌ Falha no envio. Status: {response.status_code}. Resposta: {response.text}")
                    return False
        except Exception as e:
            print(f"🚨 Erro de conexão com a Evolution API: {e}")
            return False