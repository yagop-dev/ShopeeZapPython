from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import PromotionRequest, PromotionResponse, WebHookData
from app.services.shopee import ShopeeService
from app.services.whatsapp import WhatsAppService
import re

app = FastAPI(title="ShopeeZap API - Python")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
@app.post("/webhook/whatsapp")
async def receive_whatsapp_webhook(webhook: WebHookData):
    if webhook.event != "messages.upsert":
        return {"status": "ignored", "reason": "Not a message upsert event"}

    message_data = webhook.data
    
    message_text = message_data.get("message", {}).get("conversation") or \
                   message_data.get("message", {}).get("extendedTextMessage", {}).get("text")
                   
    if not message_text:
        return {"status": "ignored", "reason": "No text content found"}

    remote_jid = message_data.get("key", {}).get("remoteJid", "")
    is_group = "@g.us" in remote_jid
    sender = message_data.get("pushName", "Desconhecido")

    shopee_url_pattern = r"https?://(?:www\.)?(?:shopee\.com\.br|shope\.ee)/[^\s]+"
    match = re.search(shopee_url_pattern, message_text)

    if not match:
        print(f"ℹ️ [WEBHOOK] Mensagem de {sender} ignorada: Nenhum link da Shopee encontrado.")
        return {"status": "ignored", "reason": "No Shopee link found in text"}

    original_url = match.group(0)

    print(f"\n📥 [WEBHOOK] Link da Shopee detectado!")
    print(f"👥 Origem: {sender} (Grupo: {is_group})")
    print(f"🔗 Link Original: {original_url}")

    try:
        converted_url = await shopee_service.convert_link(original_url)

        full_message = (
            f"*ACHADINHO AUTOMÁTICO!* 🔥\n\n"
            f"{message_text.replace(original_url, '').strip()}\n\n"
            f"👉 Compre aqui: {converted_url}"
        )
        
        await whatsapp_service.send_message(full_message)
        print(f"✅ [WEBHOOK] Oferta convertida e enviada com sucesso!\n")

    except Exception as e:
        print(f"🚨 [WEBHOOK] Erro ao processar automação do link: {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "success", "processed": True, "extracted_url": original_url}