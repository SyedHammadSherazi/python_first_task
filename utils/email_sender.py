import os
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

from utils.logger import get_logger


load_dotenv()

logger = get_logger(__name__)


@dataclass
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    from_email: str
    from_name: str = "Python Automation Tool"
    use_tls: bool = True
    use_ssl: bool = False
    timeout: int = 20


def _get_bool_env(key, default=False):
    value = os.getenv(key)

    if value is None:
        return default

    return value.lower() in ["true", "1", "yes", "y"]


def is_email_notifications_enabled():
    return _get_bool_env("EMAIL_NOTIFICATIONS_ENABLED", False)


def load_smtp_config():
    """
    SMTP config environment variables se load hoti hai.
    Credentials code mein hardcoded nahi hain.
    """

    host = os.getenv("SMTP_HOST")
    port = os.getenv("SMTP_PORT", "587")
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("SMTP_FROM_EMAIL")
    from_name = os.getenv("SMTP_FROM_NAME", "Python Automation Tool")

    if not host:
        raise ValueError("SMTP_HOST is missing.")

    if not username:
        raise ValueError("SMTP_USERNAME is missing.")

    if not password:
        raise ValueError("SMTP_PASSWORD is missing.")

    if not from_email:
        raise ValueError("SMTP_FROM_EMAIL is missing.")

    config = SMTPConfig(
        host=host,
        port=int(port),
        username=username,
        password=password,
        from_email=from_email,
        from_name=from_name,
        use_tls=_get_bool_env("SMTP_USE_TLS", True),
        use_ssl=_get_bool_env("SMTP_USE_SSL", False),
        timeout=int(os.getenv("SMTP_TIMEOUT", "20")),
    )

    logger.info(
        f"SMTP CONFIG LOADED | host={config.host} | port={config.port} | "
        f"from_email={config.from_email} | use_tls={config.use_tls} | use_ssl={config.use_ssl}"
    )

    return config


def _normalize_recipients(recipients):
    if recipients is None:
        return []

    if isinstance(recipients, str):
        return [recipients]

    return list(recipients)


def _attach_files(message, attachments):
    if not attachments:
        return

    for attachment_path in attachments:
        file_path = Path(attachment_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Attachment not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Attachment path is not a file: {file_path}")

        file_data = file_path.read_bytes()

        message.add_attachment(
            file_data,
            maintype="application",
            subtype="octet-stream",
            filename=file_path.name,
        )

        logger.info(f"EMAIL ATTACHMENT ADDED | {file_path}")


def build_email_message(
    to_email,
    subject,
    body,
    html_body=None,
    cc=None,
    bcc=None,
    attachments=None,
    config=None,
):
    if config is None:
        config = load_smtp_config()

    to_list = _normalize_recipients(to_email)
    cc_list = _normalize_recipients(cc)
    bcc_list = _normalize_recipients(bcc)

    if not to_list:
        raise ValueError("At least one recipient email is required.")

    if not subject:
        raise ValueError("Email subject is required.")

    if not body:
        raise ValueError("Email body is required.")

    message = EmailMessage()

    message["From"] = f"{config.from_name} <{config.from_email}>"
    message["To"] = ", ".join(to_list)
    message["Subject"] = subject

    if cc_list:
        message["Cc"] = ", ".join(cc_list)

    if bcc_list:
        message["Bcc"] = ", ".join(bcc_list)

    message.set_content(body)

    if html_body:
        message.add_alternative(html_body, subtype="html")

    _attach_files(message, attachments)

    logger.info(
        f"EMAIL MESSAGE BUILT | to={to_list} | cc={cc_list} | "
        f"bcc_count={len(bcc_list)} | subject={subject}"
    )

    return message


def send_email(
    to_email,
    subject,
    body,
    html_body=None,
    cc=None,
    bcc=None,
    attachments=None,
    config=None,
):
    if config is None:
        config = load_smtp_config()

    message = build_email_message(
        to_email=to_email,
        subject=subject,
        body=body,
        html_body=html_body,
        cc=cc,
        bcc=bcc,
        attachments=attachments,
        config=config,
    )

    logger.info(
        f"EMAIL SEND STARTED | host={config.host} | port={config.port} | "
        f"to={to_email} | subject={subject}"
    )

    try:
        if config.use_ssl:
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL(
                config.host,
                config.port,
                timeout=config.timeout,
                context=context,
            ) as smtp:
                smtp.login(config.username, config.password)
                smtp.send_message(message)

        else:
            with smtplib.SMTP(
                config.host,
                config.port,
                timeout=config.timeout,
            ) as smtp:
                smtp.ehlo()

                if config.use_tls:
                    context = ssl.create_default_context()
                    smtp.starttls(context=context)
                    smtp.ehlo()

                smtp.login(config.username, config.password)
                smtp.send_message(message)

        logger.info(f"EMAIL SENT SUCCESSFULLY | to={to_email} | subject={subject}")
        print("Email sent successfully.")
        return True

    except Exception as error:
        logger.exception(
            f"EMAIL SEND FAILED | to={to_email} | subject={subject} | Error: {error}"
        )
        print(f"Email failed: {error}")
        return False


def send_task_notification(task_name, status, details=None, to_email=None):
    """
    Task completion/failure notification send karta hai.
    EMAIL_NOTIFICATIONS_ENABLED=true ho to email send hogi.
    """

    if not is_email_notifications_enabled():
        logger.info(
            f"EMAIL NOTIFICATION SKIPPED | disabled | task={task_name} | status={status}"
        )
        return False

    recipient = to_email or os.getenv("NOTIFICATION_EMAIL")

    if not recipient:
        raise ValueError("NOTIFICATION_EMAIL is missing.")

    details_text = str(details or "No details provided.")

    subject = f"Task Notification: {task_name} - {status}"

    body = f"""Task Notification

Task Name: {task_name}
Status: {status}

Details:
{details_text}
"""

    html_body = f"""
    <h2>Task Notification</h2>
    <p><strong>Task Name:</strong> {task_name}</p>
    <p><strong>Status:</strong> {status}</p>
    <p><strong>Details:</strong></p>
    <pre>{details_text}</pre>
    """

    logger.info(
        f"TASK NOTIFICATION EMAIL STARTED | task={task_name} | status={status}"
    )

    return send_email(
        to_email=recipient,
        subject=subject,
        body=body,
        html_body=html_body,
    )