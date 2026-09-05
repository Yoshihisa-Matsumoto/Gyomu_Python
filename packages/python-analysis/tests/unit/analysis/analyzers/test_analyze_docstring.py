from griffe import Attribute, Class, Function
from gyomu_python_analysis.analysis.analyzers.cls import analyze_class
from gyomu_python_analysis.analysis.analyzers.docstring import (
    _extract_return_description,
)
from gyomu_python_analysis.analysis.analyzers.functions import analyze_function
from gyomu_python_analysis.analysis.analyzers.variables import analyze_variable
from gyomu_python_analysis.analysis.load_module_analysis import load_module_analysis
from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.docstring import (
    DocstringCustomSection,
    DocstringExamplesSection,
    DocstringGyomuContextSection,
    DocstringNotesSection,
    DocstringParametersSection,
    DocstringRaisesSection,
    DocstringReturnsSection,
    DocstringSectionKind,
)
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.python.variable import VariableAnalysis
from returns.result import Failure

from tests.helpers import AnalysisTestBase


class TestExtractReturnDescription:
    def test_extract_return_description(self):
        assert (
            _extract_return_description("dict[str, object]: The user information.")
            == "The user information."
        )

        assert (
            _extract_return_description("The user information.")
            == "The user information."
        )

        assert (
            _extract_return_description("The result: something.")
            == "The result: something."
        )
        assert (
            _extract_return_description("tuple[str, int]: The user's name and age.")
            == "The user's name and age."
        )


class TestAnalyzeDocstring(AnalysisTestBase):
    def _analyze_function(self, file_name: str, name: str) -> FunctionAnalysis:
        context = self._read_module_fixture(
            PythonPath(f"analysis.docstring.{file_name}")
        )
        module = context.source.module
        func = module[name]

        assert isinstance(func, Function)

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
        )
        return result

    def _analyze_class(self, file_name: str, name: str) -> ClassAnalysis:
        context = self._read_module_fixture(
            PythonPath(f"analysis.docstring.{file_name}")
        )
        module = context.source.module
        cls = module[name]

        assert isinstance(cls, Class)

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
        )
        return result

    def _analyze_variable(self, file_name: str, name: str) -> VariableAnalysis:
        context = self._read_module_fixture(
            PythonPath(f"analysis.docstring.{file_name}")
        )
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
        )
        return result

    def _analyze_file(self, file_name: str) -> ModuleAnalysis:
        module_path = PythonPath(f"analysis.docstring.{file_name}")
        context = self._read_module_fixture(module_path)
        result = load_module_analysis(context.project, module_path)
        if isinstance(result, Failure):
            raise result.failure()

        return result.unwrap()

    def test_simple(self) -> None:
        func = self._analyze_function("01-simple", "basic")
        assert func.docstring is not None

        docstring = func.docstring

        assert docstring.summary == "Return the given value."
        assert docstring.description == "This function is simple function"

        assert len(docstring.sections) == 2

        args = docstring.sections[0]
        assert args.kind == DocstringSectionKind.ARGS
        assert len(args.items) == 1

        assert args.items[0].name == "value"
        assert args.items[0].type == "str"
        assert args.items[0].description == "The value to return."

        returns = docstring.sections[1]
        assert returns.kind == DocstringSectionKind.RETURNS
        assert returns.item is not None
        assert returns.item.type == "str"
        assert returns.item.description == "The given value."

    def test_args(self) -> None:
        func = self._analyze_function("02-args", "multiple_args")
        assert func.docstring is not None

        docstring = func.docstring

        assert docstring.summary == "Create a user."
        assert docstring.description is None

        assert len(docstring.sections) == 1

        args = docstring.sections[0]

        assert args.kind == DocstringSectionKind.ARGS
        assert len(args.items) == 3

        assert args.items[0].name == "name"
        assert args.items[0].type == "str"
        assert args.items[0].description == "The user's name."

        assert args.items[1].name == "age"
        assert args.items[1].type == "int"
        assert args.items[1].description == "The user's age."

        assert args.items[2].name == "active"
        assert args.items[2].type == "bool"
        assert args.items[2].description == "Whether the user is active."

    def test_returns(self) -> None:
        func = self._analyze_function("03-typed-return", "find_user")
        assert func.docstring is not None

        docstring = func.docstring

        returns = next(
            section
            for section in docstring.sections
            if section.kind == DocstringSectionKind.RETURNS
        )

        assert returns.item is not None
        assert returns.item.type == "dict[str, object]"
        assert returns.item.description == "The user information."

    def test_raises(self) -> None:
        func = self._analyze_function("04-raises", "load_user")
        assert func.docstring is not None

        docstring = func.docstring

        raises = next(
            section
            for section in docstring.sections
            if section.kind == DocstringSectionKind.RAISES
        )

        assert len(raises.items) == 2

        assert raises.items[0].type == "ValueError"
        assert raises.items[0].description == "If the user ID is invalid."

        assert raises.items[1].type == "LookupError"
        assert raises.items[1].description == "If the user cannot be found."

    def test_examples(self) -> None:
        func = self._analyze_function("05-examples", "add")

        assert func.docstring is not None

        docstring = func.docstring

        examples = next(
            section
            for section in docstring.sections
            if section.kind == DocstringSectionKind.EXAMPLES
        )

        assert len(examples.items) == 2

        assert (
            examples.items[0].value
            == """>>> add(1, 2)
3"""
        )

        assert (
            examples.items[1].value
            == """>>> add(-1, 5)
4"""
        )

    def test_notes(self) -> None:
        func = self._analyze_function("06-notes", "process")

        assert func.docstring is not None
        assert func.docstring.summary == "Process a value."
        assert func.docstring.description is None

        assert len(func.docstring.sections) == 3

        args = func.docstring.sections[0]
        assert isinstance(args, DocstringParametersSection)
        assert len(args.items) == 1
        assert args.items[0].name == "value"
        assert args.items[0].type == "str"
        assert args.items[0].description == "The value to process."

        notes = func.docstring.sections[1]
        assert isinstance(notes, DocstringNotesSection)
        assert (
            notes.value == "The value is normalized before processing.\n"
            "Leading and trailing whitespace is removed.\n\n"
            "This operation does not modify the original value."
        )

        returns = func.docstring.sections[2]
        assert isinstance(returns, DocstringReturnsSection)
        assert returns.item.type == "str"
        assert returns.item.description == "The processed value."

    def test_complex(self) -> None:
        func = self._analyze_function("07-complex", "process_user")

        assert func.docstring is not None
        assert func.docstring.summary == "Process a user."
        assert (
            func.docstring.description
            == "This function loads a user and updates its information."
        )

        assert len(func.docstring.sections) == 5

        args = func.docstring.sections[0]
        assert isinstance(args, DocstringParametersSection)
        assert len(args.items) == 3

        assert args.items[0].name == "user_id"
        assert args.items[0].type == "int"
        assert args.items[0].description == "The user ID."

        assert args.items[1].name == "name"
        assert args.items[1].type == "str"
        assert args.items[1].description == "The user's name."

        assert args.items[2].name == "active"
        assert args.items[2].type == "bool"
        assert args.items[2].description == "Whether the user is active."

        raises = func.docstring.sections[1]
        assert isinstance(raises, DocstringRaisesSection)
        assert len(raises.items) == 2

        assert raises.items[0].type == "ValueError"
        assert raises.items[0].description == "If the user ID is invalid."

        assert raises.items[1].type == "LookupError"
        assert raises.items[1].description == "If the user does not exist."

        returns = func.docstring.sections[2]
        assert isinstance(returns, DocstringReturnsSection)
        assert returns.item.type == "dict[str, object]"
        assert returns.item.description == "The updated user information."

        examples = func.docstring.sections[3]
        assert isinstance(examples, DocstringExamplesSection)
        assert len(examples.items) == 1
        assert (
            examples.items[0].value == '>>> process_user(1, "Alice")\n'
            "{'id': 1, 'name': 'Alice', 'active': True}"
        )

        notes = func.docstring.sections[4]
        assert isinstance(notes, DocstringNotesSection)
        assert (
            notes.value
            == "The user is loaded from the repository before being updated.\n"
            "The operation is transactional."
        )

    def test_gyomu_context(self) -> None:
        func = self._analyze_function("08-gyomu-context", "process_user")

        assert func.docstring is not None
        assert func.docstring.summary == "Process a user."
        assert func.docstring.description is None

        assert len(func.docstring.sections) == 3

        args = func.docstring.sections[0]
        assert isinstance(args, DocstringParametersSection)
        assert len(args.items) == 1
        assert args.items[0].name == "user_id"
        assert args.items[0].type == "int"
        assert args.items[0].description == "The user ID."

        returns = func.docstring.sections[1]
        assert isinstance(returns, DocstringReturnsSection)
        assert returns.item.type == "dict[str, object]"
        assert returns.item.description == "The processed user."

        context = func.docstring.sections[2]
        assert isinstance(context, DocstringGyomuContextSection)
        assert (
            context.value
            == "This function is used by the user synchronization workflow.\n"
            "It should only be called from the application service layer."
        )

    def test_custom_section(self) -> None:
        func = self._analyze_function("09-custom-section", "custom_section")

        assert func.docstring is not None
        assert func.docstring.summary == "Do something."
        assert func.docstring.description is None

        assert len(func.docstring.sections) == 3

        foo = func.docstring.sections[0]
        assert isinstance(foo, DocstringCustomSection)
        assert foo.title == "Foo"
        assert foo.value == "This is a custom section.\ndummy"

        returns = func.docstring.sections[1]
        assert isinstance(returns, DocstringReturnsSection)
        assert returns.item.type == "None"
        assert returns.item.description == "The processed user."

        bar = func.docstring.sections[2]
        assert isinstance(bar, DocstringCustomSection)
        assert bar.title == "Bar"
        assert bar.value == "Another custom section."

    def test_no_sections(self) -> None:
        func = self._analyze_function("10-edge-cases", "no_sections")

        assert func.docstring is not None
        assert func.docstring.summary == "Do something."
        assert (
            func.docstring.description
            == "This function does something without any arguments or return value."
        )
        assert func.docstring.sections == ()

    def test_empty_docstring(self) -> None:
        func = self._analyze_function("10-edge-cases", "empty_docstring")

        assert func.docstring is not None
        assert func.docstring.summary is None
        assert func.docstring.description is None
        assert func.docstring.sections == ()

    def test_section_only(self) -> None:
        func = self._analyze_function("10-edge-cases", "section_only")

        assert func.docstring is not None
        assert func.docstring.summary == "Do something."
        assert func.docstring.description is None

        assert len(func.docstring.sections) == 1

        notes = func.docstring.sections[0]
        assert isinstance(notes, DocstringNotesSection)
        assert notes.value == "This is a note."

    def test_custom_and_gyomu_context(self) -> None:
        func = self._analyze_function(
            "11-custom-and-gyomu-context",
            "custom_and_gyomu_context",
        )

        assert func.docstring is not None

        docstring = func.docstring

        assert docstring.summary == "Process something."
        assert docstring.description is None

        assert len(docstring.sections) == 2

        foo = docstring.sections[0]
        assert isinstance(foo, DocstringCustomSection)
        assert foo.title == "Foo"
        assert foo.value == (
            "This is a custom section.\n\nIt contains additional information."
        )

        gyomu_context = docstring.sections[1]
        assert isinstance(gyomu_context, DocstringGyomuContextSection)
        assert gyomu_context.value == (
            "This function is used by the application workflow.\n"
            "It should only be called from the service layer."
        )

    def test_module(self) -> None:
        module = self._analyze_file("12-module")
        docstring = module.docstring
        assert docstring is not None

        assert docstring.summary == "User management module."
        assert (
            docstring.description
            == "This module provides operations for creating and updating users."
        )

        assert len(docstring.sections) == 2

        notes = docstring.sections[0]
        assert isinstance(notes, DocstringNotesSection)
        assert notes.value == ("User data is managed by the application service layer.")

        gyomu_context = docstring.sections[1]
        assert isinstance(gyomu_context, DocstringGyomuContextSection)
        assert gyomu_context.value == (
            "This module belongs to the user synchronization workflow.\n"
            "It should only be used by the application service layer."
        )

    def test_class(self) -> None:
        cls = self._analyze_class(
            "13-class",
            "User",
        )

        # Class docstring
        assert cls.docstring is not None
        assert cls.docstring.indent == 4
        assert cls.docstring.location.start_line == 2
        assert cls.docstring.location.start_column == 4
        assert cls.docstring.location.end_line == 12
        assert cls.docstring.location.end_column == 7
        assert cls.docstring.summary == "User model."
        assert (
            cls.docstring.description
            == "This class represents a user in the application."
        )

        assert len(cls.docstring.sections) == 2

        notes = cls.docstring.sections[0]
        assert isinstance(notes, DocstringNotesSection)
        assert notes.value == (
            "User instances are managed by the application service layer."
        )

        gyomu_context = cls.docstring.sections[1]
        assert isinstance(gyomu_context, DocstringGyomuContextSection)
        assert gyomu_context.value == (
            "This class is used by the user synchronization workflow.\n"
            "It should only be created by the application service layer."
        )

        # Methods
        assert len(cls.methods) == 3

        init = next(method for method in cls.methods if method.name == "__init__")
        assert init.docstring is not None
        assert init.docstring.location.start_line == 25
        assert init.docstring.location.start_column == 8
        assert init.docstring.location.end_line == 33
        assert init.docstring.location.end_column == 11
        print(init.docstring.location)
        assert init.docstring.summary == "Initialize a user."
        assert init.docstring.description is None

        activate = next(method for method in cls.methods if method.name == "activate")
        assert activate.docstring is not None
        assert activate.docstring.indent == 8
        assert activate.docstring.location.start_line == 38
        assert activate.docstring.location.start_column == 8
        assert activate.docstring.location.end_line == 47
        assert activate.docstring.location.end_column == 11
        assert activate.docstring.summary == "Activate the user."
        assert activate.docstring.description == "This method marks the user as active."

        deactivate = next(
            method for method in cls.methods if method.name == "deactivate"
        )
        assert deactivate.docstring is not None
        assert deactivate.docstring.indent == 8
        assert deactivate.docstring.location.start_line == 51
        assert deactivate.docstring.location.start_column == 8
        assert deactivate.docstring.location.end_line == 57
        assert deactivate.docstring.location.end_column == 11
        assert deactivate.docstring.summary == "Deactivate the user."
        assert (
            deactivate.docstring.description
            == "This method marks the user as inactive."
        )

        # Variables
        assert len(cls.variables) == 2

        name = next(variable for variable in cls.variables if variable.name == "name")
        assert name.docstring is not None
        assert name.docstring.indent == 4
        assert name.docstring.location.start_line == 15
        assert name.docstring.location.start_column == 4
        assert name.docstring.location.end_line == 15
        assert name.docstring.location.end_column == 26
        assert name.docstring.summary == "The user's name."
        assert name.docstring.description is None

        active = next(
            variable for variable in cls.variables if variable.name == "active"
        )
        assert active.docstring is not None
        assert active.docstring.indent == 4
        assert active.docstring.location.start_line == 18
        assert active.docstring.location.start_column == 4
        assert active.docstring.location.end_line == 18
        assert active.docstring.location.end_column == 37
        assert active.docstring.summary == "Whether the user is active."
        assert active.docstring.description is None

    def test_variable(self) -> None:
        description = self._analyze_variable("14-variable", "description")
        assert description.docstring is not None
        assert description.docstring.summary == "Description of the user."
        assert (
            description.docstring.description
            == "This variable contains the human-readable description."
        )
        assert description.docstring.indent == 0
        assert description.docstring.location.start_line == 34
        assert description.docstring.location.start_column == 0
        assert description.docstring.location.end_line == 40
        assert description.docstring.location.end_column == 3

        assert len(description.docstring.sections) == 1

        notes = description.docstring.sections[0]
        assert isinstance(notes, DocstringNotesSection)
        assert notes.value == "The description is displayed to users."

        status = self._analyze_variable("14-variable", "status")
        assert status.docstring is not None
        assert status.docstring.summary == "Current user status."
        assert status.docstring.description is None
        assert status.docstring.indent == 0
        assert status.docstring.location.start_line == 45
        assert status.docstring.location.start_column == 0
        assert status.docstring.location.end_line == 49
        assert status.docstring.location.end_column == 3

        assert len(status.docstring.sections) == 1

        gyomu_context = status.docstring.sections[0]
        assert isinstance(gyomu_context, DocstringGyomuContextSection)
        assert (
            gyomu_context.value == "This value is updated during user synchronization."
        )
