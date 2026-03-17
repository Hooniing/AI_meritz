import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_newsletter_email(issue, html: str):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    to_addr = os.getenv("NEWSLETTER_TO")
    from_addr = os.getenv("NEWSLETTER_FROM") or user

    if not all([host, user, password, to_addr]):
        raise ValueError("SMTP/recipient env vars are missing")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[{issue.title}] {issue.period_start} ~ {issue.period_end}"
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(html, "html", "utf-8"))

    recipients = [x.strip() for x in to_addr.split(",") if x.strip()]

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(from_addr, recipients, msg.as_string())
