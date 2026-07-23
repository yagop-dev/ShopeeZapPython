from typing import Dict, Any
from app.config import settings
import time
import hashlib
import json
import httpx
import logging

logger = logging.getLogger(__name__)


class ShopeeService:
    def __init__(self):
        self.app_id = str(settings.SHOPEE_APP_ID).strip() if settings.SHOPEE_APP_ID else ""
        self.secret_key = str(settings.SHOPEE_SECRET_KEY).strip() if settings.SHOPEE_SECRET_KEY else ""
        self.api_url = settings.SHOPEE_API_URL

    def _generate_signature(self, payload_str: str, timestamp: int) -> str:
        factor = f"{self.app_id}{timestamp}{payload_str}{self.secret_key}"
        return hashlib.sha256(factor.encode("utf-8")).hexdigest()

    async def expand_url(self, short_url: str) -> str:
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(short_url, timeout=5.0)
                return str(response.url)
        except Exception as e:
            logger.debug(f"Could not expand URL {short_url}: {e}")
            return short_url

    async def convert_link(self, original_url: str) -> Dict[str, Any]:
        if not self.app_id or not self.secret_key:
            logger.warning("Shopee credentials not configured")
            return {"converted_url": original_url, "product_name": "OFERTA IMPERDÍVEL!"}

        expanded_url = await self.expand_url(original_url)
        timestamp = int(time.time())

        query = f"""mutation {{generateShortLink(input: {{originUrl: "{expanded_url}"}}) {{shortLink}}}}"""
        
        payload = {"query": query}
        payload_str = json.dumps(payload, separators=(',', ':'))
        signature = self._generate_signature(payload_str, timestamp)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"SHA256 Credential={self.app_id},Timestamp={timestamp},Signature={signature}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url, 
                    headers=headers, 
                    content=payload_str, 
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()

                    if "errors" in data:
                        error_msg = data['errors'][0].get('message', 'Unknown error')
                        logger.error(f"Shopee API error: {error_msg}")
                        return {"converted_url": original_url, "product_name": "OFERTA IMPERDÍVEL!"}
                    
                    short_link = data.get("data", {}).get("generateShortLink", {}).get("shortLink")
                    
                    if short_link:
                        logger.info(f"Link converted successfully: {original_url[:50]}... → {short_link}")
                        return {
                            "converted_url": short_link,
                            "product_name": "OFERTA IMPERDÍVEL!"
                        }
                    else:
                        logger.warning(f"No shortLink returned for {original_url}")
                        return {"converted_url": original_url, "product_name": "OFERTA IMPERDÍVEL!"}
                else:
                    logger.error(f"Shopee API HTTP {response.status_code}: {response.text[:200]}")
                    return {"converted_url": original_url, "product_name": "OFERTA IMPERDÍVEL!"}
        
        except Exception as e:
            logger.exception(f"Error converting link: {e}")
            return {"converted_url": original_url, "product_name": "OFERTA IMPERDÍVEL!"}
