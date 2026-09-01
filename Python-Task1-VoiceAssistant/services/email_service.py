"""
Email Service Module for Intelligent Python Voice Assistant.
Handles secure SMTP email delivery using smtplib with robust error handling and credential safety.
"""

import re
import socket
import smtplib
from email.message import EmailMessage
from typing import Dict, Any, Optional
from config import Config
from core.logger import get_logger

logger = get_logger("EmailService")

class EmailService:
    """SMTP Email dispatch engine."""

    EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    @classmethod
    def validate_recipient(cls, recipient: str) -> bool:
        """Validates format of recipient email address."""
        if not recipient or not recipient.strip():
            return False
        return bool(cls.EMAIL_REGEX.match(recipient.strip()))

    @classmethod
    def send_email(cls, recipient: str, subject: Optional[str] = None, body: Optional[str] = None) -> Dict[str, Any]:
        """
        Sends an email securely using SMTP credentials configured in Config/.env.
        Returns a structured dictionary with execution status and safety guarantees.
        Never prints or exposes passwords or sensitive credentials in logs/errors.
        """
        target_recipient = (recipient or "").strip()
        mail_subject = (subject or "Voice Assistant Message").strip()
        mail_body = (body or "").strip()

        # Step 1: Validate configuration
        secrets_status = Config.validate_secrets_loaded()
        if not secrets_status.get("email_configured") and not secrets_status.get("smtp_configured"):
            logger.warning("[EmailService] Email credentials are not configured in .env.")
            return {
                "success": False,
                "recipient": target_recipient,
                "subject": mail_subject,
                "error_type": "missing_config",
                "error": "Email credentials are not configured in .env."
            }

        # Step 2: Validate recipient address
        if not cls.validate_recipient(target_recipient):
            logger.warning(f"[EmailService] Invalid recipient address provided: '{target_recipient}'")
            return {
                "success": False,
                "recipient": target_recipient,
                "subject": mail_subject,
                "error_type": "invalid_recipient",
                "error": f"Invalid recipient email address: '{target_recipient}'."
            }

        logger.info(f"[EmailService] Preparing to send email to: {target_recipient}")

        # Construct Email Message
        msg = EmailMessage()
        msg["Subject"] = mail_subject
        msg["From"] = Config.EMAIL_FROM or Config.EMAIL_USERNAME
        msg["To"] = target_recipient
        msg.set_content(mail_body)

        host = Config.EMAIL_SMTP_HOST
        port = Config.EMAIL_SMTP_PORT
        username = Config.EMAIL_USERNAME
        password = Config.EMAIL_PASSWORD
        use_tls = Config.EMAIL_USE_TLS

        try:
            with smtplib.SMTP(host, port, timeout=10.0) as server:
                if use_tls:
                    server.starttls()

                if username and password:
                    server.login(username, password)

                server.send_message(msg)

            logger.info(f"[EmailService] Email sent successfully to {target_recipient}")
            return {
                "success": True,
                "recipient": target_recipient,
                "subject": mail_subject,
                "error_type": None,
                "error": None
            }

        except smtplib.SMTPAuthenticationError:
            logger.error(f"[EmailService] SMTP authentication failed for user: {username}")
            return {
                "success": False,
                "recipient": target_recipient,
                "subject": mail_subject,
                "error_type": "auth_error",
                "error": "SMTP authentication failed. Please check credentials."
            }

        except (socket.timeout, TimeoutError):
            logger.error(f"[EmailService] Connection timeout reaching SMTP server {host}:{port}")
            return {
                "success": False,
                "recipient": target_recipient,
                "subject": mail_subject,
                "error_type": "timeout",
                "error": "Connection to SMTP server timed out."
            }

        except (smtplib.SMTPConnectError, socket.error, OSError) as e:
            logger.error(f"[EmailService] Network/Connection error connecting to SMTP server {host}:{port} - {e}")
            return {
                "success": False,
                "recipient": target_recipient,
                "subject": mail_subject,
                "error_type": "connection_error",
                "error": "Failed to connect to SMTP server."
            }

        except Exception as e:
            logger.error(f"[EmailService] Error sending email: {e}")
            return {
                "success": False,
                "recipient": target_recipient,
                "subject": mail_subject,
                "error_type": "send_error",
                "error": "Failed to send email."
            }

    @classmethod
    def format_email_response(cls, data: Dict[str, Any]) -> str:
        """Converts structured email result into a clean spoken TTS response."""
        recipient = data.get("recipient", "")
        if data.get("success"):
            return f"Email sent successfully to {recipient}."

        error_type = data.get("error_type")

        if error_type == "missing_config":
            return "Email service is not configured yet."

        if error_type == "invalid_recipient":
            return f"Invalid recipient email address: {recipient}."

        if error_type == "auth_error":
            return "Email authentication failed. Please check your email credentials."

        # Connection error, timeout, or general send error
        return "Unable to connect to the email server right now."
