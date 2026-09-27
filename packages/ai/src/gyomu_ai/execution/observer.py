from gyomu_schema.option.retry import RetryObserver

__OBSERVER: RetryObserver | None = None
"""Global retry observer instance."""


def register_retry_observer(observer: RetryObserver) -> None:
    """Registers a global retry observer.

    Args:
        observer (RetryObserver): The retry observer to register.

    Returns:
        None: None

    Raises:
        ValueError: If a retry observer is already registered.
    """
    global __OBSERVER
    if __OBSERVER is None:
        __OBSERVER = observer
    else:
        raise ValueError("RetryObserver is already registered")


def _get_retry_observer() -> RetryObserver | None:
    """Retrieves the currently registered retry observer.

    Returns:
        RetryObserver | None: The registered retry observer, or None if not registered.
    """
    return __OBSERVER
