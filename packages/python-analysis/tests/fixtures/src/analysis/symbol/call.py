def call_simple():
    return foo()


def call_with_positional_argument():
    return foo(1)


def call_with_multiple_positional_arguments():
    return foo(1, "value", bar)


def call_with_keyword_argument():
    return foo(name="value")


def call_with_multiple_keyword_arguments():
    return foo(name="value", mode="before")


def call_with_mixed_arguments():
    return foo("name", mode="before")


def call_with_nested_call():
    return foo(bar(value))


def call_with_keyword_call_value():
    return foo(value=bar())
