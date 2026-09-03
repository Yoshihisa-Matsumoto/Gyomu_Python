from collections.abc import Callable
from typing import Literal

# 1. 通常：パラメータ1個、戻り値あり
value_callable_1: Callable[[Exception], bool]

# 2. 複数パラメータ、戻り値あり
value_callable_2: Callable[[str, bool, dict[str, str]], list[str]]

# 3. パラメータなし、戻り値あり
value_callable_3: Callable[[], str]

# 4. パラメータ1個、戻り値が None
value_callable_4: Callable[[str], None]

# 5. パラメータなし、戻り値が None
value_callable_5: Callable[[], None]

# 6. パラメータが複雑な型
value_callable_6: Callable[
    [list[str], dict[str, int], tuple[str, bool]],
    set[str],
]

# 7. パラメータに Union
value_callable_7: Callable[[str | None, int | float], bool]

# 8. 戻り値に Union
value_callable_8: Callable[[str], str | None]

# 9. Callable をパラメータに持つ
value_callable_9: Callable[[Callable[[str], int]], bool]

# 10. Callable を戻り値に持つ
value_callable_10: Callable[[str], Callable[[int], bool]]

# 11. Callable をパラメータ・戻り値の両方に持つ
value_callable_11: Callable[
    [Callable[[str], int]],
    Callable[[bool], str],
]

# 12. 引数が tuple 型
value_callable_12: Callable[[tuple[str, int]], bool]

# 13. 引数が Literal

value_callable_13: Callable[[Literal["foo"], Literal[1]], bool]

# 14. 引数が Optional 相当
value_callable_14: Callable[[str | None], None]

# 15. 任意の引数
value_callable_15: Callable[..., str]
