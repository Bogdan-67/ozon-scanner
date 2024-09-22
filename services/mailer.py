import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()


# Функция для отправки электронного письма
def send_email(subject, body):
    receiver_email = "tugay.bogdan03@mail.ru"

    message = MIMEText(body, 'plain', 'utf-8')
    message['Subject'] = subject
    message['From'] = "Ozon Scanner"
    message['To'] = receiver_email

    # Подключение к серверу SMTP и отправка письма
    with smtplib.SMTP_SSL(f"{os.getenv('SMTP_HOST')}:{os.getenv('SMTP_PORT')}") as server:
        server.login(os.getenv('EMAIL_LOGIN'), os.getenv('EMAIL_PASSWORD'))
        server.send_message(message)