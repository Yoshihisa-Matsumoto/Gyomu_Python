class GenericClass[T]:
    pass


class GenericPair[T, U]:
    pass


value_generic_simple: GenericClass[str]
value_generic_nested: GenericClass[list[str]]
value_generic_multiple: GenericPair[str, int]
value_generic_deep_nested: GenericClass[GenericPair[str, int]]
