import os
import smtplib
from email.message import EmailMessage


def send_email(to_email: str, subject: str, body: str):
    """Send email using SMTP settings from environment. If not configured, log to stdout."""
    host = os.getenv('SMTP_HOST')
    port = int(os.getenv('SMTP_PORT', '0')) if os.getenv('SMTP_PORT') else None
    user = os.getenv('SMTP_USER')
    pwd = os.getenv('SMTP_PASS')
    from_addr = os.getenv('FROM_EMAIL', 'noreply@example.com')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_email
    msg.set_content(body)

    if not host or not port:
        print('Email not sent — SMTP not configured. To:', to_email)
        print('Subject:', subject)
        print(body)
        return True

    try:
        with smtplib.SMTP(host, port, timeout=10) as s:
            s.starttls()
            if user and pwd:
                s.login(user, pwd)
            s.send_message(msg)
        return True
    except Exception as e:
        print('Failed to send email:', e)
        return False
