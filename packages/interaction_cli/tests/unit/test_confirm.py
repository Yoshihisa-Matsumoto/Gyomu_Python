from io import StringIO
from unittest.mock import Mock

import pytest
from gyomu_interaction_cli.confirm import confirm_or_cancel


class TestConfirmOrCancel:
    @pytest.mark.parametrize("command", ["y", "Y", " y ", "Y "])
    def test_returns_true_when_confirmed(self, command: str) -> None:
        input_func = Mock(side_effect=[command])
        output = StringIO()

        result = confirm_or_cancel(input_func=input_func, output=output)

        assert result is True
        assert input_func.call_count == 1
        assert output.getvalue() == ""

    @pytest.mark.parametrize("command", ["n", "N", " n ", "N "])
    def test_returns_false_when_cancelled(self, command: str) -> None:
        input_func = Mock(side_effect=[command])
        output = StringIO()

        result = confirm_or_cancel(input_func=input_func, output=output)

        assert result is False
        assert input_func.call_count == 1
        assert output.getvalue() == ""

    def test_retries_after_invalid_command(self) -> None:
        input_func = Mock(side_effect=["invalid", "y"])
        output = StringIO()

        result = confirm_or_cancel(input_func=input_func, output=output)

        assert result is True
        assert input_func.call_count == 2
        assert output.getvalue() == "Please enter 'y' to confirm or 'n' to cancel.\n"

    @pytest.mark.parametrize(
        "exception",
        [EOFError(), KeyboardInterrupt()],
    )
    def test_returns_false_when_input_is_interrupted(
        self,
        exception: EOFError | KeyboardInterrupt,
    ) -> None:
        input_func = Mock(side_effect=[exception])
        output = StringIO()

        result = confirm_or_cancel(input_func=input_func, output=output)

        assert result is False
        assert input_func.call_count == 1
        assert output.getvalue() == ""
