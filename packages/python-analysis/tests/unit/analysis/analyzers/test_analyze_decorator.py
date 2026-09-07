from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.decorator import DecoratorAnalysis, DecoratorArgument
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.type.structure import (
    EllipsisStructureAnalysis,
    LiteralValue,
    NameStructureAnalysis,
)
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.python.variable import VariableAnalysis

from tests.helpers import AnalysisTestBase


class TestAnalyzeDecorator(AnalysisTestBase):
    def _analyze_function(self, name: str) -> FunctionAnalysis:
        return self._analyze_function_base(
            PythonPath("analysis.symbol.decorator"), name
        )

    def _analyze_class(self, name: str) -> ClassAnalysis:
        return self._analyze_class_base(PythonPath("analysis.symbol.decorator"), name)

    def _analyze_variable(self, name: str) -> VariableAnalysis:
        return self._analyze_variable_base(
            PythonPath("analysis.symbol.decorator"), name
        )

    def _analyze_file(self) -> ModuleAnalysis:
        return self._analyze_module_base(PythonPath("analysis.symbol.decorator"))

    def test_class_method(self):
        func = self._analyze_function("class_method")

        assert func.decorators == (
            DecoratorAnalysis(
                name="classmethod",
                arguments=(),
                location=func.decorators[0].location,
            ),
        )

    def test_static_method(self):
        func = self._analyze_function("static_method")

        assert func.decorators == (
            DecoratorAnalysis(
                name="staticmethod",
                arguments=(),
                location=func.decorators[0].location,
            ),
        )

    def test_property(self):
        variable = self._analyze_variable("value")

        assert variable.name == "value"
        assert variable.type
        assert variable.type.structure
        assert isinstance(variable.type.structure, NameStructureAnalysis)
        assert variable.type.structure.name == "str"

    def test_simple(self):
        func = self._analyze_function("simple")

        assert func.decorators == (
            DecoratorAnalysis(
                name="custom_decorator",
                arguments=(),
                location=func.decorators[0].location,
            ),
        )

    def test_decorated_positional(self):
        func = self._analyze_function("decorated_positional")

        assert func.decorators == (
            DecoratorAnalysis(
                name="custom_decorator",
                arguments=(
                    DecoratorArgument(
                        name=None,
                        expression=LiteralValue(value="value"),
                    ),
                ),
                location=func.decorators[0].location,
            ),
        )

    def test_call(self):
        func = self._analyze_function("call")

        assert func.decorators == (
            DecoratorAnalysis(
                name="custom_decorator",
                arguments=(
                    DecoratorArgument(
                        name=None,
                        expression=EllipsisStructureAnalysis(),
                    ),
                ),
                location=func.decorators[0].location,
            ),
        )

    def test_positional(self):
        func = self._analyze_function("positional")

        assert func.decorators == (
            DecoratorAnalysis(
                name="custom_decorator",
                arguments=(
                    DecoratorArgument(
                        name=None,
                        expression=LiteralValue(value="value"),
                    ),
                    DecoratorArgument(
                        name=None,
                        expression=LiteralValue(value=123),
                    ),
                ),
                location=func.decorators[0].location,
            ),
        )

    def test_decorated_keyword(self):
        func = self._analyze_function("decorated_keyword")

        assert func.decorators == (
            DecoratorAnalysis(
                name="custom_decorator",
                arguments=(
                    DecoratorArgument(
                        name="mode",
                        expression=LiteralValue(value="before"),
                    ),
                ),
                location=func.decorators[0].location,
            ),
        )

    def test_mixed(self):
        func = self._analyze_function("mixed")

        assert func.decorators == (
            DecoratorAnalysis(
                name="custom_decorator",
                arguments=(
                    DecoratorArgument(
                        name=None,
                        expression=LiteralValue(value="value"),
                    ),
                    DecoratorArgument(
                        name="mode",
                        expression=LiteralValue(value="before"),
                    ),
                ),
                location=func.decorators[0].location,
            ),
        )

    def test_decorated_multiple_keywords(self):
        func = self._analyze_function("decorated_multiple_keywords")

        assert func.decorators == (
            DecoratorAnalysis(
                name="custom_decorator",
                arguments=(
                    DecoratorArgument(
                        name="name",
                        expression=LiteralValue(value="value"),
                    ),
                    DecoratorArgument(
                        name="mode",
                        expression=LiteralValue(value="before"),
                    ),
                ),
                location=func.decorators[0].location,
            ),
        )

    def test_validate_attribute(self):
        func = self._analyze_function("validate_attribute")

        assert func.decorators == (
            DecoratorAnalysis(
                name="pydantic.field_validator",
                arguments=(),
                location=func.decorators[0].location,
            ),
        )

    def test_validate_name(self):
        func = self._analyze_function("validate_name")

        assert func.decorators == (
            DecoratorAnalysis(
                name="pydantic.field_validator",
                arguments=(
                    DecoratorArgument(
                        name=None,
                        expression=LiteralValue(value="name"),
                    ),
                    DecoratorArgument(
                        name="mode",
                        expression=LiteralValue(value="before"),
                    ),
                ),
                location=func.decorators[0].location,
            ),
        )

    def test_multiple_decorators(self):
        func = self._analyze_function("multiple_decorators")

        assert len(func.decorators) == 2

        assert func.decorators[0].name == "classmethod"
        assert func.decorators[0].arguments == ()

        assert func.decorators[1].name == "custom_decorator"
        assert func.decorators[1].arguments == (
            DecoratorArgument(
                name=None,
                expression=LiteralValue(value="value"),
            ),
            DecoratorArgument(
                name="mode",
                expression=LiteralValue(value="before"),
            ),
        )

    def test_decorated_class(self):
        cls = self._analyze_class("DecoratedClass")
        assert len(cls.decorators) == 1
        assert cls.decorators[0].name == "custom_class_decorator"

    def test_multiple_decorated_class(self):
        cls = self._analyze_class("MultipleDecoratedClass")

        assert len(cls.decorators) == 2
        assert [decorator.name for decorator in cls.decorators] == [
            "first_decorator",
            "second_decorator",
        ]

    def test_class_methods_decorators(self):
        cls = self._analyze_class("ClassWithMethods")

        class_method = next(
            method for method in cls.methods if method.name == "class_method"
        )
        assert len(class_method.decorators) == 1
        assert class_method.decorators[0].name == "classmethod"

        static_method = next(
            method for method in cls.methods if method.name == "static_method"
        )
        assert len(static_method.decorators) == 1
        assert static_method.decorators[0].name == "staticmethod"

    def test_multiple_decorated_method(self):
        cls = self._analyze_class("ClassWithMethods")

        method = next(
            method
            for method in cls.methods
            if method.name == "multiple_decorated_method"
        )

        assert len(method.decorators) == 2
        assert [decorator.name for decorator in method.decorators] == [
            "first_decorator",
            "second_decorator",
        ]

    def test_class_property(self):
        cls = self._analyze_class("ClassWithMethods")

        variable = next(
            variable for variable in cls.variables if variable.name == "value"
        )
        assert variable
