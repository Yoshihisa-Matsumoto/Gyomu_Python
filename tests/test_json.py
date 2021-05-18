from gyomu.json import Json
from enum import Enum
from email.message import EmailMessage
from collections import namedtuple

SimpleTuple = namedtuple('SimpleTuple', ['arg1', 'arg2'])

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
#     #emailStr = Json.to_json_pickle(email)
#     emailStr = Json.to_json(email)
#     print(emailStr)
#     #email2 = Json.deserialize_pickle(emailStr)
#     email2 = Json.deserialize(emailStr, EmailMessage)
#     assert email.as_string() == email2.as_string()

def test_int_type():
    value1: int = 234
    value1_str: str = Json.to_json(value1)
    value2 = Json.deserialize(value1_str,int)
    print(value1_str)
    assert value1 == value2

def test_bool_type():
    value1: bool = True
    value1_str: str = Json.to_json(value1)
    value2 = Json.deserialize(value1_str,bool)
    print(value1_str)
    assert value1 == value2

def test_str_type():
    value1: str = 'Hello World'
    value1_str: str = Json.to_json(value1)
    value2 = Json.deserialize(value1_str,str)
    print(value1_str)
    assert value1 == value2

def test_array_type():
    value1: list = [234,True,'Hello World']
    value1_str: str = Json.to_json(value1)
    value2 = Json.deserialize(value1_str,list)
    print(value1_str)
    assert value1 == value2

def test_dict_type():
    value1: dict = {"Key1":"Value1","Key2":"Value2","Abc":"Def"}
    value1_str: str = Json.to_json(value1)
    value2 = Json.deserialize(value1_str, dict)
    print(value1_str)
    assert value1 == value2

def test_complicated_dict_type():
    value1: dict = {234:234, True:True, "Hello":"Key", "array":[234,True,'Hello World'] }
    value1_str: str = Json.to_json(value1)
    value2 = Json.deserialize(value1_str,dict)
    print(value1_str)

def test_tuple():
    value1: SimpleTuple = SimpleTuple(arg1=234, arg2=234)
    value1_str: str = Json.to_json(value1)
    value2 = Json.deserialize(value1_str, SimpleTuple)
    print(value1_str)
    assert value1 == value2

    value1: SimpleTuple = SimpleTuple(arg1=True, arg2=True)
    value1_str: str = Json.to_json(value1)
    value2 = Json.deserialize(value1_str, SimpleTuple)
    print(value1_str)
    assert value1 == value2

    value1: SimpleTuple = SimpleTuple(arg1="Hello", arg2="World")
    value1_str: str = Json.to_json(value1)
    value2 = Json.deserialize(value1_str, SimpleTuple)
    print(value1_str)
    assert value1 == value2

    value1: SimpleTuple = SimpleTuple(arg1=[234,True,'Hello World'], arg2={"Key1":"Value1","Key2":"Value2","Abc":"Def"})
    value1_str: str = Json.to_json(value1)
    value2 = Json.deserialize(value1_str, SimpleTuple)
    print(value1_str)
    assert value1 == value2

# def test_complicated_tuple():
#     brian = _User("Brian")
#     value1: SimpleTuple = SimpleTuple(arg1=234, arg2=brian)
#     value1_str: str = Json.to_json(value1)
#     value2 = Json.deserialize(value1_str, SimpleTuple)
#     print(value1_str)
#     assert value1 == value2