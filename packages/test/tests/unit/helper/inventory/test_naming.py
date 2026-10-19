import pytest
from gyomu_test.helper.inventory.naming import (
    _build_class_name_from_helper_name,
    _build_helper_name_from_class_name,
)


class Test_BuildHelperFunctionName:
    @pytest.mark.parametrize(
        ("class_name", "expected"),
        [
            ("SymbolAnalysis", "create_symbol_analysis"),
            ("ClassAnalysis", "create_class_analysis"),
            ("BaseModel", "create_base_model"),
            ("HttpResponse", "create_http_response"),
            ("XmlParser", "create_xml_parser"),
            ("Symbol", "create_symbol"),
            ("_Symbol", "create__symbol"),
        ],
    )
    def test_build_helper_function_name(
        self,
        class_name: str,
        expected: str,
    ) -> None:
        assert _build_helper_name_from_class_name(class_name) == expected
        assert _build_class_name_from_helper_name(expected) == class_name
