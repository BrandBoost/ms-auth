import smtplib

from fastapi.exceptions import HTTPException

from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader

from app.config import settings, logger


async def send_mail(email: str, content: str):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Registration"
        msg["From"] = settings.EMAIL_HOST_USER
        msg["To"] = email
        msg.add_alternative(content, subtype="html")
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, 465) as smtp:
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp.send_message(msg)
        logger.info(f"Email successfully send: TO: {email}")
    except Exception:
        # TODO ask and update status code
        raise HTTPException(status_code=409)


async def open_html(user_email: str, user_name: str, user_code: str, action: bool):
    environment = Environment(loader=FileSystemLoader("app/static/templates"))
    try:
        if action:
            html_template = environment.get_template("reset.html")
        else:
            html_template = environment.get_template("change.html")
        data = {
            "user_email": user_email,
            "user_name": user_name,
            "user_code": user_code,
        }
        rendered = html_template.render(**data)
        return rendered

    except IOError:
        logger.info("The template file doesn't found")


async def get_email_verify_render(user_email: str, user_code: str):
    environment = Environment(loader=FileSystemLoader("app/static/templates"))
    try:
        html_template = environment.get_template("verify.html")
        data = {
            "user_email": user_email,
            "user_code": user_code,
        }
        rendered = html_template.render(**data)
        return rendered

    except IOError:
        logger.info("The template file doesn't found")
