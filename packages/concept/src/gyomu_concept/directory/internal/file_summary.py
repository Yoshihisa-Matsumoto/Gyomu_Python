from gyomu_schema.schemas.concept.file_summary import FileSummary
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext


def build_file_summary_record(context: FileAnalysisContext) -> FileSummary: ...
