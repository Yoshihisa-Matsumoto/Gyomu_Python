from gyomu_workflow.snapshot.models import SnapshotTargetOption


def normalize_filter(option: SnapshotTargetOption) -> None:
    if option.file_filter is None:
        return
    option.file_filter.pattern = _normalize_snapshot_filter(option.file_filter.pattern)


def _normalize_snapshot_filter(
    filter: str,
) -> str:

    if filter.endswith("/*"):
        return f"{filter[:-2]}/**/*"

    return filter
