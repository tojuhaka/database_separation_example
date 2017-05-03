import enum
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from datetime import datetime


class Product:
    def __init__(self, name: 'str', description: 'str', prices: 'List[Price]', id: 'int' = None):
        self.id = id
        self.name = name
        self.description = description
        self.prices = prices

    @classmethod
    def create(cls, id: 'int', name: 'str', description: 'str', prices: 'List[Price]'):
        return cls(id, name, description, prices)

    def get_price(self, one_time: 'PriceType'):
        return [price for price in self.prices if price.price_type == one_time][0]


class Basket:
    def __init__(self, reference_number: 'str', owner_name: 'str', created_at: 'datetime',
                 updated_at: 'datetime', items: 'List[Item]'):
        self.created_at = created_at
        self.updated_at = updated_at
        self.reference_number = reference_number
        self.owner_name = owner_name
        self.items = items

    def get_all_prices(self) -> 'List[Price]':
        return [item.get_default_price() for item in self.items]


class PriceType(enum.Enum):
    recurring = 'recurring'
    one_time = 'one-time'
    usage = 'usage'

    def __str__(self):
        return str(self.value)


class Item:
    def __init__(self, amount: 'int', product: 'Product'):
        self.amount = amount
        self.product = product

    @classmethod
    def create(cls, amount: 'int', product: 'Product'):
        return cls(amount, product)

    def get_default_price(self):
        return self.product.get_price(PriceType.one_time)


class Price:
    def __init__(self, amount: 'int', price_type: 'PriceType', id: 'int' = None):
        self.price_type = price_type
        self.amount = amount
        self.id = id

    @classmethod
    def create(cls, amount: 'int', price_type: 'PriceType', id: 'int' = None):
        return cls(amount, price_type, id)

