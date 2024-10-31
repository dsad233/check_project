from enum import Enum


class SIGNINGMETHOD_OBJECT_TYPE(str, Enum):
    KAKAO = "KAKAO"
    EMAIL = "EMAIL"
    SECURE_LINK = "SECURE_LINK"
