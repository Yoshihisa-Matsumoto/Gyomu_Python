from gyomu_python_analysis.resolve.path import normalize_reference_name
from gyomu_schema.schemas.python.import_analysis import ImportKind

from packages.schema.test_support.helpers import create_import_analysis


class TestNormalizeReferenceName:
    def test_normalizes_symbol_import_alias(self) -> None:
        imported = (
            create_import_analysis(
                local_name="Alpha",
                imported_name="pydantic.BaseModel",
                kind=ImportKind.SYMBOL,
            ),
        )

        assert normalize_reference_name(imported, "Alpha") == "pydantic.BaseModel"

    def test_normalizes_module_import_alias(self) -> None:
        imported = (
            create_import_analysis(
                local_name="Base",
                imported_name="pydantic",
                kind=ImportKind.MODULE,
            ),
        )

        assert (
            normalize_reference_name(imported, "Base.BaseModel") == "pydantic.BaseModel"
        )

    def test_preserves_suffix_after_symbol_import_alias(self) -> None:
        imported = (
            create_import_analysis(
                local_name="Alpha",
                imported_name="some_module.BaseModel",
                kind=ImportKind.SYMBOL,
            ),
        )

        assert (
            normalize_reference_name(imported, "Alpha.Inner")
            == "some_module.BaseModel.Inner"
        )

    def test_prefers_longest_matching_local_name(self) -> None:
        imported = (
            create_import_analysis(
                local_name="pkg",
                imported_name="package",
                kind=ImportKind.MODULE,
            ),
            create_import_analysis(
                local_name="pkg.sub",
                imported_name="other_module",
                kind=ImportKind.MODULE,
            ),
        )

        assert (
            normalize_reference_name(imported, "pkg.sub.Model") == "other_module.Model"
        )

    def test_returns_reference_unchanged_when_no_imports(self) -> None:
        assert normalize_reference_name((), "MyClass") == "MyClass"

    def test_returns_reference_unchanged_when_import_does_not_match(self) -> None:
        imported = (
            create_import_analysis(
                local_name="Alpha",
                imported_name="pydantic.BaseModel",
                kind=ImportKind.SYMBOL,
            ),
        )

        assert normalize_reference_name(imported, "Beta") == "Beta"

    def test_does_not_match_partial_identifier(self) -> None:
        imported = (
            create_import_analysis(
                local_name="Base",
                imported_name="pydantic",
                kind=ImportKind.MODULE,
            ),
        )

        assert normalize_reference_name(imported, "BaseModel") == "BaseModel"

    def test_preserves_generic_type_expression(self) -> None:
        imported = (
            create_import_analysis(
                local_name="list",
                imported_name="custom_list",
                kind=ImportKind.SYMBOL,
            ),
        )

        assert normalize_reference_name(imported, "list[str]") == "list[str]"

    def test_preserves_union_type_expression(self) -> None:
        imported = (
            create_import_analysis(
                local_name="Alpha",
                imported_name="pydantic.BaseModel",
                kind=ImportKind.SYMBOL,
            ),
        )

        assert normalize_reference_name(imported, "Alpha | None") == "Alpha | None"

    def test_normalizes_aliased_module_with_nested_attributes(self) -> None:
        imported = (
            create_import_analysis(
                local_name="Base",
                imported_name="pydantic",
                kind=ImportKind.MODULE,
            ),
        )

        assert (
            normalize_reference_name(imported, "Base.types.BaseModel")
            == "pydantic.types.BaseModel"
        )

    def test_preserves_unaliased_nested_module_import_reference(self) -> None:
        imported = (
            create_import_analysis(
                local_name="package",
                imported_name="package.submodule",
                kind=ImportKind.MODULE,
            ),
        )

        assert (
            normalize_reference_name(imported, "package.submodule.Model")
            == "package.submodule.Model"
        )
