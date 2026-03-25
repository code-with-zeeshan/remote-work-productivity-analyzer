# database/connection.py
"""
Database connection pool management using psycopg2.
ALL database access goes through this class.
"""

from contextlib import contextmanager
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

from config.settings import db_config
from utils.logger import setup_logger

logger = setup_logger("database.connection")


class DatabasePool:
    """Manages PostgreSQL connection pooling and query execution."""

    def __init__(self) -> None:
        self.pool: SimpleConnectionPool | None = None
        self._create_pool()

    def _create_pool(self) -> None:
        """Create the connection pool."""
        try:
            self.pool = SimpleConnectionPool(
                minconn=db_config.min_connections,
                maxconn=db_config.max_connections,
                user=db_config.user,
                password=db_config.password,
                host=db_config.host,
                port=db_config.port,
                database=db_config.database,
            )
            logger.info(f"Connection pool created: {db_config.host}:{db_config.port}/{db_config.database}")
        except psycopg2.Error as e:
            logger.critical(f"Failed to create connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):  # type: ignore[return]
        """
        Context manager for getting a connection from the pool.
        Automatically returns connection to pool when done.
        """
        if self.pool is None:
            raise Exception("Connection pool not initialized")

        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Connection error: {e}")
            raise
        finally:
            if conn and self.pool is not None:
                self.pool.putconn(conn)

    def execute_query(self, query: str, params: tuple[Any, ...] | None = None) -> bool:
        """Execute a write query (INSERT, UPDATE, DELETE). Returns True on success."""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
                    return True
            except psycopg2.Error as e:
                conn.rollback()
                logger.error(f"Query execution error: {e}\nQuery: {query}")
                return False

    def execute_query_returning(self, query: str, params: tuple[Any, ...] | None = None) -> Any | None:
        """Execute a write query that returns a value (e.g., RETURNING id)."""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchone()
                    conn.commit()
                    return result[0] if result else None
            except psycopg2.Error as e:
                conn.rollback()
                logger.error(f"Query execution error: {e}\nQuery: {query}")
                return None

    def fetch_one(self, query: str, params: tuple[Any, ...] | None = None) -> tuple[Any, ...] | None:
        """Fetch a single row."""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchone()  # type: ignore[no-any-return]
            except psycopg2.Error as e:
                logger.error(f"Fetch error: {e}\nQuery: {query}")
                return None

    def fetch_all(self, query: str, params: tuple[Any, ...] | None = None) -> list[tuple[Any, ...]]:
        """Fetch all rows."""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall()  # type: ignore[no-any-return]
            except psycopg2.Error as e:
                logger.error(f"Fetch error: {e}\nQuery: {query}")
                return []

    def fetch_all_dict(self, query: str, params: tuple[Any, ...] | None = None) -> list[dict]:
        """Fetch all rows as dictionaries."""
        with self.get_connection() as conn:
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall()  # type: ignore[no-any-return]
            except psycopg2.Error as e:
                logger.error(f"Fetch error: {e}\nQuery: {query}")
                return []

    def close_all(self) -> None:
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("All database connections closed")
