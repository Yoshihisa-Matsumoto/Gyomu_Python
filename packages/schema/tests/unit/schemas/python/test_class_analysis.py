from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.helpers import (
    create_class_analysis,
    create_class_type_alias_analysis,
    create_class_variable_analysis,
    create_declaration_identity,
    create_inner_class_analysis,
    create_location,
    create_method_analysis,
)


class TestClassAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            ClassAnalysis,
            create_class_analysis(
                0,
                create_location(),
                "test1",
                create_declaration_identity("id1"),
                methods=(
                    create_method_analysis(
                        indent=4,
                        location=create_location(),
                        identity=create_declaration_identity("method1"),
                    ),
                ),
                variables=(
                    create_class_variable_analysis(
                        indent=4,
                        location=create_location(),
                        name="test_var1",
                        identity=create_declaration_identity("id3"),
                    ),
                ),
                type_aliases=(
                    create_class_type_alias_analysis(
                        indent=4,
                        location=create_location(),
                        name="test_alias1",
                        identity=create_declaration_identity("id4"),
                    ),
                ),
                inner_classes=(
                    create_inner_class_analysis(
                        indent=4,
                        location=create_location(),
                        name="inner1",
                        identity=create_declaration_identity("id5"),
                        methods=(
                            create_method_analysis(
                                indent=4,
                                location=create_location(),
                                identity=create_declaration_identity("method23"),
                            ),
                        ),
                    ),
                ),
            ),
        )
