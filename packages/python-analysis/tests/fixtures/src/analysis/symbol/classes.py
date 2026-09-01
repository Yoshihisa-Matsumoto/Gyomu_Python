class Base:
    def __init__(self, base_value: int) -> None:
        self.base_value = base_value


class Simple:
    def __init__(
        self,
        name: str,
        age: int = 0,
    ) -> None:
        self.name = name
        self.age = age
        self.position = 0

    position: int

    def get_name(self) -> str:
        return self.name


class NoInit:
    value: int = 10


class Inherited(Base):
    pass


class Complex:
    def __init__(
        self,
        positional_only: str,
        /,
        positional_or_keyword: int,
        *args: str,
        keyword_only: bool = False,
        **kwargs: object,
    ) -> None:
        self.positional_only = positional_only
        self.positional_or_keyword = positional_or_keyword
        self.args = args
        self.keyword_only = keyword_only
        self.kwargs = kwargs

    @classmethod
    def from_value(
        cls,
        value: str,
    ) -> "Complex":
        return cls(value, 1)

    @staticmethod
    def create(
        name: str,
    ) -> "Complex":
        return Complex(name, 1)


class Nested:
    def __init__(self, value: int) -> None:
        self.parent_value = value

    class Inner:
        def __init__(self, value: int) -> None:
            self.child_value = value

        class InnerMost:
            def __init__(self, value: int) -> None:
                self.grandchild_value = value
