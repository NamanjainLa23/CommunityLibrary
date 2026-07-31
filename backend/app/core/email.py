import os
import smtplib
from email.message import EmailMessage

def send_email(to_email: str, subject: str, body: str):
    host = os.getenv('SMTP_HOST')
    port = int(os.getenv('SMTP_PORT', '0')) if os.getenv('SMTP_PORT') else None
    user = os.getenv('SMTP_USER')
    pwd = os.getenv('SMTP_PASS')
    from_addr = os.getenv('FROM_EMAIL', '')

    msg = EmailMessage()
    