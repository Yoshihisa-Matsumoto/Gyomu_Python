# from gyomu_infra.logger import logger
# from gyomu_python_analysis.resolve.type_dump import _convert_literal_to_code
# from gyomu_schema.schemas.config.test.model_defaults import (
#     AttributeParameter,
#     CallParameter,
#     DictParameter,
#     ListParameter,
#     LiteralParameter,
#     NameParameter,
#     NoneParameter,
#     Parameter,
#     TupleParameter,
# )
# from gyomu_schema.schemas.python.type.structure import (
#     LiteralValue,
#     NameStructureAnalysis,
#     NoneStructureAnalysis,
# )
# from gyomu_schema.schemas.python.type.type_analysis import (
#     ArrayStructureAnalysis,
#     AttributeStructureAnalysis,
#     DictionaryStructureAnalysis,
#     LiteralStructureAnalysis,
#     StructureAnalysis,
#     TupleStructureAnalysis,
#     TypeAnalysis,
#     TypeExpression,
#     UnionStructureAnalysis,
# )


# def _get_supporting_parameter_str_list(parameter: Parameter) -> str | None:

#     if isinstance(parameter, LiteralParameter):
#         return type(parameter.value).__name__
#     elif isinstance(parameter, NoneParameter):
#         return "None"
#     elif isinstance(parameter, NameParameter):
#         return parameter.name
#     elif isinstance(parameter, CallParameter):
#         return parameter.callable_identity.symbol_id
#     elif isinstance(parameter, AttributeParameter):
#         value = _get_supporting_parameter_str_list(parameter.value)
#         if value is None:
#             return None
#         return value + f".{parameter.attribute}"
#     else:
#         return None


# def _get_supporting_type_str_list(
#     expression: TypeExpression, value_display: bool = False
# ) -> tuple[str, ...] | None:
#     result: list[str] = []
#     if isinstance(expression, LiteralValue):
#         if not value_display:
#             result.append(type(expression.value).__name__)
#         else:
#             result.append(_convert_literal_to_code(expression.value))
#     elif isinstance(expression, NoneStructureAnalysis):
#         result.append("None")
#     elif isinstance(expression, NameStructureAnalysis):
#         result.append(expression.name)
#     elif isinstance(expression, LiteralStructureAnalysis):
#         children = _get_supporting_type_str_list(
#             expression=expression.value, value_display=True
#         )
#         if children is None:
#             return None
#         else:
#             for child_str in children:
#                 result.append(f"Literal({child_str})")
#     elif isinstance(expression, UnionStructureAnalysis):
#         union: list[str] = []
#         for child in expression.types:
#             child_result = _get_supporting_type_str_list(expression=child)
#             if child_result is not None:
#                 union.extend(child_result)
#             else:
#                 return None
#         if len(union) == 0:
#             return None
#         result.extend(union)
#     elif isinstance(expression, AttributeStructureAnalysis):
#         attributes: list[str] = []
#         for child in expression.values:
#             child_result = _get_supporting_type_str_list(expression=child)
#             if child_result is not None:
#                 attributes.extend(child_result)
#         if len(attributes) == 0:
#             return None
#         result.append(".".join(attributes))
#     else:
#         return None

#     return tuple(result)


# def _validate_parameter_from_structure(
#     structure: StructureAnalysis, default: Parameter
# ) -> Parameter | None:
#     support_type_str_list = _get_supporting_type_str_list(structure)
#     if isinstance(default, NoneParameter):
#         return (
#             None
#             if support_type_str_list is None or "None" not in support_type_str_list
#             else default
#         )
#     if isinstance(default, LiteralParameter):
#         return (
#             default
#             if support_type_str_list is not None
#             and type(default.value).__name__ in support_type_str_list
#             else None
#         )
#     if isinstance(default, NameParameter):
#         return (
#             None
#             if support_type_str_list is None
#             or default.name not in support_type_str_list
#             else default
#         )
#     # if isinstance(default,CallParameter):
#     #     default.callable_identity.get_symbol_name()
#     parameter_strs: list[str] = []
#     if isinstance(default, TupleParameter):
#         if not isinstance(structure, TupleStructureAnalysis):
#             return None

#         type_strs: list[tuple[str, ...]] = []

#         for default_element in default.elements:
#             default_str = _get_supporting_parameter_str_list(default_element)
#             if default_str is None:
#                 return None
#             parameter_strs.append(default_str)

#         for type_element in structure.elements:
#             type_str = _get_supporting_type_str_list(type_element)
#             if type_str is None:
#                 continue
#             type_strs.append(type_str)

#         if len(type_strs) == 1:
#             for param in parameter_strs:
#                 if param not in type_strs[0]:
#                     return None
#             return default
#         else:
#             if len(type_strs) != len(parameter_strs):
#                 return None
#             for index, param in enumerate(parameter_strs):
#                 type_str = type_strs[index]
#                 if param not in type_str:
#                     return None
#             return default
#     if isinstance(default, ListParameter):
#         if not isinstance(structure, ArrayStructureAnalysis):
#             return None
#         for default_element in default.elements:
#             default_str = _get_supporting_parameter_str_list(default_element)
#             if default_str is None:
#                 return None
#             parameter_strs.append(default_str)

#         list_type_strs = _get_supporting_type_str_list(structure.element)
#         if list_type_strs is None:
#             return None

#         for parameter_str in parameter_strs:
#             if parameter_str not in list_type_strs:
#                 return None
#         return default

#     elif isinstance(default, DictParameter):
#         if not isinstance(structure, DictionaryStructureAnalysis):
#             return None
#         if structure.keys is None or structure.values is None:
#             return None

#         key_strs = _get_supporting_type_str_list(structure.keys)
#         value_strs = _get_supporting_type_str_list(structure.values)
#         if key_strs is None or value_strs is None:
#             return None

#         for entry in default.entries:
#             key_param = _get_supporting_parameter_str_list(entry.key)
#             value_param = _get_supporting_parameter_str_list(entry.value)
#             if key_param not in key_strs or value_param not in value_strs:
#                 return None
#         return default
#     else:
#         # Not Support yet (DictParameter/LambdaParameter)
#         return default


# def validate_parameter(
#     type_analysis: TypeAnalysis, default: Parameter
# ) -> Parameter | None:
#     if type_analysis.structure is None:
#         is_text_valid = True
#         if isinstance(default, LiteralParameter):
#             is_text_valid = type(default.value).__name__ == type_analysis.text
#             if is_text_valid:
#                 return default
#             else:
#                 logger.error(
#                     f"Type: {type_analysis.text} not match with Parameter: "
#                     f"{type(default.value).__name__}"
#                 )
#                 return None
#         if isinstance(default, NoneParameter):
#             if type_analysis.text == "None":
#                 return default
#             else:
#                 logger.error(
#                     f"Type: {type_analysis.text} not match with Parameter: None"
#                 )
#                 return None

#         return None
#     else:
#         return _validate_parameter_from_structure(type_analysis.structure, default)
