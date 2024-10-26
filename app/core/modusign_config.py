from app.core.config import settings

# 모두싸인 API 관련 설정
MODUSIGN_BASE_URL = "https://api.modusign.co.kr"
MODUSIGN_API_KEY = settings.MODUSIGN_API_KEY
MODUSIGN_WEBHOOK_URL = settings.MODUSIGN_WEBHOOK_URL

MODUSIGN_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization": f"Basic {MODUSIGN_API_KEY}"
}