"""
Модели базы данных.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PackageType(Base):
    """Модель типа посылки."""
    __tablename__ = "package_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    # Связь с посылками
    packages = relationship("Package", back_populates="type")


class Session(Base):
    """Модель сессии пользователя."""
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связь с посылками
    packages = relationship("Package", back_populates="session")


class Package(Base):
    """Модель посылки."""
    __tablename__ = "packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    weight = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    shipping_cost = Column(String(50), default="Не рассчитано")
    
    # Внешние ключи
    type_id = Column(Integer, ForeignKey("package_types.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)

    # Связи
    type = relationship("PackageType", back_populates="packages")
    session = relationship("Session", back_populates="packages")
