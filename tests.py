import unittest

import arrow

from database import Base, db, BasketModel, ItemModel, ProductModel, PriceModel
from database_interface import DatabaseInterface
from resources import Basket, Item, Price, PriceType, Product


class ResourceTests(unittest.TestCase):
    @staticmethod
    def _create_dummy_basket():
        items = []
        for i in range(1, 5):
            prices = [Price(amount=i, price_type=price_type) for price_type in PriceType]
            product = Product("name", "description", prices, 123)
            items.append(Item(amount=i, product=product))
        return Basket('1234', 'owner', arrow.utcnow(), arrow.utcnow(), items)

    @classmethod
    def test_basket_total_prices_count(cls):
        basket = cls._create_dummy_basket()
        assert len(basket.get_all_prices()) == 4

    @classmethod
    def test_basket_prices(cls):
        basket = cls._create_dummy_basket()
        for price in basket.get_all_prices():
            assert isinstance(price, Price)


class DatabaseInterfaceTests(unittest.TestCase):

    def setUp(self):
        db.connect('sqlite:///:memory:')
        Base.metadata.create_all(db._engine)

    def tearDown(self):
        Base.metadata.drop_all(db._engine)

    @staticmethod
    def test_get_basket():
        basket = BasketModel(reference_number='test_number', owner_name='owner')

        db.session.add(basket)
        db.session.commit()
        result = DatabaseInterface.get_basket_by_reference_number('test_number')
        assert isinstance(result, Basket)

    @staticmethod
    def _create_dummy_basket():
        prices = [PriceModel(amount=3, price_type=price_type) for price_type in PriceType]
        product = ProductModel(name="name", description="description", prices=prices)

        db.session.add(product)
        db.session.commit()

        items = [ItemModel(amount=4, product=product), ItemModel(amount=10, product=product)]
        basket = BasketModel(reference_number='test_number', owner_name='owner', items=items)

        db.session.add(basket)
        db.session.commit()

    @classmethod
    def test_get_basket_with_correct_content(cls):
        cls._create_dummy_basket()
        result = DatabaseInterface.get_basket_by_reference_number('test_number')
        result.get_all_prices()

    @classmethod
    def test_search_product_by_name(cls):
        cls._create_dummy_basket()
        result = DatabaseInterface.search_product_by_name('name')
        assert result

    @classmethod
    def test_search_product_by_substring(cls):
        cls._create_dummy_basket()
        result = [p for p in DatabaseInterface.search_product_by_substring('na')]
        assert result

    @classmethod
    def test_search_product_by_substring_not_found(cls):
        cls._create_dummy_basket()
        result = [p for p in DatabaseInterface.search_product_by_substring('ka')]
        assert not result

if __name__ == '__main__':
    unittest.main()
