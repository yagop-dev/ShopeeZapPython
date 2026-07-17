from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import PromotionRequest, PromotionResponse
from app.services.shopee import ShopeeService
from app.services.whatsapp import WhatsAppService

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