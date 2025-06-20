# orders/orders/models.py (Proposed)
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # For timestamps if needed

# Define a base for your SQLAlchemy models
Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    reservasi_id = Column(Integer, nullable=True)
    event_id = Column(Integer, nullable=True)
    voucher_id = Column(Integer, nullable=True)
    order_type = Column(Enum('DINE IN', 'DELIVERY', 'RESERVASI', 'EVENT', name='order_type_enum'), nullable=False)
    total_payment = Column(Float, nullable=False)

    # Relationships to order_details and order_packages (optional for schema, but good practice)
    details = relationship("OrderDetail", back_populates="order")
    packages = relationship("OrderPackage", back_populates="order")

class OrderDetail(Base):
    __tablename__ = 'order_details'
    order_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    menu_id = Column(Integer, nullable=False)
    chef_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    note = Column(String(100), nullable=False)
    status = Column(Enum('PENDING', 'ON DELIVERY', 'COMPLETED', '', name='order_detail_status_enum'), nullable=False)

    order = relationship("Order", back_populates="details")

class OrderPackage(Base):
    __tablename__ = 'order_packages'
    order_package_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.order_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    menu_package_id = Column(Integer, nullable=False)
    chef_id = Column(Integer, nullable=True) # chef_id is NULLABLE in your SQL dump
    quantity = Column(Integer, nullable=False)
    note = Column(String(100), nullable=False)
    status = Column(Enum('PENDING', 'ON DELIVERY', 'COMPLETED', '', name='order_package_status_enum'), nullable=False)

    order = relationship("Order", back_populates="packages")

# You might put this in a separate config or dependency file,
# but for Alembic, you usually just import Base.metadata.
# For example, in dependencies.py you might create the engine:
# from orders.models import Base
# engine = create_engine(your_db_url)
# Base.metadata.create_all(engine) # Only for creating tables from scratch, not for migrations