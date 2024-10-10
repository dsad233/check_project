from jwt.jwtEncoder import JWTEncoder
from jwt.jwtDecoder import JWTDecoder
from datetime import datetime
from zoneinfo import ZoneInfo
from app.api.utils.DB.config import settings

class JWTService:
    """
    JWT 로그인시 access token, refresh token을 생성하는 로직
    """
 
    def __init__(
        self,
        encoder: JWTEncoder,
        decoder: JWTDecoder
    ):
        self.encoder = encoder
        self.decoder = decoder
        self.algorithm = settings.JWT_ALGORITHM
        self.secret_key = settings.JWT_SECRET_KEY
        self.access_token_expire_time = 120
        self.refresh_token_expire_time = 120
 
    def create_access_token(self, data: dict) -> str:
        return self._create_token(data, self.access_token_expire_time)
 
    def create_refresh_token(self, data: dict) -> str:
        return self._create_token(data, self.refresh_token_expire_time)
 
    def _create_token(self, data: dict) -> str:
        return self.encoder.encode(data, self.secret_key, self.algorithm)
 
    def check_token_expired(self, token: str) -> dict | None:
        payload = self.decoder.decode(token, self.secret_key, self.algorithm)
 
        now = datetime.timestamp(datetime.now(ZoneInfo("Asia/Seoul")))
        if payload and payload["exp"] < now:
            return None
 
        return payload