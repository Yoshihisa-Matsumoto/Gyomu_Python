import pytest
from gyomu.email_sender import EmailSender, EmailBuilder, EmailMessage
from gyomu.json import Json

class FileEmailSender(EmailSender):
    _temp_directory: dir = None

    def __init__(self, temp_directory):
        self._temp_directory = temp_directory

    def send(self,msg: EmailMessage):
        a_file = self._temp_directory.join('mail_test.txt')
        a_file.write(Json.to_json(msg))

@pytest.fixture()
def register_file_mail_sender(tmpdir):
    EmailBuilder.register_mail_sender(FileEmailSender(tmpdir))