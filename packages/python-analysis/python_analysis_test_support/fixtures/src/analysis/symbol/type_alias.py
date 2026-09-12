from typing import Literal

type UserId = int
type UserList = list[UserId]
type UserValue = UserId | None
type Status = Literal["active", "inactive"]
