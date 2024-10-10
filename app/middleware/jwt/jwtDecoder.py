from abc import ABC, abstractmethod
from jose import jwt, JWTError

class AbstractJWTDecoder(ABC):
    @abstractmethod
    def decode(self, token: str, secret_key: str, algorithm: str) -> dict | None:
        pass
 
class JWTDecoder(AbstractJWTDecoder):
    def decode(self, token: str, secret_key: str, algorithm: str) -> dict | None:
        try:
            return jwt.decode(token, secret_key, algorithms=algorithm)
        except JWTError:
            return None