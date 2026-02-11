from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app


def send_email(to_email: str, subject: str, body: str):
    """
    Envio de email via SendGrid API (HTTP).
    Seguro para Railway.
    """

    api_key = current_app.config.get("SENDGRID_API_KEY")
    sender = current_app.config.get("SENDGRID_FROM")

    if not api_key:
        raise RuntimeError("SENDGRID_API_KEY não configurada")

    message = Mail(
        from_email=sender,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )

    try:
        sg = SendGridAPIClient(api_key)
        sg.send(message)
    except Exception as e:
        raise RuntimeError(f"Erro ao enviar email: {str(e)}")
