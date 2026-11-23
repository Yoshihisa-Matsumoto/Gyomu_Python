def create_user_summary(

    user_id: int = 1,

    display_name: str = "dis",

) -> UserSummary:

    return UserSummary(

        user_id=user_id,

        display_name=display_name,

    )
