def outer() -> None:
    def inner(value: int) -> str:
        return str(value)

    result = inner(10)


def outer_with_multiple_functions(value: int) -> int:
    def add(left: int, right: int) -> int:
        return left + right

    def multiply(left: int, right: int) -> int:
        return left * right

    return add(value, 2) + multiply(value, 3)


def outer_with_async_function() -> None:
    async def inner(value: int) -> str:
        return str(value)

    result = inner(10)
