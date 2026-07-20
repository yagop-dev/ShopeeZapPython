from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import PromotionRequest, PromotionResponse, WebHookData
from app.services.shopee import ShopeeService
from app.services.whatsapp import WhatsAppService
from app.config import settings
import re
import redis.asyncio as redis

app = FastAPI(title="ShopeeZap API - Python")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

shopee_service = ShopeeService()
whatsapp_service = WhatsAppService()

@app.post("/api/promotion/send", response_model=PromotionResponse)
async def send_promotion(request: PromotionRequest):
    try:
        converted_url = await shopee_service.convert_link(request.original_url)
        full_message = (
            f"*ACHADINHO!* 🔥\n\n"
            f"{request.description}\n\n"
            f"🤑 Por apenas: {request.price}\n\n"
            f"👉 Compre aqui: {converted_url}"
        )

        sent = await whatsapp_service.send_message(full_message)

        if not sent:
            raise HTTPException(status_code=400, detail="Falha ao enviar mensagem no WhatsApp.")
        
        return PromotionResponse(
            success=True,
            message="Promoção enviada com sucesso!",
            converted_url=converted_url
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    

redis_client = redis.Redis(
    host = settings.REDIS_HOST,
    port = settings.REDIS_PORT,
    db = 0,
    decode_responses= True
)
    
@app.post("/webhook/whatsapp")
async def receive_whatsapp_webhook(webhook: WebHookData):
    if webhook.event != "messages.upsert":
        return {"status": "ignored", "reason": "Not a message upsert event"}

    message_data = webhook.data

    remote_jid = message_data.get("key", {}).get("remoteJid", "")
    if remote_jid != settings.ALLOWED_GROUP_JID:
        return {"status": "ignored", "reason": "Message from unauthorized chat/group"}

    message_id = message_data.get("key", {}).get("id")
    if not message_id:
        return {"status": "ignored", "reason": "No message ID found"}
    
    is_new_message = await redis_client.set(f"msg_id:{message_id}", "1", ex=86400, nx=True)  
    if not is_new_message:
        print(f"⚠️ [WEBHOOK] Mensagme duplicada ignorada pelo Redis (ID:{message_id})")
        return {"status": "ignored", "reason": "Duplicate message"}

    message_text = message_data.get("message", {}).get("conversation") or \
                   message_data.get("message", {}).get("extendedTextMessage", {}).get("text")          
    if not message_text:
        return {"status": "ignored", "reason": "No text content found"}    

    shopee_url_pattern = r"https?://(?:www\.)?(?:shopee\.com\.br|shope\.ee)/[^\s]+"
    match = re.search(shopee_url_pattern, message_text)

    if not match:
        return {"status": "ignored", "reason": "No Shopee link found in text"}

    original_url = match.group(0)
    sender = message_data.get("pushName", "Desconhecido")

    print(f"\n📥 [WEBHOOK] Nova oferta processada (ID: {message_id} de: {sender})")

    try:
        converted_url = await shopee_service.convert_link(original_url)

        full_message = (
            f"*ACHADINHO AUTOMÁTICO!* 🔥\n\n"
            f"{message_text.replace(original_url, '').strip()}\n\n"
            f"👉 Compre aqui: {converted_url}"
        )
        
        await whatsapp_service.send_message(full_message)

    except Exception as e:
        await redis_client.delete(f"mesg_id:{message_id}")
        print(f"🚨 [WEBHOOK] Erro ao processar automação do link: {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "success", "processed": True, "extracted_url": original_url}