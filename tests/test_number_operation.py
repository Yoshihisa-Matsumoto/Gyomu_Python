import pytest
import decimal
from collections import namedtuple
from gyomu.number_operation import to_half_adjust

RoundResult = namedtuple('RoundResult', ['input_value', 'input_digit', 'output_value'])


@pytest.mark.parametrize('input_data',
                         {
                            RoundResult(input_value='123.4567', input_digit='2', output_value='100'),
                            RoundResult(input_value='153.4567', input_digit='2', output_value='200'),
                             RoundResult(input_value='23.4567', input_digit='1', output_value='20'),
                             RoundResult(input_value='23.4567', input_digit='-1', output_value='23'),
                             RoundResult(input_value='23.4567', input_digit='-2', output_value='23.5'),
                             RoundResult(input_value='23.4567', input_digit='-3', output_value='23.46'),
                         })
def test_to_half_adjust(input_data):
    output_result = to_half_adjust(decimal.Decimal(input_data.input_value),int(input_data.input_digit))
    assert decimal.Decimal(input_data.output_value) == output_result


