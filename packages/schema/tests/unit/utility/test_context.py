from gyomu_schema.utility.context import caller_context


def test_caller_context_returns_caller() -> None:
    def call_caller_context() -> str:
        return caller_context()

    assert call_caller_context() == f"{__name__}.call_caller_context"
