from pydantic import BaseModel

# 회원가입 스키마
class Register(BaseModel):
    email: str
    password: str
    nickname: str


# 로그인
class Login(BaseModel):
    email : str
    password : str

# 토큰 발급
class Token(BaseModel):
    authorization: str = None
