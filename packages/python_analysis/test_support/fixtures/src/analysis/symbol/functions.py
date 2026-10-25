from dataclasses import dataclass


def greet(
    name: str,
    count: int = 1,
) -> str:
    return name


def parameters(
    positional_only,
    /,
    positional_or_keyword,
    *var_positional,
    keyword_only,
    **var_keyword,
) -> None:
    pass


async def test_async() -> str:
    return "a"

async def abstract()->str:...

@dataclass
class User:
    id: str

def create_user(id:str ="23AB")-> User:
    return User(id=id)

def build_default_user(user:User=create_user(id="345D"))->User:
    return user

def build_default_parameter(param1:str|None=None,param2:str|None="None")->bool:
    return param1==param2
