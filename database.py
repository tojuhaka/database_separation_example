import arrow
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import Unicode
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session as sqla_scoped_session, relationship

from resources import PriceType


class DBConnection(object):
    def __init__(self) -> object:
        self._engine = None
        self.new_session = None
        self.session = None

    def connect(self, address):
        self._engine = create_engine(address, pool_recycle=3600)
        self.new_session = sessionmaker(bind=self._engine, autoflush=False, autocommit=False)
        self.session = sqla_scoped_session(self.new_session)
        print("DB: Connected")

    def finish_session(self):
        """
        Finishes the currently open session. This should be called after every request.
        Please see sqlalchemy documentation about scoped_sessions !
        """
        self.session.remove()

    def rollback(self):
        self.session.rollback()

    def commit(self):
        self.session.commit()

    def close(self):
        if self.session:
            self.session.remove()
            self.session = None
        self.new_session = None
        if self._engine:
            self._engine.dispose()
            self._engine = None

Base = declarative_base()


class BasketModel(Base):
    __tablename__ = "basket"
    id = Column(Integer, primary_key=True)

    owner_name = Column(Unicode(64), nullable=True, default=None, index=True)
    reference_number = Column(Unicode(32), nullable=True, default=None, index=True)
    created_at = Column(DateTime(timezone=True), default=arrow.utcnow().datetime, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=arrow.utcnow().datetime, nullable=False, index=True)
    items = relationship("ItemModel", backref="item")


class ProductModel(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)

    name = Column(Unicode(64), nullable=False, default=None, index=True)
    description = Column(Text(), nullable=False, default=None, index=True)
    prices = relationship("PriceModel", backref="price")


class ItemModel(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)

    basket = Column(Integer, ForeignKey('basket.id'), nullable=False)
    amount = Column(Integer, nullable=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship("ProductModel")


class PriceModel(Base):
    __tablename__ = "price"
    id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=True)
    product = Column(Integer, ForeignKey('product.id'), nullable=False)
    price_type = Column(Enum(PriceType), index=True)


db = DBConnection()
