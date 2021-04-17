from email.message import EmailMessage
from smtplib import SMTP
from abc import ABCMeta, abstractmethod
import os


class EmailSender(metaclass=ABCMeta):
    @abstractmethod
    def send(self, msg: EmailMessage):
        pass


class SimpleEmailSender(EmailSender):
    SMTP_SERVER_PORT: str = "SMTP_SERVER_PORT"

    @classmethod
    def send(cls, msg: EmailMessage):
        server_port = os.environ[cls.SMTP_SERVER_PORT]
        servers = server_port.split(':')
        with SMTP(servers[0], int(servers[1])) as s:
            s.send_messagatsuogae(msg)


class EmailBuilder:
    _registered_email_sender: EmailSender = None

    @classmethod
    def send_html_message(cls, from_address: str, subject: str, to_address: list[str] = None,
                          cc_address: list[str] = None,
                          body: str = None, attachment_files: list[str] = None) -> EmailMessage:
        email = EmailMessage()
        email['Subject'] = subject
        email['From'] = from_address
        if to_address is not None and len(to_address) > 0:
            email['To'] = ','.join(to_address)
        if cc_address is not None and len(cc_address) > 0:
            email['Cc'] = ','.join(to_address)

        if body is not None:
            email.set_content(body, subtype='html')

        if attachment_files is not None and len(attachment_files) > 1:
            for filepath in attachment_files:
                mime_type = cls.__get_mime_type(filepath)
                with open(filepath, 'rb') as content_file:
                    content = content_file.read()
                    email.add_attachment(content,
                                         maintype=mime_type['maintype'], subtype=mime_type['subtype'],
                                         filename=filepath)

        if cls._registered_email_sender is None:
            SimpleEmailSender().send(email)
        else:
            cls._registered_email_sender.send(email)

        return email

    @classmethod
    def register_mail_sender(cls, custom_mail_sender: EmailSender):
        cls._registered_email_sender = custom_mail_sender

    @classmethod
    def __get_mime_type(cls, path: str) -> dict:
        if path == '':
            return None
        parts = path.split('.')
        if len(parts) < 2:
            return None

        extension = parts[len(parts) - 1]

        applications = ['zip', 'pdf']
        texts = ['txt']
        images = ['png', 'jpeg', 'gif']

        if extension in applications:
            return dict(maintype='application', subtype=extension)
        elif extension in images:
            return dict(maintype='image', subtype=extension)
        elif extension == 'jpg':
            return dict(maintype='image', subtype='jpeg')
        elif extension == 'html':
            return dict(maintype='text', subtype='html')
        elif extension in texts:
            return dict(maintype='text', subtype='plain')
        else:
            return dict(maintype='application', subtype='octet-stream')
