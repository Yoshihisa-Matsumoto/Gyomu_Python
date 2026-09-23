import inspect


def caller_context() -> str:
    """Retrieves the module and function name of the caller using frame inspection.

    Returns:
        str: The fully qualified name of the caller function in the format
            'module.function'.
    """
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        return "<unknown>"

    caller = frame.f_back
    module = caller.f_globals.get("__name__", "<unknown>")
    function = caller.f_code.co_name

    return f"{module}.{function}"
