# ShopeeZap Python API

API para enviar promoções do Shopee via WhatsApp.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

pip install -r requirements.txt


## Rodar

```bash
uvicorn app.main:app --reload

## Endpoints

POST /api/promotion/send - Envia promoção no WhatsApp