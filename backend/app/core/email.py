import os
import smtplib
from email.message import EmailMessage


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send email using SMTP settings from environment.

    Environment variables:
    - SMTP_HOST: smtp server host
    - SMTP_PORT: smtp port (optional; defaults: 587 for STARTTLS, 465 for SSL if SMTP_USE_SSL=1)
    - SMTP_USER / SMTP_PASS: optional credentials
    - SMTP_USE_SSL: if set ('1' or 'true') use SMTP_SSL on port (default 465)
    - SMTP_NO_TLS: if set, do not call starttls() (for plaintext servers)
    - FROM_EMAIL: envelope From header

    If SMTP is not configured, prints the email to stdout (development fallback) and returns True.
    Returns True on success, False on failure.
    """
    host = os.getenv('SMTP_HOST')
    port_env = os.getenv('SMTP_PORT')
    use_ssl = os.getenv('SMTP_USE_SSL', '').lower() in ('1', 'true', 'yes')
    no_tls = os.getenv('SMTP_NO_TLS', '').lower() in ('1', 'true', 'yes')
    user = os.getenv('SMTP_USER')
    pwd = os.getenv('SMTP_PASS')
    from_addr = os.getenv('FROM_EMAIL', 'noreply@example.com')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_email
    msg.set_content(body)

    # If SMTP not configured, fallback to logging
    if not host:
        print('Email not sent — SMTP not configured. To:', to_email)
        print('Subject:', subject)
        print(body)
        return True

    # Determine port defaults
    try:
        port = int(port_env) if port_env else (465 if use_ssl else 587)
    except Exception:
        port = 465 if use_ssl else 587

    try:
        if use_ssl:
            with smtplib.SMTP_SSL(host, port, timeout=10) as s:
                if user and pwd:
                    s.login(user, pwd)
                s.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=10) as s:
                s.ehlo()
                if not no_tls:
                    s.starttls()
                    s.ehlo()
                if user and pwd:
                    s.login(user, pwd)
                s.send_message(msg)
        return True
    except Exception as e:
        # Log the error to stdout for visibility in development
        print('Failed to send email:', e)
        print('Email details — To:', to_email, 'Subject:', subject)
        return False