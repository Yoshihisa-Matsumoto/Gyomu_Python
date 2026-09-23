import inspect


def caller_context() -> str:
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        return "<unknown>"

    caller = frame.f_back
    module = caller.f_globals.get("__name__", "<unknown>")
    function = caller.f_code.co_name

    return f"{module}.{function}"
