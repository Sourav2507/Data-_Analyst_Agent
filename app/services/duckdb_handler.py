import duckdb

class DuckDBHandler:
    def __init__(self):
        self.conn = duckdb.connect(":memory:")
        # Install/load extensions
        self.conn.execute("INSTALL httpfs")
        self.conn.execute("LOAD httpfs")
        self.conn.execute("INSTALL parquet")
        self.conn.execute("LOAD parquet")

    def query(self, sql: str):
        return self.conn.execute(sql).fetchall()

    def close(self):
        self.conn.close()
