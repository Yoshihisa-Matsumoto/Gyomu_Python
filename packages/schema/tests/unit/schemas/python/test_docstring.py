from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.helpers import (
    create_custom_section,
    create_docstring,
    create_example_section,
    create_gyomu_context_section,
    create_note_section,
    create_parameter_section,
    create_parameter_section_item,
    create_raise_section,
    create_raise_section_item,
    create_return_section,
)


class TestDocstringAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            DocstringAnalysis,
            create_docstring(
                sections=(
                    create_parameter_section(
                        items=(
                            create_parameter_section_item(
                                name="arg1", description="ABCDE#", type="int | ABC"
                            ),
                        )
                    ),
                    create_return_section(type=None, description="ABC#DFD"),
                    create_raise_section(
                        items=(
                            create_raise_section_item(
                                type="ValueException", description="ABCD##"
                            ),
                        )
                    ),
                    create_example_section(values=tuple(["ABC#,", "BCD#"])),
                    create_note_section(value="Note"),
                    create_gyomu_context_section(value="Gyomu"),
                    create_custom_section(title="title1", value="Custom1"),
                )
            ),
        )
