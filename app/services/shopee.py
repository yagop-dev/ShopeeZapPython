from typing import Dict, Any
from app.config import settings
import time
import hashlib
import hmac
import json
import httpx

class ShopeeService:
    def __init__(self):
        self.app_id = settings.SHOPEE_APP_ID
        self.secret_key = settings.SHOPEE_SECRET_KEY
        self.api_url = settings.SHOPEE_API_URL

    def _generate_signature(self, payload_str: str, timestamp: int) -> str:
        factor = f"{self.app_id}{timestamp}{payload_str}"
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            factor.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def convert_link(self, original_url: str) -> str:
        if not self.app_id or not self.secret_key:
            print("⚠️ Chaves da Shopee não configuradas. Retornando link simulado.")
            return {
                "converted_url": f"https://shope.ee/m/simulado_{int(time.time())}",
                "product_name": "🔥 Produto da Shopee (Titulo Simulado)"
            }
        timestamp = int(time.time())

        query = """
        mutation {
            generatePromotionLink(
                originLink: "%s"
            ){
                promotionLink
                productName
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
                        return {
                            "converted_url": original_url,
                            "product_name": "OFERTA IMPERDÍVEL!"
                        }
                    
                    result_data = data.get("data", {}).get("generatePromotionLink", {})
                    link = result_data.get("promotionLink", original_url)
                    product_name = result_data.get("productName", "OFERTA IMPERDÍVEL!")
                    
                    return {
                        "converted_url": link,
                        "product_name": product_name
                    }
                
                else:
                    print(f"❌ Falha na API da Shopee. Status: {response.status_code}. Resposta: {response.text}")
                    return {
                        "converted_url": original_url,
                        "product_name": "OFERTA IMPERDÍVEL!"
                    }
        
        except Exception as e:
            print(f"🚨 Erro ao converter link na Shopee: {e}")
            return {
                "converted_url": original_url,
                "product_name": "OFERTA IMPERDÍVEL!"
            }
        