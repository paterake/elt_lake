"""SQL transformation executor for DuckDB."""

from dataclasses import dataclass
from pathlib import Path

import duckdb


@dataclass
class TransformResult:
    """Result of executing a transform SQL file.

    Attributes:
        sql_file: Name of the SQL file executed.
        success: Whether execution succeeded.
        error: Error message if failed, None otherwise.
    """

    sql_file: str
    success: bool
    error: str | None = None


class SqlExecutor:
    """Executes SQL transformation files against a DuckDB database.

    Reads an order.txt file to determine execution order and runs
    each SQL file sequentially.
    """

    def __init__(self, transform_path: Path, database_path: Path):
        """Initialize the SQL executor.

        Args:
            transform_path: Path to directory containing SQL files and order.txt.
            database_path: Path to the DuckDB database file.
        """
        self.transform_path = Path(transform_path)
        self.database_path = Path(database_path)

    def execute(self) -> list[TransformResult]:
        """Execute all SQL files in order.

        Reads order.txt from transform_path and executes each SQL file
        listed in sequence.

        Returns:
            List of TransformResult objects for each SQL file executed.
        """
        order_file = self.transform_path / "order.txt"
        if not order_file.exists():
            return []

        sql_files = self._read_order_file(order_file)
        results = []

        with duckdb.connect(str(self.database_path)) as conn:
            for sql_file in sql_files:
                result = self._execute_sql_file(conn, sql_file)
                results.append(result)

        return results

    def _read_order_file(self, order_file: Path) -> list[str]:
        """Read order.txt and return list of SQL file names.

        Args:
            order_file: Path to order.txt file.

        Returns:
            List of SQL file names to execute.
        """
        content = order_file.read_text()
        files = []
        for line in content.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):  # Skip empty lines and comments
                files.append(line)
        return files

    def _execute_sql_file(
        self,
        conn: duckdb.DuckDBPyConnection,
        sql_file: str,
    ) -> TransformResult:
        """Execute a single SQL file.

        Args:
            conn: DuckDB connection.
            sql_file: Name of the SQL file to execute.

        Returns:
            TransformResult with execution status.
        """
        sql_path = self.transform_path / sql_file
        print(f"\n  Executing: {sql_file}")

        if not sql_path.exists():
            error = f"SQL file not found: {sql_path}"
            print(f"    ERROR: {error}")
            return TransformResult(sql_file=sql_file, success=False, error=error)

        try:
            sql_content = sql_path.read_text()

            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql_content.split(";") if s.strip()]

            for i, statement in enumerate(statements, 1):
                if statement:
                    conn.execute(statement)
                    print(f"    Statement {i} executed")

            print("    SUCCESS")
            return TransformResult(sql_file=sql_file, success=True)

        except Exception as e:
            error = str(e)
            print(f"    ERROR: {error}")
            return TransformResult(sql_file=sql_file, success=False, error=error)

    def get_sql_file_count(self) -> int:
        """Get the number of SQL files to execute.

        Returns:
            Number of SQL files listed in order.txt, or 0 if not found.
        """
        order_file = self.transform_path / "order.txt"
        if not order_file.exists():
            return 0
        return len(self._read_order_file(order_file))
