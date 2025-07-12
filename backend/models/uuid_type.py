"""
Cross-database compatible UUID type for SQLAlchemy.

This module provides a UUID type that works with both SQLite and PostgreSQL:
- SQLite: Stores UUIDs as strings (CHAR(36))
- PostgreSQL: Uses native UUID type
"""

import uuid
from sqlalchemy import TypeDecorator, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID


class UUID(TypeDecorator):
    """
    Cross-database UUID type.
    
    Uses PostgreSQL's native UUID type when available,
    falls back to String(36) for other databases like SQLite.
    """
    
    impl = String
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        """Load the appropriate implementation based on the database dialect."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        else:
            # For SQLite and other databases, use String(36)
            return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value, dialect):
        """Process values being sent to the database."""
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            # For SQLite, convert UUID to string
            if isinstance(value, uuid.UUID):
                return str(value)
            return value
    
    def process_result_value(self, value, dialect):
        """Process values coming from the database."""
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            # For SQLite, convert string back to UUID
            if isinstance(value, str):
                return uuid.UUID(value)
            return value