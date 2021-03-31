from gyomu.json import Json
from enum import Enum
from email.message import EmailMessage

class _User:
    name = ""

    def __init__(self, name):
        self.name = name

    def printName(self):
        print("Name = " + self.name)

    def __eq__(self, other):
        return self.name == other.name

class _Programmer(_User):
    job = "Programmer"

    def __init__(self, name):
        super().__init__(name)

    #       self.job = "Programmer"

    def doPython(self):
        print("Programming Python")

    def __eq__(self, other):
        return super().__eq__(other) and self.job == other.job

class _Color(Enum):
    RED = 1,
    GREEN = 2,
    BLUE = 3


class _ColorStr(Enum):
    RED = "red",
    GREEN = "green"
    BLUE = "blue"


def test_to_json():
    brian = _User("Brian")
    brian_str = Json.to_json(brian)

    brian2 = Json.deserialize(brian_str,_User)
    assert brian.name == brian2.name
    assert brian == brian2
    #"{\"py/object\": \"tests.test_json._User\", \"name\": \"Brian\"}"  #
    diana = _Programmer("Dianna")
    diana_str= Json.to_json(diana)
    diana2 = Json.deserialize(diana_str, _Programmer)
    assert diana.job==diana2.job and diana.name == diana2.name
    #"{\"py/object\": \"tests.test_json._Programmer\", \"name\": \"Dianna\"}" #
    diana.job = "Test"
    diana_str = Json.to_json(diana)
    diana2 = Json.deserialize(diana_str, _Programmer)
    assert diana.job == diana2.job and diana.name == diana2.name
    blue = _Color.BLUE
    bluestr = Json.to_json(blue)
    blue2 = Json.deserialize(bluestr, _Color)
    assert blue == blue2
    #assert bluestr == "{\"py/reduce\": [{\"py/type\": \"tests.test_json._Color\"}, {\"py/tuple\": [3]}]}"
    red = _ColorStr.RED
    redstr = Json.to_json(red)
    red2 = Json.deserialize(redstr, _ColorStr)
    assert red == red2

# def test_email_json():
#     email = EmailMessage()
#     email['Subject'] = "test subject"
#     email['From'] = 'test@test.com'
#     email['To'] = 'recipient@tt.com, recipient2@tt.aa'
#     email.set_content('body', subtype='html')
#
#     emailStr = Json.to_json(email, EmailMessage)
#     email2 = Json.deserialize(emailStr, EmailMessage)
#     assert email == email2