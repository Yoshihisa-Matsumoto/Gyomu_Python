def simple_match(value: int) -> str:
    match value:
        case 0:
            return "zero"
        case 1:
            return "one"
        case _:
            return "other"


def match_with_guard(value: int) -> str:
    match value:
        case number if number > 0:
            return "positive"
        case number if number < 0:
            return "negative"
        case _:
            return "zero"


def match_with_or_pattern(value: int) -> str:
    match value:
        case 0 | 1:
            return "small"
        case 2 | 3:
            return "medium"
        case _:
            return "large"


def match_sequence(value: list[int]) -> str:
    match value:
        case []:
            return "empty"
        case [first]:
            return f"one: {first}"
        case [first, second]:
            return f"two: {first}, {second}"
        case _:
            return "many"


def match_mapping(value: dict[str, int]) -> str:
    match value:
        case {"name": name, "age": age}:
            return f"{name}: {age}"
        case {"name": name}:
            return str(name)
        case _:
            return "unknown"


def match_class(value: object) -> str:
    match value:
        case int(number):
            return f"int: {number}"
        case str(text):
            return f"str: {text}"
        case _:
            return "other"
