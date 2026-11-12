from dataclasses import dataclass


@dataclass(frozen=True)
class InteractionAccepted[ValueT]:
    value: ValueT


@dataclass(frozen=True)
class InteractionRejected:
    pass


@dataclass(frozen=True)
class InteractionCancelled:
    pass


type InteractionResult[ValueT] = (
    InteractionAccepted[ValueT] | InteractionRejected | InteractionCancelled
)
