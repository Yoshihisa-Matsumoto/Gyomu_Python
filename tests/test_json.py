from gyomu.json import Json
from enum import Enum


class User:
    name = ""

    def __init__(self, name):
        self.name = name

    def printName(self):
        print("Name = " + self.name)

    def __eq__(self, other):
        return self.name == other.name

class Programmer(User):
    job = "Programmer"

    def __init__(self, name):
        super().__init__(name)

    #       self.job = "Programmer"

    def doPython(self):
        print("Programming Python")

    def __eq__(self, other):
        return super().__eq__(other) and self.job == other.job

class Color(Enum):
    RED = 1,
    GREEN = 2,
    BLUE = 3


class ColorStr(Enum):
    RED = "red",
    GREEN = "green"
    BLUE = "blue"


def test_to_json():
    brian = User("Brian")
    assert Json.to_json(brian) == "{\"py/object\": \"tests.test_json.User\", \"name\": \"Brian\"}"
    diana = Programmer("Dianna")
    assert Json.to_json(diana) == "{\"py/object\": \"tests.test_json.Programmer\", \"name\": \"Dianna\"}"
    diana.job = "Test"
    assert Json.to_json(
        diana) == "{\"py/object\": \"tests.test_json.Programmer\", \"name\": \"Dianna\", \"job\": \"Test\"}"


def test_deserialize():
    brian = User("Brian")
    assert Json.deserialize("{\"py/object\": \"tests.test_json.User\", \"name\": \"Brian\"}") == brian
    diana = Programmer("Dianna")
    assert Json.deserialize("{\"py/object\": \"tests.test_json.Programmer\", \"name\": \"Dianna\"}") == diana

