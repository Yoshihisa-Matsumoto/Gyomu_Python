@classmethod
def class_method(self) -> None: ...


@staticmethod
def static_method() -> None: ...


@property
def value(self) -> str: ...


@custom_decorator
def simple(self) -> None: ...


@custom_decorator("value")
def decorated_positional():
    pass


@custom_decorator(...)
def call(self) -> None: ...


@custom_decorator("value", 123)
def positional(self) -> None: ...


@custom_decorator(mode="before")
def decorated_keyword():
    pass


@custom_decorator("value", mode="before")
def mixed(self) -> None: ...


@custom_decorator(name="value", mode="before")
def decorated_multiple_keywords():
    pass


@pydantic.field_validator
def validate_attribute(self, value: str) -> str: ...


@pydantic.field_validator("name", mode="before")
def validate_name(self, value: str) -> str: ...


@classmethod
@custom_decorator("value", mode="before")
def multiple_decorators(cls) -> None: ...


@custom_class_decorator
class DecoratedClass:
    pass


@first_decorator
@second_decorator("value")
class MultipleDecoratedClass:
    pass


class ClassWithMethods:
    @classmethod
    def class_method(cls) -> None:
        pass

    @staticmethod
    def static_method() -> None:
        pass

    @first_decorator
    @second_decorator("value")
    def multiple_decorated_method(self) -> None:
        pass

    @property
    def value(self) -> str:
        return "value"
