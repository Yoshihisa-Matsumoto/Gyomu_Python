from gyomu_schema.option.retry import RetryObserver

__OBSERVER: RetryObserver | None = None


def register_retry_observer(observer: RetryObserver) -> None:
    global __OBSERVER
    if __OBSERVER is None:
        __OBSERVER = observer
    else:
        raise ValueError("RetryObserver is already registered")


def _get_retry_observer() -> RetryObserver | None:
    return __OBSERVER
