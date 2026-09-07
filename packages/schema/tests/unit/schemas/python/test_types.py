from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    SymbolId,
)


def test_declaration_identity_is_hashable() -> None:
    identity = DeclarationIdentity(
        symbol_id=SymbolId("test.user::User"),
        declaration_id=DeclarationId(".::User"),
    )

    assert hash(identity) == hash(identity)
