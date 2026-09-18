def divide(a: int, b: int) -> float:
    """Divide two numbers.

    Args:
        a (int): The dividend.
        b (int): The divisor.

    Returns:
        float: The quotient.

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("b must not be zero")
    return a / b
