from griffe import Attribute, Class, Function
from gyomu_python_analysis.analysis.analyzers.cls import analyze_class
from gyomu_python_analysis.analysis.analyzers.context import initialize_symbol_context
from gyomu_python_analysis.analysis.analyzers.functions import analyze_function
from gyomu_python_analysis.analysis.analyzers.variables import analyze_variable
from gyomu_python_analysis.analysis.load_module_analysis import load_module_analysis
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
from returns.result import Failure

from tests.helpers import AnalysisTestBase


class TestAnalyzeDecorator(AnalysisTestBase):
    def _analyze_function(self, name: str) -> FunctionAnalysis:
        module_name = PythonPath("analysis.symbol.decorator")
        context = self._read_module_fixture(module_name)
        module = context.source.module
        func = module[name]

        assert isinstance(func, Function)

        print(func.decorators)

        source_full_path = (
            context.project.project_root
            / context.project.source_root
            / context.source.path
        )
        source_lines = source_full_path.read_text(
            encoding="utf-8",
        ).splitlines()
        result = analyze_function(
            func=func,
            name=name,
            source_lines=source_lines,
            context=initialize_symbol_context(
                imports=tuple(),
                module_name=module_name,
                name=name,
            ),
        )
        return result

    def _analyze_class(self, name: str) -> ClassAnalysis:
        module_name = PythonPath("analysis.symbol.decorator")
        context = self._read_module_fixture(module_name)
        module = context.source.module
        cls = module[name]

        assert isinstance(cls, Class)

        print(cls.decorators)

        source_full_path = (
            context.project.project_root
            / context.project.source_root
            / context.source.path
        )
        source_lines = source_full_path.read_text(
            encoding="utf-8",
        ).splitlines()
        result = analyze_class(
            cls=cls,
            name=name,
            source_lines=source_lines,
            context=initialize_symbol_context(
                imports=tuple(),
                module_name=module_name,
                name=name,
            ),
        )
        return result

    def _analyze_variable(self, name: str) -> VariableAnalysis:
        module_name = PythonPath("analysis.symbol.decorator")
        context = self._read_module_fixture(module_name)
        module = context.source.module
        variable = module[name]

        assert isinstance(variable, Attribute)

        source_full_path = (
            context.project.project_root
            / context.project.source_root
            / context.source.path
        )
        source_lines = source_full_path.read_text(
            encoding="utf-8",
        ).splitlines()
        result = analyze_variable(
            variable=variable,
            name=name,
            source_lines=source_lines,
            context=initialize_symbol_context(
                imports=tuple(),
                module_name=module_name,
                name=name,
            ),
        )
        return result

    def _analyze_file(self) -> ModuleAnalysis:
        module_path = PythonPath("analysis.symbol.decorator")
        context = self._read_module_fixture(module_path)
        result = load_module_analysis(context.project, module_path)
        if isinstance(result, Failure):
            raise result.failure()

        return result.unwrap()

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
