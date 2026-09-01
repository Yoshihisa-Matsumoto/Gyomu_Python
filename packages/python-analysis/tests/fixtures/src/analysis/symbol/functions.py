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
