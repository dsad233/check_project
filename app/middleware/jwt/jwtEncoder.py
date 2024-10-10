from abc import ABC, abstractmethod
from jose import jwt
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

class AbstractJWTEncoder(ABC):
    @abstractmethod
    def encode(
        self, data: dict, secret_key: str, algorithm: str
    ) -> str:
        pass
 
class JWTEncoder(AbstractJWTEncoder):
    def encode(
        self, data: dict, secret_key: str, algorithm: str
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(ZoneInfo("Asia/Seoul")) + timedelta(minutes=120)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, secret_key, algorithm=algorithm)
    

    