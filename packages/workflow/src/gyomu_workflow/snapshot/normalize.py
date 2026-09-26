from gyomu_workflow.snapshot.models import SnapshotTargetOption


def normalize_filter(option: SnapshotTargetOption) -> None:
    """Normalizes the file filter pattern within a snapshot target option.

    Args:
        option (SnapshotTargetOption): The snapshot target option to normalize.
    """
    if option.file_filter is None:
        return
    option.file_filter.pattern = _normalize_snapshot_filter(option.file_filter.pattern)


def _normalize_snapshot_filter(
    filter: str,
) -> str:
    """Normalizes a snapshot filter pattern string.

    Args:
        filter (str): The filter pattern string to normalize.

    Returns:
        str: The normalized filter pattern string.
    """

    if filter.endswith("/*"):
        return f"**/{filter[:-2]}/**"

    return filter
