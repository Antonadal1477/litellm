"""
Base Database Interface for LiteLLM DB Abstraction
Provides abstract interfaces and neutral error types for PostgreSQL and DM8 backends.
"""

from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod


# --- Database Exceptions ---

class DatabaseError(Exception):
    """Base exception for all database operations."""
    pass

class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails or times out."""
    pass

class DatabaseTimeoutError(DatabaseError):
    """Raised when a query or transaction times out."""
    pass

class DatabaseIntegrityError(DatabaseError):
    """Raised when unique or foreign key constraints fail."""
    pass

class DatabaseNotFoundError(DatabaseError):
    """Raised when expected record is not found."""
    pass

class DatabaseConflictError(DatabaseError):
    """Raised on concurrent modification or deadlock conflict."""
    pass


# --- Abstract Model Handle Interface ---

class BaseModelHandle(ABC):
    """
    Abstract Model Handle defining standard CRUD / Prisma-like operations
    for a specific table.
    """

    @abstractmethod
    async def find_unique(self, where: Dict[str, Any], include: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        pass

    @abstractmethod
    async def find_first(
        self,
        where: Optional[Dict[str, Any]] = None,
        order: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        include: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        pass

    @abstractmethod
    async def find_many(
        self,
        where: Optional[Dict[str, Any]] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None,
        order: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
        include: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        pass

    @abstractmethod
    async def create(self, data: Dict[str, Any], include: Optional[Dict[str, Any]] = None) -> Any:
        pass

    @abstractmethod
    async def create_many(self, data: List[Dict[str, Any]], skip_duplicates: Optional[bool] = None) -> int:
        pass

    @abstractmethod
    async def update(
        self,
        where: Dict[str, Any],
        data: Dict[str, Any],
        include: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        pass

    @abstractmethod
    async def update_many(self, where: Dict[str, Any], data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    async def delete(self, where: Dict[str, Any]) -> Optional[Any]:
        pass

    @abstractmethod
    async def delete_many(self, where: Optional[Dict[str, Any]] = None) -> int:
        pass

    @abstractmethod
    async def upsert(
        self,
        where: Dict[str, Any],
        data: Dict[str, Any],
        include: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        data param should contain 'create' and 'update' dicts matching Prisma semantics,
        or a flat dictionary if normalized by implementation.
        """
        pass

    @abstractmethod
    async def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        pass

    @abstractmethod
    async def group_by(
        self,
        by: List[str],
        where: Optional[Dict[str, Any]] = None,
        sum: Optional[Dict[str, bool]] = None,
        count: Optional[Dict[str, bool]] = None,
        avg: Optional[Dict[str, bool]] = None,
        min: Optional[Dict[str, bool]] = None,
        max: Optional[Dict[str, bool]] = None,
        having: Optional[Dict[str, Any]] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None,
        order: Optional[Union[Dict[str, str], List[Dict[str, str]]]] = None,
    ) -> List[Dict[str, Any]]:
        pass


# --- Abstract Database Backend Interface ---

class BaseDatabaseBackend(ABC):
    """
    Abstract Database Backend representing the entry point for DB connections
    and table handles.
    """

    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def transaction(self) -> Any:
        """
        Context manager interface for async transactions:
        async with db.transaction():
            ...
        """
        pass

    # Standard model accessor dynamic lookup or property getter
    @abstractmethod
    def get_model_handle(self, table_name: str) -> BaseModelHandle:
        pass
