from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import duckdb


def register_all(conn: "duckdb.DuckDBPyConnection") -> None:
    from . import phone
    from . import address

    phone.register(conn)
    address.register(conn)
