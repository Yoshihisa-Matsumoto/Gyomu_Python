import pytest
from gyomu.email_sender import EmailBuilder

def test_send_html_message(register_file_mail_sender):
    EmailBuilder.send_html_message("sender@address.com","Test Subject",
                                   ["test_to@test.com"],["test_cc1@test.com","test_cc2@test.com"],
                                   "test body")
