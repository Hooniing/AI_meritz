import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_html_email(subject: str, html: str):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    to_addr = os.getenv("NEWSLETTER_TO")
    from_addr = os.getenv("NEWSLETTER_FROM") or user

    if not all([host, port, user, password, to_addr]):
        raise ValueError("SMTP/recipient env vars are missing")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(from_addr, [x.strip() for x in to_addr.split(",")], msg.as_string())
