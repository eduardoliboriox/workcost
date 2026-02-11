import smtplib
from email.message import EmailMessage
from flask import current_app


def send_email(to_email: str, subject: str, body: str):
    """
    Serviço genérico de envio de email.
    Responsabilidade única: comunicação SMTP.
    """

    config = current_app.config

    if not config.get("SMTP_HOST"):
        raise RuntimeError("SMTP não configurado")

    msg = EmailMessage()
    msg["From"] = config["SMTP_FROM"]
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(config["SMTP_HOST"], config["SMTP_PORT"]) as server:
            if config["SMTP_USE_TLS"]:
                server.starttls()

            server.login(
                config["SMTP_USERNAME"],
                config["SMTP_PASSWORD"]
            )

            server.send_message(msg)

    except Exception as e:
        raise RuntimeError(f"Erro ao enviar email: {str(e)}")
