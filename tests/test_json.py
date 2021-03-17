from gyomu.json import Json
from enum import Enum


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
    assert Json.to_json(brian) == "{\"py/object\": \"tests.test_json._User\", \"name\": \"Brian\"}"
    diana = _Programmer("Dianna")
    assert Json.to_json(diana) == "{\"py/object\": \"tests.test_json._Programmer\", \"name\": \"Dianna\"}"
    diana.job = "Test"
    assert Json.to_json(
        diana) == "{\"py/object\": \"tests.test_json._Programmer\", \"name\": \"Dianna\", \"job\": \"Test\"}"
    blue = _Color.BLUE
    bluestr = Json.to_json(blue)
    assert bluestr == "{\"py/reduce\": [{\"py/type\": \"tests.test_json._Color\"}, {\"py/tuple\": [3]}]}"
    red = _ColorStr.RED
    redstr = Json.to_json(red)
    assert Json.deserialize(redstr) == _ColorStr.RED

def test_deserialize():
    brian = _User("Brian")
    assert Json.deserialize("{\"py/object\": \"tests.test_json._User\", \"name\": \"Brian\"}") == brian
    diana = _Programmer("Dianna")
    assert Json.deserialize("{\"py/object\": \"tests.test_json._Programmer\", \"name\": \"Dianna\"}") == diana
    assert _Color.BLUE == Json.deserialize("{\"py/reduce\": [{\"py/type\": \"tests.test_json._Color\"}, {\"py/tuple\": [3]}]}")
