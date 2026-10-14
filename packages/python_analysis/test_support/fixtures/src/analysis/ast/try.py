def simple_try(value: int) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


def try_except_as(value: str) -> int:
    try:
        return int(value)
    except ValueError as error:
        return 0


def try_multiple_except(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0
    except TypeError:
        return -1


def try_except_else(value: str) -> int:
    try:
        result = int(value)
    except ValueError:
        return 0
    else:
        return result


def try_except_finally(value: str) -> int:
    try:
        result = int(value)
    except ValueError:
        result = 0
    finally:
        result += 1 

    return result
