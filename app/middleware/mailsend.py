from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from pydantic_settings import BaseSettings

app = FastAPI()

class MailSend(BaseSettings):
    to_email : EmailStr
    title : str = Field(None, description="메일 전송 제목")
    context : str = Field(None, description= "메일 전송 내용")

# SMTP 설정 (예시: Gmail SMTP 서버)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@gmail.com"
SMTP_PASSWORD = "your_email_password"


def send_email(to_email: str, subject: str, message: str):
    try:
        # 이메일 작성
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        # SMTP 서버 연결
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)

        # 이메일 전송
        server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")


@app.post("/send-email/")
async def send_email_endpoint(email_data: EmailSchema, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email_data.email, email_data.subject, email_data.message)
    return {"message": "Email has been sent in the background."}
