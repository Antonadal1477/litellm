"""
SQLAlchemy Session and Bounded Thread Executor for Dameng DM8 Database
Handles connection pooling and safe non-blocking async execution via asyncio.to_thread / bounded ThreadPoolExecutor.
"""

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional, TypeVar
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session

T = TypeVar("T")

class DamengSessionManager:
    """
    Manages SQLAlchemy Engine, Session factory, and bounded ThreadPoolExecutor
    for safe async-wrapped DM8 operations.
    """

    def __init__(
        self,
        connection_url: Optional[str] = None,
        pool_size: int = 20,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
        max_workers: int = 20,
    ):
        if not connection_url:
            db_user = os.getenv("DATABASE_USER", "LITELLM")
            db_pass = os.getenv("DATABASE_PASSWORD", "")
            db_host = os.getenv("DATABASE_HOST", "127.0.0.1")
            db_port = os.getenv("DATABASE_PORT", "5236")
            db_name = os.getenv("DATABASE_NAME", "LITELLM")
            connection_url = os.getenv(
                "DATABASE_URL",
                f"dm+dmPython://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}",
            )

        self.connection_url = connection_url
        self.pool_size = int(os.getenv("DATABASE_POOL_SIZE", pool_size))
        self.max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", max_overflow))
        self.pool_timeout = int(os.getenv("DATABASE_POOL_TIMEOUT", pool_timeout))
        self.pool_recycle = int(os.getenv("DATABASE_POOL_RECYCLE", pool_recycle))
        self.max_workers = int(os.getenv("DM_DB_WORKERS", max_workers))

        self.engine = None
        self.session_factory = None
        self.executor = None

    def initialize(self) -> None:
        if self.engine is not None:
            return

        # Handle SQLite fallback for local/unit testing if dm+dmPython driver is missing or url is sqlite
        url = self.connection_url
        if url.startswith("sqlite"):
            self.engine = create_engine(url, connect_args={"check_same_thread": False})
        else:
            self.engine = create_engine(
                url,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                pool_pre_ping=True,
            )

        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="dm_db_worker")

    def get_session(self) -> Session:
        if self.session_factory is None:
            self.initialize()
        return self.session_factory()

    async def run_in_db_thread(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Executes a synchronous DB function inside the bounded ThreadPoolExecutor
        without blocking the asyncio event loop.
        """
        if self.executor is None:
            self.initialize()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, lambda: func(*args, **kwargs))

    def close(self) -> None:
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
        if self.engine:
            self.engine.dispose()
            self.engine = None
