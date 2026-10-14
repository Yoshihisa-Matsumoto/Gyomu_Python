def simple_if(value: int) -> str:
    if value > 0:
        return "positive"
    return "non-positive"


def if_else(value: int) -> str:
    if value > 0:
        return "positive"
    else:
        return "non-positive"


def if_elif_else(value: int) -> str:
    if value > 0:
        return "positive"
    elif value == 0:
        return "zero"
    else:
        return "negative"


def nested_if(value: int, threshold: int) -> str:
    if value > 0:
        if value >= threshold:
            return "large"
        else:
            return "small"
    return "non-positive"


def if_with_multiple_statements(value: int) -> int:
    result = 0

    if value > 0:
        result = value
        result += 1
        return result

    return result
