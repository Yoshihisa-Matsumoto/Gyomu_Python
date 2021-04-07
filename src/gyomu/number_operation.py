from decimal import Decimal, ROUND_HALF_UP


def to_half_adjust(decimal_value: Decimal, digit: int) -> Decimal:
    """
    :param decimal_value: Target decimal value to be rounded as half up
    :param digit: In which digit, you want to round?
        RoundResult(input_value='123.4567', input_digit='2', output_value='100'),
        RoundResult(input_value='23.4567', input_digit='1', output_value='20'),
        RoundResult(input_value='23.4567', input_digit='-1', output_value='23'),
        RoundResult(input_value='23.4567', input_digit='-2', output_value='23.5'),
        RoundResult(input_value='23.4567', input_digit='-3', output_value='23.46')
    decimal.Decimal(input_data.output_value) ==
        to_half_adjust(decimal.Decimal(input_data.input_value),int(input_data.input_digit))
    :return: return rounded value
    """
    if digit == 0:
        digit = 1

    if digit > 0:
        str_value = '1E' + str(digit)
        digit_base = Decimal(str_value)
        return Decimal(str(int(decimal_value.quantize(digit_base, rounding=ROUND_HALF_UP))))
    else:
        base = Decimal(10)
        digit_base = base ** (digit + 1)
        if digit_base == 1:
            digit_base = Decimal(0)
        return decimal_value.quantize(digit_base, rounding=ROUND_HALF_UP)
