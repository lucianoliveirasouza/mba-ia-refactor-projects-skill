import logging
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)

SMTP_TIMEOUT_SECONDS = 10


class NotificationService:
    """Envia notificações por email. A configuração SMTP é injetada (Settings)."""

    def __init__(self, settings, smtp_factory=smtplib.SMTP):
        self._settings = settings
        self._smtp_factory = smtp_factory

    @property
    def enabled(self):
        return bool(self._settings.SMTP_HOST and self._settings.SMTP_SENDER)

    def send_email(self, to, subject, body):
        if not self.enabled:
            logger.info('Envio de email desabilitado (SMTP_HOST não configurado): %s', subject)
            return False

        message = EmailMessage()
        message['From'] = self._settings.SMTP_SENDER
        message['To'] = to
        message['Subject'] = subject
        message.set_content(body)

        try:
            with self._smtp_factory(self._settings.SMTP_HOST, self._settings.SMTP_PORT,
                                    timeout=SMTP_TIMEOUT_SECONDS) as server:
                server.starttls()
                if self._settings.SMTP_USER:
                    server.login(self._settings.SMTP_USER, self._settings.SMTP_PASSWORD)
                server.send_message(message)
        except (smtplib.SMTPException, OSError):
            logger.exception('Falha ao enviar email: %s', subject)
            return False

        logger.info('Email enviado: %s', subject)
        return True

    def notify_task_assigned(self, user, task):
        subject = f'Nova task atribuída: {task.title}'
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f'Prioridade: {task.priority}\nStatus: {task.status}'
        )
        return self.send_email(user.email, subject, body)
