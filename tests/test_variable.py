from datetime import date
import pytest
from gyomu.variable import VariableTranslator
from gyomu.holidays import MarketDateAccess
from collections import namedtuple
from pytest_mock import mocker

VariableResult = namedtuple('VariableResult', ['target_date', 'parameter', 'output'])

@pytest.fixture()
def mock_variables(mocker):
    mocker.patch.object(VariableTranslator, '_VariableTranslator__get_supported_market', return_value=['JP'])
    yield

class TestVariableTranslator:

    @pytest.mark.parametrize('input_data',
                             {
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$TODAY$yyyyMMdd%}',
                                            output='19840502'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$TODAY$%Y%m%d%}',
                                                output='19840502'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$NEXTBUS$%Y%m%d%}',
                                                output='19840507'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$PREVBUS$%Y%m%d%}',
                                                output='19840427'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$BBOM$%Y%m%d%}',
                                                output='19840502'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$BBOY$%Y%m%d%}',
                                                output='19840104'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$BOM$%Y%m%d%}',
                                                output='19840502'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$BOY$%Y%m%d%}',
                                                output='19840102'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$BEOM$%Y%m%d%}',
                                                output='19840530'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$BEOY$%Y%m%d%}',
                                                output='19841228'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$EOM$%Y%m%d%}',
                                                output='19840530'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$EOY$%Y%m%d%}',
                                                output='19841230'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$NEXTBBOM$%Y%m%d%}',
                                                output='19840604'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$NEXTBUS$%Y%m%d%}',
                                                output='19840507'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$NEXTDAY$%Y%m%d%}',
                                                output='19840504'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$NEXTBEOM$%Y%m%d%}',
                                                output='19840628'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$PREVBUS$%Y%m%d%}',
                                                output='19840427'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$PREVDAY$%Y%m%d%}',
                                                output='19840430'),
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$PREVBEOM$%Y%m%d%}',
                                                output='19840426'),
                             })
    def test_parse(self, mock_holiday,mock_variables,input_data):
        parameter = input_data.parameter
        market_access = MarketDateAccess('JP')
        translator = VariableTranslator(market_access)
        assert input_data.output == translator.parse(parameter,input_data.target_date)

    @pytest.mark.parametrize('input_data',
                             {
                                 VariableResult(target_date=date(1984, 5, 2), parameter='{%JP$2$PREVBEOM$%}',
                                                output=date(1984,4,26))
                             })
    def test_parse_date(self, mock_holiday,mock_variables,input_data):
        parameter = input_data.parameter
        market_access = MarketDateAccess('JP')
        translator = VariableTranslator(market_access)
        assert input_data.output == translator.parse_date(parameter, input_data.target_date)
