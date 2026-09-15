from gyomu_docstring.update.build_file_update import (
    _get_declaration_definition_end_offset,
    build_addition_entry,
    build_deletion_entry,
    build_file_update_plan,
    build_file_update_plan_entry,
    build_replacement_entry,
    validate_file_update_plan_entries,
)
from gyomu_docstring.update.docstring.rendered_symbol import (
    RenderedSymbolDocstring,
)
from gyomu_python_analysis.error.update import UpdateError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.schemas.python.location import SourceLocation
from returns.result import Failure, Success

from packages.docstring.docstring_test_support.helpers import (
    create_entry,
    create_rendered_docstring,
)
from packages.schema.schema_test_support.helpers import (
    _default_identity,
    create_class_analysis,
    create_declaration_identity,
    create_file_analysis_context,
    create_function_analysis,
    create_location,
    create_method_analysis,
)


class TestValidateFileUpdatePlanEntries:
    def test_accepts_empty_entries(self) -> None:
        result = validate_file_update_plan_entries(())
        assert isinstance(result, Success)

    def test_accepts_single_entry(self) -> None:
        entry = create_entry(start_offset=10, end_offset=20)

        result = validate_file_update_plan_entries((entry,))
        assert isinstance(result, Success)

    def test_accepts_adjacent_entries(self) -> None:
        first = create_entry(start_offset=10, end_offset=20)
        second = create_entry(start_offset=20, end_offset=30)

        result = validate_file_update_plan_entries((first, second))
        assert isinstance(result, Success)

    def test_rejects_overlapping_entries(self) -> None:
        first = create_entry(start_offset=10, end_offset=20)
        second = create_entry(start_offset=19, end_offset=30)

        # with pytest.raises(ValidationError, match="Overlapping"):
        result = validate_file_update_plan_entries((first, second))
        assert isinstance(result, Failure)
        assert "Overlapping" in result.failure().message

    def test_rejects_invalid_range(self) -> None:
        entry = create_entry(start_offset=20, end_offset=10)

        # with pytest.raises(ValidationError, match="start_offset"):
        result = validate_file_update_plan_entries((entry,))
        assert isinstance(result, Failure)
        assert "start_offset" in result.failure().message

    def test_validates_entries_regardless_of_input_order(self) -> None:
        first = create_entry(start_offset=10, end_offset=20)
        second = create_entry(start_offset=30, end_offset=40)

        result = validate_file_update_plan_entries((second, first))
        assert isinstance(result, Success)


class TestBuildDeletionEntry:
    def test_build_deletion_entry_removes_surrounding_spaces(self) -> None:
        source = '    """test"""    \n'

        location = SourceLocation(
            start_line=1,
            start_column=4,
            end_line=1,
            end_column=14,
            start_offset=4,
            end_offset=14,
        )

        rendered = RenderedSymbolDocstring(
            identity=_default_identity,
            docstring=None,
            location=location,
        )

        entry = build_deletion_entry(source, rendered)

        assert entry.location.start_offset == 0
        assert entry.location.end_offset == 18
        assert entry.new_text == ""

    def test_build_deletion_entry_removes_spaces_and_tabs(self) -> None:
        source = '\t \t"""test"""\t \n'

        location = SourceLocation(
            start_line=1,
            start_column=3,
            end_line=1,
            end_column=13,
            start_offset=3,
            end_offset=13,
        )

        rendered = RenderedSymbolDocstring(
            identity=_default_identity,
            docstring=None,
            location=location,
        )

        entry = build_deletion_entry(source, rendered)

        assert entry.location.start_offset == 0
        assert entry.location.end_offset == 15
        assert entry.new_text == ""

    def test_build_deletion_entry_preserves_newline(self) -> None:
        source = '    """test"""\n    pass\n'

        location = SourceLocation(
            start_line=1,
            start_column=4,
            end_line=1,
            end_column=14,
            start_offset=3,
            end_offset=14,
        )

        rendered = RenderedSymbolDocstring(
            identity=_default_identity,
            docstring=None,
            location=location,
        )

        entry = build_deletion_entry(source, rendered)

        assert (
            source[entry.location.start_offset : entry.location.end_offset]
            == '    """test"""'
        )

    def test_build_deletion_entry_preserves_crlf(self) -> None:
        source = '    """test"""\t\r\n    pass\r\n'

        location = SourceLocation(
            start_line=1,
            start_column=4,
            end_line=1,
            end_column=14,
            start_offset=3,
            end_offset=14,
        )

        rendered = RenderedSymbolDocstring(
            identity=_default_identity,
            docstring=None,
            location=location,
        )

        entry = build_deletion_entry(source, rendered)

        assert source[entry.location.end_offset] == "\r"

    def test_build_deletion_entry_at_eof(self) -> None:
        source = '    """test"""    '

        location = SourceLocation(
            start_line=1,
            start_column=4,
            end_line=1,
            end_column=14,
            start_offset=4,
            end_offset=14,
        )

        rendered = RenderedSymbolDocstring(
            identity=_default_identity,
            docstring=None,
            location=location,
        )

        entry = build_deletion_entry(source, rendered)

        assert entry.location.start_offset == 0
        assert entry.location.end_offset == len(source)


class TestBuildReplacementEntry:
    def test_build_replacement_entry(self) -> None:
        rendered = create_rendered_docstring(
            docstring='"""new"""',
            start_offset=10,
            end_offset=20,
        )

        entry = build_replacement_entry(rendered)

        assert entry.identity == rendered.identity
        assert entry.location == rendered.location
        assert entry.new_text == '"""new"""'


class TestBuildAdditionEntry:
    def test_builds_entry_for_function(self) -> None:
        analysis = create_function_analysis(
            indent=0,
            location=create_location(start_offset=0, end_offset=48),
        )
        rendered = create_rendered_docstring(
            docstring='    """new"""',
            start_offset=4,
            end_offset=4,
        )

        entry = build_addition_entry(
            source="def add(a1: int, a2:int)-> int:\n    return a1+a2",
            analysis=analysis,
            rendered=rendered,
        ).unwrap()

        assert entry.identity == rendered.identity
        assert entry.location.start_offset == 31
        assert entry.location.end_offset == 31
        assert entry.new_text == '\n    """new"""'

    def test_builds_entry_for_class(self) -> None:
        source = "    class Foo:\n        pass\n"
        analysis = create_class_analysis(
            indent=4,
            location=create_location(start_offset=4, end_offset=16),
        )
        rendered = create_rendered_docstring(
            docstring='        """new"""',
            start_offset=0,
            end_offset=0,
        )

        entry = build_addition_entry(
            source=source,
            analysis=analysis,
            rendered=rendered,
        ).unwrap()

        assert entry.identity == rendered.identity
        assert entry.location.start_offset == source.index("\n")
        assert entry.location.end_offset == source.index("\n")
        assert entry.new_text == '\n        """new"""'

    def test_builds_entry_for_member(self) -> None:
        source = "    class Foo:\n        def bar(self):\n            pass\n"

        start_offset = source.index("def bar")
        analysis = create_method_analysis(
            indent=8,
            location=create_location(
                start_offset=start_offset,
                end_offset=start_offset + len("def bar(self):"),
            ),
        )
        rendered = create_rendered_docstring(
            docstring='            """new"""',
            start_offset=0,
            end_offset=0,
        )

        entry = build_addition_entry(
            source=source,
            analysis=analysis,
            rendered=rendered,
        ).unwrap()

        assert entry.identity == rendered.identity

        expected = source.index("\n", start_offset)
        assert entry.location.start_offset == expected
        assert entry.location.end_offset == expected
        assert entry.new_text == '\n            """new"""'


class TestBuildFileUpdatePlanEntry:
    def test_builds_addition_entry(self) -> None:
        source = "    def add(a1: int, a2: int) -> int:\n        return a1 + a2"
        analysis = create_function_analysis(
            indent=4,
            location=create_location(
                start_offset=4,
                end_offset=38,
            ),
        )
        context = create_file_analysis_context(analysis)

        rendered = create_rendered_docstring(
            docstring='        """new"""',
            start_offset=0,
            end_offset=0,
            identity=analysis.identity,
        )

        entry = build_file_update_plan_entry(
            source=source,
            context=context,
            rendered=rendered,
        ).unwrap()

        expected = source.index("\n")

        assert entry.identity == rendered.identity
        assert entry.location.start_offset == expected
        assert entry.location.end_offset == expected
        assert entry.new_text == '\n        """new"""'

    def test_builds_replacement_entry(self) -> None:
        analysis = create_function_analysis(
            indent=4,
            location=create_location(start_offset=10, end_offset=20),
        )
        context = create_file_analysis_context(analysis)

        rendered = create_rendered_docstring(
            docstring='"""new"""',
            start_offset=30,
            end_offset=40,
            identity=analysis.identity,
        )

        entry = build_file_update_plan_entry(
            source="",
            context=context,
            rendered=rendered,
        ).unwrap()

        assert entry.identity == rendered.identity
        assert entry.location == rendered.location
        assert entry.new_text == '"""new"""'

    def test_builds_deletion_entry(self) -> None:
        source = '    """test"""    \n'
        analysis = create_function_analysis(
            indent=4,
            location=create_location(start_offset=0, end_offset=20),
        )
        context = create_file_analysis_context(analysis)

        rendered = create_rendered_docstring(
            docstring=None, start_offset=4, end_offset=14, identity=analysis.identity
        )

        entry = build_file_update_plan_entry(
            source=source,
            context=context,
            rendered=rendered,
        ).unwrap()

        assert entry.identity == rendered.identity
        assert entry.location.start_offset == 0
        assert entry.location.end_offset == 18
        assert entry.new_text == ""

    def test_builds_deletion_entry_for_empty_docstring(self) -> None:
        analysis = create_function_analysis(
            indent=4,
            location=create_location(start_offset=0, end_offset=20),
        )
        context = create_file_analysis_context(analysis)

        rendered = create_rendered_docstring(
            docstring="", start_offset=4, end_offset=15, identity=analysis.identity
        )

        entry = build_file_update_plan_entry(
            source='    """old"""\n',
            context=context,
            rendered=rendered,
        ).unwrap()

        assert entry.new_text == ""

    def test_rejects_unknown_identity(self) -> None:
        context = create_file_analysis_context()

        rendered = create_rendered_docstring(
            docstring='"""new"""',
            start_offset=0,
            end_offset=0,
        )

        result = build_file_update_plan_entry(
            source="",
            context=context,
            rendered=rendered,
        )
        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, ValidationError)
        assert "Declaration Item Not Found" in failure.message

    def test_rejects_declaration_without_location(self) -> None:
        analysis = create_method_analysis(
            indent=None,
            location=None,
        )
        context = create_file_analysis_context(analysis)

        rendered = create_rendered_docstring(
            docstring='"""new"""',
            start_offset=0,
            end_offset=0,
            identity=analysis.identity,
        )

        # with pytest.raises(
        #     ValidationError,
        #     match="Declation Item is constructor parameter",
        # ):
        result = build_file_update_plan_entry(
            source="",
            context=context,
            rendered=rendered,
        )
        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, ValidationError)
        assert "Declation Item is constructor parameter" in failure.message


class TestBuildFileUpdatePlan:
    def test_builds_file_update_plan(self) -> None:
        first_analysis = create_function_analysis(
            identity=create_declaration_identity("first"),
            indent=4,
            location=create_location(start_offset=10, end_offset=20),
        )
        second_analysis = create_function_analysis(
            identity=create_declaration_identity("second"),
            indent=4,
            location=create_location(start_offset=30, end_offset=40),
        )

        context = create_file_analysis_context(
            first_analysis,
            second_analysis,
        )

        rendered = (
            RenderedSymbolDocstring(
                identity=first_analysis.identity,
                docstring='"""first"""',
                location=create_location(
                    start_offset=50,
                    end_offset=60,
                ),
            ),
            RenderedSymbolDocstring(
                identity=second_analysis.identity,
                docstring='"""second"""',
                location=create_location(
                    start_offset=70,
                    end_offset=80,
                ),
            ),
        )

        plan = build_file_update_plan(
            context=context,
            rendered_docstrings=rendered,
            source="",
        ).unwrap()

        assert len(plan.items) == 2

        assert plan.items[0].identity == first_analysis.identity
        assert plan.items[0].location.start_offset == 50
        assert plan.items[0].location.end_offset == 60
        assert plan.items[0].new_text == '"""first"""'

        assert plan.items[1].identity == second_analysis.identity
        assert plan.items[1].location.start_offset == 70
        assert plan.items[1].location.end_offset == 80
        assert plan.items[1].new_text == '"""second"""'

    def test_rejects_overlapping_entries(self) -> None:
        first_analysis = create_function_analysis(
            identity=create_declaration_identity("first"),
            indent=4,
            location=create_location(start_offset=10, end_offset=20),
        )
        second_analysis = create_function_analysis(
            identity=create_declaration_identity("second"),
            indent=4,
            location=create_location(start_offset=30, end_offset=40),
        )

        context = create_file_analysis_context(
            first_analysis,
            second_analysis,
        )

        rendered = (
            RenderedSymbolDocstring(
                identity=first_analysis.identity,
                docstring='"""first"""',
                location=create_location(
                    start_offset=10,
                    end_offset=25,
                ),
            ),
            RenderedSymbolDocstring(
                identity=second_analysis.identity,
                docstring='"""second"""',
                location=create_location(
                    start_offset=20,
                    end_offset=30,
                ),
            ),
        )

        # with pytest.raises(ValidationError, match="Overlapping"):
        result = build_file_update_plan(
            context=context,
            rendered_docstrings=rendered,
            source="",
        )
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, UpdateError)
        assert error.__cause__
        assert isinstance(error.__cause__, ValidationError)

        assert "Overlapping" in error.__cause__.message

    def test_builds_empty_file_update_plan(self) -> None:
        context = create_file_analysis_context()

        plan = build_file_update_plan(
            context=context,
            rendered_docstrings=(),
            source="",
        ).unwrap()

        assert plan.items == ()

    def test_builds_plan_with_addition_replacement_and_deletion(self) -> None:
        source = (
            "def add():\n"
            "    pass\n"
            "\n"
            "def replace():\n"
            '    """old"""\n'
            "    pass\n"
            "\n"
            "def delete():\n"
            '    """remove"""\n'
            "    pass\n"
        )
        # for i, char in enumerate(source):
        #     print(i, repr(char))

        add_start = source.index("def add")
        add_end = source.index("\n", add_start)

        add_analysis = create_function_analysis(
            name="add",
            indent=4,
            location=create_location(
                start_offset=add_start,
                end_offset=add_end,
            ),
        )
        replace_analysis = create_function_analysis(
            name="replace",
            indent=4,
            location=create_location(
                start_offset=25,
                end_offset=50,
            ),
        )
        delete_analysis = create_function_analysis(
            name="delete",
            indent=4,
            location=create_location(
                start_offset=78,
                end_offset=90,
            ),
        )

        context = create_file_analysis_context(
            add_analysis,
            replace_analysis,
            delete_analysis,
        )

        rendered_docstrings = (
            create_rendered_docstring(
                identity=add_analysis.identity,
                docstring='    """added"""',
                start_offset=8,
                end_offset=8,
            ),
            create_rendered_docstring(
                identity=replace_analysis.identity,
                docstring='"""new"""',
                start_offset=39,
                end_offset=49,
            ),
            create_rendered_docstring(
                identity=delete_analysis.identity,
                docstring=None,
                start_offset=78,
                end_offset=90,
            ),
        )

        plan = build_file_update_plan(
            context=context,
            rendered_docstrings=rendered_docstrings,
            source=source,
        ).unwrap()

        assert len(plan.items) == 3

        addition, replacement, deletion = plan.items

        assert addition.identity == add_analysis.identity
        assert addition.new_text == '\n    """added"""'
        expected_addition_offset = source.index("\n", add_start)

        assert addition.location.start_offset == expected_addition_offset
        assert addition.location.end_offset == expected_addition_offset
        assert replacement.identity == replace_analysis.identity
        assert replacement.new_text == '"""new"""'
        assert replacement.location == rendered_docstrings[1].location

        assert deletion.identity == delete_analysis.identity
        assert deletion.new_text == ""


class TestGetDeclarationDefinitionEndOffset:
    @staticmethod
    def _location(source: str) -> SourceLocation:
        return SourceLocation(
            start_line=1,
            start_column=0,
            end_line=len(source.splitlines()),
            end_column=len(source.splitlines()[-1]),
            start_offset=0,
            end_offset=len(source),
        )

    def test_function(self) -> None:
        source = "def foo():\n    pass\n"
        analysis = create_function_analysis(
            indent=0,
            location=self._location(source),
            name="foo",
        )

        result = _get_declaration_definition_end_offset(
            source=source,
            analysis=analysis,
        )

        assert result == Success(source.index(":") + 1)

    def test_multiline_function(self) -> None:
        source = "def foo(\n    value: int,\n) -> None:\n    pass\n"

        result = _get_declaration_definition_end_offset(
            source=source,
            analysis=create_function_analysis(0, location=self._location(source)),
        )

        expected = source.index(":\n    pass")
        assert result == Success(expected + 1)

    def test_multiline_function_with_type_annotation(self) -> None:
        source = (
            "def foo(\n"
            "    value: dict[str, int],\n"
            "    other: list[str],\n"
            ") -> str:\n"
            "    pass\n"
        )
        result = _get_declaration_definition_end_offset(
            source=source,
            analysis=create_function_analysis(
                indent=0, location=self._location(source)
            ),
        )

        expected = source.index(":\n    pass")
        assert result == Success(expected + 1)

    def test_class(self) -> None:
        source = "class Foo:\n    pass\n"
        analysis = create_class_analysis(indent=0, location=self._location(source))

        result = _get_declaration_definition_end_offset(
            source=source,
            analysis=analysis,
        )

        expected = source.index(":\n    pass")
        assert result == Success(expected + 1)

    def test_method(self) -> None:
        source = "class Foo:\n    def bar(self):\n        pass\n"

        # MethodAnalysis の location は def bar の位置を指すようにする

        result = _get_declaration_definition_end_offset(
            source=source,
            analysis=create_method_analysis(
                indent=4,
                location=create_location(
                    start_line=2,
                    start_column=4,
                    start_offset=15,
                    end_line=3,
                    end_column=13,
                    end_offset=42,
                ),
            ),
        )

        expected = source.index(":\n        pass")
        assert result == Success(expected + 1)

    def test_async_function(self) -> None:
        source = "async def foo(value: dict[str, int]) -> str:\n    pass\n"

        result = _get_declaration_definition_end_offset(
            source=source,
            analysis=create_function_analysis(
                indent=0, location=self._location(source)
            ),
        )

        expected = source.index(":\n    pass")
        assert result == Success(expected + 1)

    def test_definition_end_not_found(self) -> None:
        source = "def foo()\n"
        analysis = create_function_analysis(indent=0, location=self._location(source))
        result = _get_declaration_definition_end_offset(
            source=source,
            analysis=analysis,
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, ValidationError)
        assert error.message == "Declaration definition end not found"
        assert error.context == (
            "gyomu_docstring.update.build_file_update."
            "_get_declaration_definition_end_offset"
        )
        assert error.details == {"identity": analysis.identity}

    def test_trailing_spaces_before_newline(self) -> None:
        source = "def foo():   \n    pass\n"
        analysis = create_function_analysis(
            indent=0,
            location=self._location(source),
        )

        result = _get_declaration_definition_end_offset(
            source=source,
            analysis=analysis,
        )

        expected = source.index("\n")
        assert result == Success(expected)

    def test_trailing_tabs_before_newline(self) -> None:
        source = "def foo():\t\t\n    pass\n"
        analysis = create_function_analysis(
            indent=0,
            location=self._location(source),
        )

        result = _get_declaration_definition_end_offset(
            source=source,
            analysis=analysis,
        )

        expected = source.index("\n")
        assert result == Success(expected)

    def test_trailing_spaces_and_tabs_before_newline(self) -> None:
        source = "def foo():  \t  \n    pass\n"
        analysis = create_function_analysis(
            indent=0,
            location=self._location(source),
        )

        result = _get_declaration_definition_end_offset(
            source=source,
            analysis=analysis,
        )

        expected = source.index("\n")
        assert result == Success(expected)

    def test_trailing_spaces_before_crlf(self) -> None:
        source = "def foo():   \r\n    pass\r\n"
        analysis = create_function_analysis(
            indent=0,
            location=self._location(source),
        )

        result = _get_declaration_definition_end_offset(
            source=source,
            analysis=analysis,
        )

        expected = source.index("\r")
        assert result == Success(expected)
