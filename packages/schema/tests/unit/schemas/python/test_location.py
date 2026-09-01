from gyomu_schema.schemas.python.location import SourceLocation


def test_creates_source_location() -> None:
    location = SourceLocation(
        start_line=10,
        start_column=4,
        end_line=10,
        end_column=15,
    )

    assert location.start_line == 10
    assert location.start_column == 4
    assert location.end_line == 10
    assert location.end_column == 15
