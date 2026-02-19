from pathlib import Path
from typing import TYPE_CHECKING

import duckdb

from ..models import TransformResult

if TYPE_CHECKING:
    from ..reporting import PipelineReporter


class SqlFileExecutor:
    def __init__(self, transform_path: Path, reporter: "PipelineReporter | None" = None):
        self.transform_path = Path(transform_path)
        self.reporter = reporter

    def run(
        self,
        conn: duckdb.DuckDBPyConnection,
        sql_file: str,
    ) -> TransformResult:
        sql_path = self.transform_path / sql_file
        if self.reporter:
            self.reporter.print_sql_file_start(sql_file)
        if not sql_path.exists():
            error = f"SQL file not found: {sql_path}"
            if self.reporter:
                self.reporter.print_sql_file_not_found(sql_file, str(sql_path))
            return TransformResult(sql_file=sql_file, success=False, error=error)
        try:
            sql_content = sql_path.read_text()
            statements = conn.extract_statements(sql_content)
            for i, statement in enumerate(statements, 1):
                try:
                    conn.execute(statement)
                except Exception as e:
                    msg = f"Statement {i} failed: {e}"
                    if self.reporter:
                        self.reporter.print_sql_file_error(msg)
                    return TransformResult(sql_file=sql_file, success=False, error=msg)
                if self.reporter:
                    self.reporter.print_sql_statement_executed(i)
            if self.reporter:
                self.reporter.print_sql_file_success()
            return TransformResult(sql_file=sql_file, success=True)
        except Exception as e:
            error = str(e)
            if self.reporter:
                self.reporter.print_sql_file_error(error)
            return TransformResult(sql_file=sql_file, success=False, error=error)
