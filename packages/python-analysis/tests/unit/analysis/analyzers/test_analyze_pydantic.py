from griffe import Class
from gyomu_python_analysis.analysis.analyzers.cls import analyze_class
from gyomu_python_analysis.analysis.analyzers.context import initialize_symbol_context
from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.types import PythonPath

from tests.helpers import AnalysisTestBase


class TestAnalyzePydantic(AnalysisTestBase):
    def _analyze_file(self, file_name: str, class_name: str) -> ClassAnalysis:
        module_name = PythonPath(f"analysis.symbol.{file_name}")
        context = self._read_module_fixture(module_name)
        module = context.source.module
        cls = module[class_name]

        assert isinstance(cls, Class)
        print(cls.as_dict())
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
            name=class_name,
            source_lines=source_lines,
            context=initialize_symbol_context(
                module_name=module_name,
                name=class_name,
            ),
        )
        return result

    def test_description(self) -> None:
        result = self._analyze_file("pydantic", "FieldDescriptionModel")
        assert result.name == "FieldDescriptionModel"

        assert result.variables[0] and result.variables[0].pydantic
        assert result.variables[0].name == "value"

        pydantic = result.variables[0].pydantic
        assert pydantic.required is True
        assert pydantic.description == "Primary identifier"
        assert pydantic.alias is None
        assert pydantic.default_source is None

    def test_alias(self) -> None:
        result = self._analyze_file("pydantic", "FieldAliasModel")
        assert result.name == "FieldAliasModel"

        assert result.variables[0] and result.variables[0].pydantic
        assert result.variables[0].name == "value"

        pydantic = result.variables[0].pydantic
        assert pydantic.required is True
        assert pydantic.description is None
        assert pydantic.alias == "user_id"
        assert pydantic.default_source is None

    def test_description_and_alias(self) -> None:
        result = self._analyze_file("pydantic", "FieldDescriptionAndAliasModel")
        assert result.name == "FieldDescriptionAndAliasModel"

        assert result.variables[0] and result.variables[0].pydantic
        assert result.variables[0].name == "value"

        pydantic = result.variables[0].pydantic
        assert pydantic.required is True
        assert pydantic.description == "Primary identifier"
        assert pydantic.alias == "user_id"
        assert pydantic.default_source is None

    def test_default(self) -> None:
        result = self._analyze_file("pydantic", "FieldDefaultModel")
        assert result.name == "FieldDefaultModel"

        assert result.variables[0] and result.variables[0].pydantic
        assert result.variables[0].name == "value"

        pydantic = result.variables[0].pydantic
        assert pydantic.required is True
        assert pydantic.description is None
        assert pydantic.alias is None
        assert pydantic.default_source == "0"

    def test_empty_field(self) -> None:
        result = self._analyze_file("pydantic", "FieldEmptyModel")
        assert result.name == "FieldEmptyModel"

        assert result.variables[0] and result.variables[0].pydantic
        assert result.variables[0].name == "value"

        pydantic = result.variables[0].pydantic
        assert pydantic.required is True
        assert pydantic.description is None
        assert pydantic.alias is None
        assert pydantic.default_source is None

    def test_optional(self) -> None:
        result = self._analyze_file("pydantic", "FieldOptionalModel")
        assert result.name == "FieldOptionalModel"

        assert result.variables[0] and result.variables[0].pydantic
        assert result.variables[0].name == "value"

        pydantic = result.variables[0].pydantic
        assert pydantic.required is False
        assert pydantic.description == "Optional value"
        assert pydantic.alias is None
        assert pydantic.default_source is None

    def test_non_field(self) -> None:
        result = self._analyze_file("pydantic", "NonFieldModel")
        assert result.name == "NonFieldModel"

        assert result.variables[0] is not None
        assert result.variables[0].name == "value"
        assert result.variables[0].pydantic is None
