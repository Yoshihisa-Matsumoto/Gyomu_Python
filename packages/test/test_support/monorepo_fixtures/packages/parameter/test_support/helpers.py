
from parameter.models import (
    AttributeReferenceModel,
    BasicModel,
    BooleanLiteralModel,
    CallDefaultModel,
    Color,
    DictLiteralModel,
    EmptyTupleModel,
    IntegerLiteralModel,
    KeywordCallModel,
    ListLiteralModel,
    NameReferenceModel,
    NestedCallModel,
    NoneDefaultModel,
    RequiredParameterModel,
    SingletonTupleModel,
    StringLiteralModel,
    TupleLiteralModel,
)


DEFAULT_NAME = "default-name"


def create_string_literal_model(value: str = "hello") -> StringLiteralModel:
    return StringLiteralModel(value=value)


def create_integer_literal_model(value: int = 42) -> IntegerLiteralModel:
    return IntegerLiteralModel(value=value)


def create_boolean_literal_model(value: bool = True) -> BooleanLiteralModel:
    return BooleanLiteralModel(value=value)


def create_none_default_model(
    value: str | None = None,
) -> NoneDefaultModel:
    return NoneDefaultModel(value=value)


def create_name_reference_model(
    value: str = DEFAULT_NAME,
) -> NameReferenceModel:
    return NameReferenceModel(value=value)


def create_attribute_reference_model(
    value: Color = Color.RED,
) -> AttributeReferenceModel:
    return AttributeReferenceModel(value=value)


def create_empty_tuple_model(
    value: tuple[int, ...] = (),
) -> EmptyTupleModel:
    return EmptyTupleModel(value=value)


def create_tuple_literal_model(
    value: tuple[int, ...] = (1, 2),
) -> TupleLiteralModel:
    return TupleLiteralModel(value=value)


def create_singleton_tuple_model(
    value: tuple[int, ...] = (1,),
) -> SingletonTupleModel:
    return SingletonTupleModel(value=value)


def create_list_literal_model(
    value: list[int] = [1, 2],
) -> ListLiteralModel:
    return ListLiteralModel(value=value)


def create_dict_literal_model(
    value: dict[str, int] = {"a": 1, "b": 2},
) -> DictLiteralModel:
    return DictLiteralModel(value=value)


def create_basic_model(value: str = "basic") -> BasicModel:
    return BasicModel(value=value)


def create_call_default_model(
    value: BasicModel = create_basic_model(),
) -> CallDefaultModel:
    return CallDefaultModel(value=value)


def create_keyword_call_model(
    value: BasicModel = create_basic_model(value="keyword"),
) -> KeywordCallModel:
    return KeywordCallModel(value=value)


def create_nested_call_model(
    value: tuple[BasicModel, ...] = tuple([create_basic_model()]),
) -> NestedCallModel:
    return NestedCallModel(value=value)

def create_required_parameter_model(
    user_id: int,
    name: str = "unknown",
) -> RequiredParameterModel:
    return RequiredParameterModel(
        user_id=user_id,
        name=name,
    )
