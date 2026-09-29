from pathlib import Path

from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.concept_helpers import (
    create_dependency_analysis,
    create_dependency_summary,
    create_directory_analysis,
    create_directory_analysis_fact,
    create_directory_concept,
    create_file_summary,
    create_package_analysis,
    create_public_declaration_summary,
    create_pyproject_analysis,
)


class TestPackageAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            PackageAnalysis,
            create_package_analysis(
                package=create_pyproject_analysis(),
                dependencies=tuple([create_dependency_analysis()]),
                directories=tuple(
                    [
                        create_directory_analysis(
                            path=ProjectRelativePath(Path("src")),
                            concept=create_directory_concept(),
                            fact=create_directory_analysis_fact(),
                        ),
                    ]
                ),
                exported_files=tuple(
                    [
                        create_file_summary(
                            path=ProjectRelativePath(Path("src/test.py")),
                            exports=tuple(
                                [
                                    create_public_declaration_summary(),
                                ]
                            ),
                            dependencies=tuple([create_dependency_summary()]),
                        )
                    ]
                ),
            ),
        )


class TestDirectoryAnalysisFact:
    def test_append(self) -> None:
        item = create_directory_analysis_fact(
            public_symbol_count=3, file_count=4, total_symbol_count=5
        )
        result = item.add(
            create_directory_analysis_fact(
                public_symbol_count=10, file_count=20, total_symbol_count=30
            )
        )

        assert result.file_count == 24
        assert result.public_symbol_count == 13
        assert result.total_symbol_count == 35
        assert item.file_count == 24
        assert item.public_symbol_count == 13
        assert item.total_symbol_count == 35
