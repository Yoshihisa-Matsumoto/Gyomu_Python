def list_comprehension(values: list[int]) -> list[int]:
    return [value * 2 for value in values]


def list_comprehension_with_if(values: list[int]) -> list[int]:
    return [value * 2 for value in values if value > 0]


def list_comprehension_multiple_for(
    values: list[list[int]],
) -> list[int]:
    return [value for items in values for value in items]


def set_comprehension(values: list[int]) -> set[int]:
    return {value * 2 for value in values}


def set_comprehension_with_if(values: list[int]) -> set[int]:
    return {value * 2 for value in values if value > 0}


def dict_comprehension(values: list[int]) -> dict[int, int]:
    return {value: value * 2 for value in values}


def dict_comprehension_with_if(values: list[int]) -> dict[int, int]:
    return {value: value * 2 for value in values if value > 0}


def generator_expression(values: list[int]):
    return (value * 2 for value in values)


def generator_expression_with_if(values: list[int]):
    return (value * 2 for value in values if value > 0)


def nested_comprehension(values: list[list[int]]) -> list[int]:
    return [value * 2 for items in values for value in items if value > 0]
