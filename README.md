# WIP

# ShopeeZap Python API

Automação inteligente para enviar promoções do Shopee no WhatsApp Business usando Evolution API.

## ✨ Funcionalidades

- 🛍️ Converte links de afiliado do Shopee
- 📱 Integração com WhatsApp Business (Evolution API)
- 💬 Formata e envia mensagens automáticas
- ⚡ Assíncrono com FastAPI
- 🐳 Containerizado com Docker

## 🛠️ Tech Stack

- **Backend**: Python 3.11
- **Framework**: FastAPI
- **HTTP Client**: httpx (async)
- **Validação**: Pydantic
- **API WhatsApp**: Evolution API
- **Containerização**: Docker & Docker Compose

## 📋 Pré-requisitos

- Python 3.11+
- Evolution API rodando localmente ou em servidor
- Conta WhatsApp Business

## Setup

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/ShopeeZapPython.git
cd ShopeeZapPython

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais
```

## Rodar

```bash
uvicorn app.main:app --reload

docker compose up -d
A API estará disponível em http://localhost:8000

```

## Endpoints

>>>>>>> c605a69 (feat: integração com Evolution API para WhatsApp Business)
POST /api/promotion/send - Envia promoção no WhatsApp
