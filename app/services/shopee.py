import time
import hashlib
import hmac
import json
import httpx

class ShopeeService:
    def __init__(self):
        self.app_id = "APP_ID_AQUI"
        self.secret = "SECRET_KEY_AQUI"
        self.api_url = "https://open-api.affiliate.shopee.com.br/api/v1/graphql"

    def _generate_signature(self, payload_str: str, timestamp: int) -> str:
        factor = f"{self.app_id}{timestamp}{payload_str}"
        signature = hmac.new(
            self.secret.encode("utf-8"),
            factor.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def convert_link(self, original_url: str) -> str:
        if self.app_id == "APP_ID_AQUI" or self.secret == "SECRET_KEY_AQUI":
            print("⚠️ Chaves da Shopee não configuradas. Retornando link simulado.")
            return f"https://shope.ee/m/simulado_{int(time.time())}"
        
        timestamp = int(time.time())

        query = """
        mutation {
            generatePromotionLink(
                originLink: "%s"
            ){
                promotionLink
            }
        }
        """ % original_url

        payload = {"query": query}
        payload_str = json.dumps(payload)

        signature = self._generate_signature(payload_str, timestamp)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"SHA256 Credential={self.app_id}, Timestamp={timestamp}, Signature={signature}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, headers=headers, content=payload_str, timeout=10.0)

                if response.status_code == 200:
                    data = response.json()

                    if "errors" in data:
                        print(f"❌ Erro da API Shopee: {data['errors']}")
                        return original_url
                    
                    link = data["data"]["generatePromotionLink"]["promotionLink"]
                    return link
                else:
                    print(f"❌ Falha na API da Shopee. Status: {response.status_code}. Resposta: {response.text}")
                    return original_url
        
        except Exception as e:
            print(f"🚨 Erro ao converter link na Shopee: {e}")
            return original_url