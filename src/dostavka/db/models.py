import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)

    packages = relationship("Package", back_populates="session")


class PackageType(Base):
    __tablename__ = "package_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    packages = relationship("Package", back_populates="package_type")


class Package(Base):
    __tablename__ = "packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    weight = Column(Float, nullable=False)
    type_id = Column(Integer, ForeignKey("package_types.id"), nullable=False)
    price = Column(Float, nullable=False)
    shipping_cost = Column(String(50), nullable=True)  # Может быть "Не рассчитано" или число в строке
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)

    package_type = relationship("PackageType", back_populates="packages")
    session = relationship("Session", back_populates="packages")


class Ship(Base):
    __tablename__ = "shippings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    package_id = Column(UUID(as_uuid=True), ForeignKey("packages.id"), nullable=False)
    shipping_cost = Column(Float, nullable=False)

    package = relationship("Package")
