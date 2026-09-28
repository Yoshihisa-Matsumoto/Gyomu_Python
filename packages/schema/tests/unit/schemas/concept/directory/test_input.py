from pathlib import Path

from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.concept.directory.input import DirectoryConceptInput
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.concept_helpers import (
    create_dependency_summary,
    create_directory_concept,
    create_directory_concept_input,
    create_file_summary,
    create_public_declaration_summary,
    create_sub_directory_input,
)


class TestDirectoryConceptInput:
    def test(self) -> None:
        _assert_json_round_trip(
            DirectoryConceptInput,
            create_directory_concept_input(
                files=tuple(
                    [
                        create_file_summary(
                            path=ProjectRelativePath(Path("test/temp.py")),
                            exports=tuple(
                                [
                                    create_public_declaration_summary(
                                        symbol="test",
                                        kind=DeclarationKind.VARIABLE,
                                        summary="test",
                                    )
                                ]
                            ),
                            # re_exports=tuple(
                            #     [
                            #         create_re_exports_summary(
                            #             export_all=True, module="test_module"
                            #         )
                            #     ]
                            # ),
                            dependencies=tuple(
                                [
                                    create_dependency_summary(
                                        target="test", external=False
                                    )
                                ]
                            ),
                        )
                    ]
                ),
                sub_directories=tuple(
                    [
                        create_sub_directory_input(
                            path=Path("sub"),
                            concept=create_directory_concept(
                                summary="test",
                                responsibilities=(["test"]),
                                concepts=(["test"]),
                                relationships=(["test"]),
                                design_decisions=(["test"]),
                                importance=DirectoryImportance.CORE,
                            ),
                        )
                    ]
                ),
            ),
        )
