from dataclasses import dataclass
from pathlib import Path

from gyomu_python_analysis.update.apply_merge import apply_merge_plan, apply_merge_plans
from gyomu_python_analysis.update.docstring.merge_plan import (
    DeleteAction,
    MergeAction,
    MergePlan,
    ParamActionValue,
    ParamMergePlan,
    PreserveAction,
    RaiseActionValue,
    RaiseMergePlan,
    ReplaceAction,
    ReturnActionValue,
)
from gyomu_python_analysis.update.docstring.updated_docstring import (
    UpdatedDocstring,
)
from gyomu_schema.schemas.python.docstring import (
    DocstringAnalysis,
    DocstringCustomSection,
    DocstringGyomuContextSection,
    DocstringNotesSection,
    DocstringParametersSection,
    DocstringParametersSectionItem,
    DocstringRaisesSection,
    DocstringRaisesSectionItem,
    DocstringReturnsSection,
    DocstringReturnsSectionItem,
    DocstringStyle,
)
from gyomu_schema.schemas.python.file_analysis import (
    FileAnalysisContext,
    FileAnalysisMetadata,
)
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.symbol import MemberAnalysis, SymbolAnalysis
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    PythonPath,
    SourceRelativePath,
    SymbolId,
)
from returns.result import Success

from tests.helpers import (
    create_class_analysis,
    create_function_analysis,
    create_location,
    create_method_analysis,
    create_type_alias_analysis,
    create_variable_analysis,
)


@dataclass(frozen=True)
class _TestLocation:
    start_line: int = 1
    start_column: int = 0
    end_line: int = 1
    end_column: int = 0
    start_offset: int = 0
    end_offset: int = 0


class TestApplyMerge:
    @staticmethod
    def _identity() -> DeclarationIdentity:
        return DeclarationIdentity(
            symbol_id=SymbolId("example.module::example"),
            declaration_id=DeclarationId(".::example"),
        )

    @staticmethod
    def _docstring(
        *,
        summary: str | None = "Original summary.",
        description: str | None = "Original description.",
        sections: tuple = (),
    ) -> DocstringAnalysis:
        return DocstringAnalysis(
            raw='"""Original raw docstring."""',
            summary=summary,
            description=description,
            style=DocstringStyle.GOOGLE,
            location=create_location(),
            sections=sections,
            indent=4,
        )

    @classmethod
    def _context(
        cls,
        identity: DeclarationIdentity,
        docstring: DocstringAnalysis | None = None,
        symbol: SymbolAnalysis | MemberAnalysis | None = None,
        doc_is_added: bool = False,
    ) -> FileAnalysisContext:

        new_symbol = symbol
        if new_symbol is None:
            new_symbol = create_function_analysis(
                indent=0, location=create_location(), identity=identity
            )

        parsed_docstring: dict[DeclarationIdentity, DocstringAnalysis] = {}
        if doc_is_added is False:
            parsed_docstring[identity] = docstring or cls._docstring()
        else:
            pass
        metadata = FileAnalysisMetadata(
            parsed_docstring=parsed_docstring,
            symbols={identity: new_symbol},
        )

        return FileAnalysisContext(
            metadata=metadata,
            analysis=ModuleAnalysis(
                path=SourceRelativePath(Path("test.py")),
                name="test",
                module_name=PythonPath("test"),
                docstring=None,
                imports=tuple(),
                symbols=tuple(),
            ),
        )

    _preserve_action = PreserveAction()

    @staticmethod
    def _plan(
        *,
        identity: DeclarationIdentity,
        summary: MergeAction[str] = _preserve_action,
        description: MergeAction[str] = _preserve_action,
        params: tuple[ParamMergePlan, ...] = (),
        returns: MergeAction[ReturnActionValue] = _preserve_action,
        raises: tuple[RaiseMergePlan, ...] = (),
    ) -> MergePlan:
        return MergePlan(
            identity=identity,
            summary=summary,
            description=description,
            params=params,
            returns=returns,
            raises=raises,
            conflicts=(),
            confidence=1.0,
            average_confidence=1.0,
        )

    def test_apply_merge_plan_preserves_summary(self) -> None:
        identity = self._identity()
        context = self._context(identity, self._docstring(summary="Original summary."))
        plan = self._plan(identity=identity)

        result = apply_merge_plan(context, plan)

        assert isinstance(result, Success)
        updated = result.unwrap()
        assert isinstance(updated, UpdatedDocstring)
        assert updated.identity == identity
        assert updated.docstring.summary == "Original summary."

    def test_apply_merge_plan_replaces_summary(self) -> None:
        identity = self._identity()
        context = self._context(identity, self._docstring(summary="Original summary."))
        plan = self._plan(
            identity=identity,
            summary=ReplaceAction("Updated summary."),
        )

        result = apply_merge_plan(context, plan)
        assert isinstance(result, Success)

        assert result.unwrap().docstring.summary == "Updated summary."

    def test_apply_merge_plan_deletes_summary(self) -> None:
        identity = self._identity()
        context = self._context(identity, self._docstring(summary="Original summary."))
        plan = self._plan(
            identity=identity,
            summary=DeleteAction(),
        )

        result = apply_merge_plan(context, plan)

        assert isinstance(result, Success)

        assert result.unwrap().docstring.summary is None

    def test_apply_merge_plan_preserves_description(self) -> None:
        identity = self._identity()
        context = self._context(
            identity, self._docstring(description="Original description.")
        )
        plan = self._plan(identity=identity)

        result = apply_merge_plan(context, plan)

        assert isinstance(result, Success)

        assert result.unwrap().docstring.description == "Original description."

    def test_apply_merge_plan_replaces_description(self) -> None:
        identity = self._identity()
        context = self._context(
            identity, self._docstring(description="Original description.")
        )
        plan = self._plan(
            identity=identity,
            description=ReplaceAction("Updated description."),
        )

        result = apply_merge_plan(context, plan)

        assert isinstance(result, Success)

        assert result.unwrap().docstring.description == "Updated description."

    def test_apply_merge_plan_deletes_description(self) -> None:
        identity = self._identity()
        context = self._context(
            identity, self._docstring(description="Original description.")
        )
        plan = self._plan(
            identity=identity,
            description=DeleteAction(),
        )

        result = apply_merge_plan(context, plan)

        assert isinstance(result, Success)

        assert result.unwrap().docstring.description is None

    def test_apply_merge_plan_preserves_parameter(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            self._docstring(
                sections=(
                    DocstringParametersSection(
                        items=(
                            DocstringParametersSectionItem(
                                name="user_id",
                                type="int",
                                description="User identifier.",
                            ),
                        ),
                    ),
                ),
            ),
        )
        plan = self._plan(
            identity=identity,
            params=(
                ParamMergePlan(
                    name="user_id",
                    sort_order=0,
                    action=PreserveAction(),
                ),
            ),
        )

        result = apply_merge_plan(context, plan)
        assert isinstance(result, Success)

        section = result.unwrap().docstring.sections[0]
        assert isinstance(section, DocstringParametersSection)
        assert section.items == (
            DocstringParametersSectionItem(
                name="user_id",
                type="int",
                description="User identifier.",
            ),
        )

    def test_apply_merge_plan_replaces_parameter(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            self._docstring(
                sections=(
                    DocstringParametersSection(
                        items=(
                            DocstringParametersSectionItem(
                                name="user_id",
                                type="int",
                                description="User identifier.",
                            ),
                        ),
                    ),
                ),
            ),
        )
        plan = self._plan(
            identity=identity,
            params=(
                ParamMergePlan(
                    name="user_id",
                    sort_order=0,
                    action=ReplaceAction(
                        ParamActionValue(
                            parameter_type="int",
                            description="The user's identifier.",
                        )
                    ),
                ),
            ),
        )

        result = apply_merge_plan(context, plan)

        assert isinstance(result, Success)

        section = result.unwrap().docstring.sections[0]
        assert isinstance(section, DocstringParametersSection)
        assert section.items == (
            DocstringParametersSectionItem(
                name="user_id",
                type="int",
                description="The user's identifier.",
            ),
        )

    def test_apply_merge_plan_deletes_parameter(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            self._docstring(
                sections=(
                    DocstringParametersSection(
                        items=(
                            DocstringParametersSectionItem(
                                name="user_id",
                                type="int",
                                description="User identifier.",
                            ),
                            DocstringParametersSectionItem(
                                name="name",
                                type="str",
                                description="User name.",
                            ),
                        ),
                    ),
                ),
            ),
        )
        plan = self._plan(
            identity=identity,
            params=(
                ParamMergePlan(
                    name="user_id",
                    sort_order=0,
                    action=DeleteAction(),
                ),
                ParamMergePlan(
                    name="name",
                    sort_order=1,
                    action=PreserveAction(),
                ),
            ),
        )

        result = apply_merge_plan(context, plan)

        assert isinstance(result, Success)

        section = result.unwrap().docstring.sections[0]
        assert isinstance(section, DocstringParametersSection)
        assert section.items == (
            DocstringParametersSectionItem(
                name="name",
                type="str",
                description="User name.",
            ),
        )

    def test_apply_merge_plan_adds_parameter(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            self._docstring(
                sections=(
                    DocstringParametersSection(
                        items=(
                            DocstringParametersSectionItem(
                                name="user_id",
                                type="int",
                                description="User identifier.",
                            ),
                        ),
                    ),
                ),
            ),
        )
        plan = self._plan(
            identity=identity,
            params=(
                ParamMergePlan(
                    name="user_id",
                    sort_order=0,
                    action=PreserveAction(),
                ),
                ParamMergePlan(
                    name="name",
                    sort_order=1,
                    action=ReplaceAction(
                        ParamActionValue(
                            parameter_type="str",
                            description="User name.",
                        )
                    ),
                ),
            ),
        )

        result = apply_merge_plan(context, plan)

        assert isinstance(result, Success)

        section = result.unwrap().docstring.sections[0]
        assert isinstance(section, DocstringParametersSection)
        assert section.items == (
            DocstringParametersSectionItem(
                name="user_id",
                type="int",
                description="User identifier.",
            ),
            DocstringParametersSectionItem(
                name="name",
                type="str",
                description="User name.",
            ),
        )

    def test_apply_merge_plan_sorts_parameters_by_sort_order(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            self._docstring(
                sections=(
                    DocstringParametersSection(
                        items=(
                            DocstringParametersSectionItem(
                                name="user_id",
                                type="int",
                                description="User identifier.",
                            ),
                        ),
                    ),
                ),
            ),
        )
        plan = self._plan(
            identity=identity,
            params=(
                ParamMergePlan(
                    name="name",
                    sort_order=0,
                    action=ReplaceAction(
                        ParamActionValue(
                            parameter_type="str",
                            description="User name.",
                        )
                    ),
                ),
                ParamMergePlan(
                    name="user_id",
                    sort_order=1,
                    action=PreserveAction(),
                ),
            ),
        )

        result = apply_merge_plan(context, plan)

        assert isinstance(result, Success)

        section = result.unwrap().docstring.sections[0]
        assert isinstance(section, DocstringParametersSection)
        assert section.items == (
            DocstringParametersSectionItem(
                name="name",
                type="str",
                description="User name.",
            ),
            DocstringParametersSectionItem(
                name="user_id",
                type="int",
                description="User identifier.",
            ),
        )

    def test_apply_merge_plan_preserves_returns(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            self._docstring(
                sections=(
                    DocstringReturnsSection(
                        item=DocstringReturnsSectionItem(
                            type="User",
                            description="The user.",
                        ),
                    ),
                ),
            ),
        )
        plan = self._plan(identity=identity)

        result = apply_merge_plan(context, plan)

        assert isinstance(result, Success)

        section = result.unwrap().docstring.sections[0]
        assert section == DocstringReturnsSection(
            item=DocstringReturnsSectionItem(
                type="User",
                description="The user.",
            ),
        )

    def test_apply_merge_plan_replaces_return_description(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            self._docstring(
                sections=(
                    DocstringReturnsSection(
                        item=DocstringReturnsSectionItem(
                            type="User",
                            description="The user.",
                        ),
                    ),
                ),
            ),
        )
        plan = self._plan(
            identity=identity,
            returns=ReplaceAction(
                ReturnActionValue(description="The matching user.", return_type=None)
            ),
        )

        result = apply_merge_plan(context, plan)

        assert isinstance(result, Success)

        section = result.unwrap().docstring.sections[0]
        assert isinstance(section, DocstringReturnsSection)
        assert section.item == DocstringReturnsSectionItem(
            type="User",
            description="The matching user.",
        )

    def test_apply_merge_plan_deletes_returns(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            self._docstring(
                sections=(
                    DocstringReturnsSection(
                        item=DocstringReturnsSectionItem(
                            type="User",
                            description="The user.",
                        ),
                    ),
                ),
            ),
        )
        plan = self._plan(
            identity=identity,
            returns=DeleteAction(),
        )

        result = apply_merge_plan(context, plan)

        assert result.unwrap().docstring.sections == ()

    def test_apply_merge_plan_replaces_raises(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            self._docstring(
                sections=(
                    DocstringRaisesSection(
                        items=(
                            DocstringRaisesSectionItem(
                                type="TypeError",
                                description="Invalid type.",
                            ),
                        ),
                    ),
                ),
            ),
        )
        plan = self._plan(
            identity=identity,
            raises=(
                RaiseMergePlan(
                    exception_type="ValueError",
                    sort_order=1,
                    action=ReplaceAction[RaiseActionValue](
                        value=RaiseActionValue(
                            exception_type="ValueError",
                            description="Invalid value.",
                        )
                    ),
                ),
            ),
        )

        result = apply_merge_plan(context, plan)

        section = result.unwrap().docstring.sections[0]
        assert isinstance(section, DocstringRaisesSection)
        assert section.items == (
            DocstringRaisesSectionItem(
                type="ValueError",
                description="Invalid value.",
            ),
        )

    def test_apply_merge_plan_replaces_multiple_raises(self) -> None:
        identity = self._identity()
        context = self._context(identity, self._docstring())
        plan = self._plan(
            identity=identity,
            raises=(
                RaiseMergePlan(
                    exception_type="ValueError",
                    sort_order=1,
                    action=ReplaceAction[RaiseActionValue](
                        value=RaiseActionValue(
                            exception_type="ValueError",
                            description="Invalid value.",
                        )
                    ),
                ),
                RaiseMergePlan(
                    exception_type="RuntimeError",
                    sort_order=1,
                    action=ReplaceAction[RaiseActionValue](
                        value=RaiseActionValue(
                            exception_type="RuntimeError",
                            description="Operation failed.",
                        )
                    ),
                ),
            ),
        )

        result = apply_merge_plan(context, plan)

        assert result.unwrap().docstring.sections == (
            DocstringRaisesSection(
                items=(
                    DocstringRaisesSectionItem(
                        type="ValueError",
                        description="Invalid value.",
                    ),
                    DocstringRaisesSectionItem(
                        type="RuntimeError",
                        description="Operation failed.",
                    ),
                ),
            ),
        )

    def test_apply_merge_plan_removes_raises_when_empty(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            self._docstring(
                sections=(
                    DocstringRaisesSection(
                        items=(
                            DocstringRaisesSectionItem(
                                type="ValueError",
                                description="Invalid value.",
                            ),
                        ),
                    ),
                ),
            ),
        )
        plan = self._plan(
            identity=identity,
            raises=(),
        )

        result = apply_merge_plan(context, plan)

        assert result.unwrap().docstring.sections == ()

    def test_apply_merge_plan_preserves_gyomu_context(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            self._docstring(
                sections=(
                    DocstringGyomuContextSection(
                        value="Internal project metadata.",
                    ),
                ),
            ),
        )
        plan = self._plan(
            identity=identity,
            summary=ReplaceAction("Updated summary."),
        )

        result = apply_merge_plan(context, plan)

        assert result.unwrap().docstring.summary == "Updated summary."
        assert result.unwrap().docstring.sections == (
            DocstringGyomuContextSection(
                value="Internal project metadata.",
            ),
        )

    def test_apply_merge_plan_preserves_unmanaged_sections(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            self._docstring(
                sections=(
                    DocstringNotesSection(
                        value="Important note.",
                    ),
                    DocstringCustomSection(
                        title="Warning",
                        value="Do not call directly.",
                    ),
                ),
            ),
        )
        plan = self._plan(
            identity=identity,
            summary=ReplaceAction("Updated summary."),
        )

        result = apply_merge_plan(context, plan)

        assert result.unwrap().docstring.summary == "Updated summary."
        assert result.unwrap().docstring.sections == (
            DocstringNotesSection(
                value="Important note.",
            ),
            DocstringCustomSection(
                title="Warning",
                value="Do not call directly.",
            ),
        )

    def test_apply_merge_plan_preserves_raw_location_and_indent(self) -> None:
        identity = self._identity()
        existing = self._docstring(
            summary="Original summary.",
        )
        context = self._context(identity, existing)
        plan = self._plan(
            identity=identity,
            summary=ReplaceAction("Updated summary."),
        )

        result = apply_merge_plan(context, plan).unwrap()

        assert result.docstring.raw == existing.raw
        assert result.docstring.location == existing.location
        assert result.docstring.indent == existing.indent
        assert result.docstring.style == existing.style

    def test_apply_merge_plan_preserves_identity(self) -> None:
        identity = self._identity()
        context = self._context(
            identity,
        )
        plan = self._plan(
            identity=identity,
            summary=ReplaceAction("Updated summary."),
        )

        result = apply_merge_plan(context, plan).unwrap()

        assert result.identity == identity

    def test_apply_merge_plans_returns_multiple_updated_docstrings(self) -> None:
        first_identity = DeclarationIdentity(
            symbol_id=SymbolId("example.module::first"),
            declaration_id=DeclarationId(".::first"),
        )
        second_identity = DeclarationIdentity(
            symbol_id=SymbolId("example.module::second"),
            declaration_id=DeclarationId(".::second"),
        )

        first_docstring = self._docstring(summary="First summary.")
        second_docstring = self._docstring(summary="Second summary.")

        context = FileAnalysisContext(
            metadata=FileAnalysisMetadata(
                parsed_docstring={
                    first_identity: first_docstring,
                    second_identity: second_docstring,
                },
                symbols={
                    first_identity: create_function_analysis(
                        indent=0, location=create_location(), identity=first_identity
                    ),
                    second_identity: create_function_analysis(
                        indent=0, location=create_location(), identity=second_identity
                    ),
                },
            ),
            analysis=ModuleAnalysis(
                path=SourceRelativePath(Path("test.py")),
                name="test",
                module_name=PythonPath("test"),
                docstring=None,
                imports=tuple(),
                symbols=tuple(),
            ),
        )

        plans = (
            self._plan(
                identity=first_identity,
                summary=ReplaceAction("Updated first."),
            ),
            self._plan(
                identity=second_identity,
                summary=ReplaceAction("Updated second."),
            ),
        )

        results = apply_merge_plans(context, plans).unwrap()

        assert results == (
            UpdatedDocstring(
                identity=first_identity,
                docstring=DocstringAnalysis(
                    raw=first_docstring.raw,
                    summary="Updated first.",
                    description=first_docstring.description,
                    style=first_docstring.style,
                    location=first_docstring.location,
                    sections=first_docstring.sections,
                    indent=first_docstring.indent,
                ),
            ),
            UpdatedDocstring(
                identity=second_identity,
                docstring=DocstringAnalysis(
                    raw=second_docstring.raw,
                    summary="Updated second.",
                    description=second_docstring.description,
                    style=second_docstring.style,
                    location=second_docstring.location,
                    sections=second_docstring.sections,
                    indent=second_docstring.indent,
                ),
            ),
        )

    def test_apply_merge_plan_sets_function_indent_when_docstring_is_added(
        self,
    ) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            docstring=None,
            symbol=create_function_analysis(
                indent=4,
                location=create_location(),
                identity=identity,
            ),
            doc_is_added=True,
        )
        plan = self._plan(
            identity=identity,
            summary=ReplaceAction("New summary."),
        )

        result = apply_merge_plan(context, plan).unwrap()

        assert result.docstring.indent == 8

    def test_apply_merge_plan_sets_class_indent_when_docstring_is_added(
        self,
    ) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            docstring=None,
            symbol=create_class_analysis(
                indent=4,
                location=create_location(),
                identity=identity,
            ),
            doc_is_added=True,
        )
        plan = self._plan(
            identity=identity,
            summary=ReplaceAction("New summary."),
        )

        result = apply_merge_plan(context, plan).unwrap()

        assert result.docstring.indent == 8

    def test_apply_merge_plan_sets_method_indent_when_docstring_is_added(
        self,
    ) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            docstring=None,
            symbol=create_method_analysis(
                indent=8,
                location=create_location(),
                identity=identity,
            ),
            doc_is_added=True,
        )
        plan = self._plan(
            identity=identity,
            summary=ReplaceAction("New summary."),
        )

        result = apply_merge_plan(context, plan).unwrap()

        assert result.docstring.indent == 12

    def test_apply_merge_plan_sets_variable_indent_when_docstring_is_added(
        self,
    ) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            docstring=None,
            symbol=create_variable_analysis(
                indent=8,
                location=create_location(),
                identity=identity,
            ),
            doc_is_added=True,
        )
        plan = self._plan(
            identity=identity,
            summary=ReplaceAction("New summary."),
        )

        result = apply_merge_plan(context, plan).unwrap()

        assert result.docstring.indent == 8

    def test_apply_merge_plan_sets_type_alias_indent_when_docstring_is_added(
        self,
    ) -> None:
        identity = self._identity()
        context = self._context(
            identity,
            docstring=None,
            symbol=create_type_alias_analysis(
                indent=8,
                location=create_location(),
                identity=identity,
            ),
            doc_is_added=True,
        )
        plan = self._plan(
            identity=identity,
            summary=ReplaceAction("New summary."),
        )

        result = apply_merge_plan(context, plan).unwrap()

        assert result.docstring.indent == 8
