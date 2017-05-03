from sqlalchemy.orm import joinedload

from database import BasketModel, db, ProductModel, PriceModel
from resources import Basket, Item, Product, Price, PriceType


class ProductNotFoundException(Exception):
    pass


class ResourceUtils:
    @staticmethod
    def get_product_from_model(product_model):
        prices = [Price.create(amount=p.amount, price_type=p.price_type, id=p.id) for p in product_model.prices]
        product = Product(id=product_model.id, name=product_model.name,
                          description=product_model.description, prices=prices)
        return product


class DatabaseInterface:
    """ Combines the database models with the application resources """

    @staticmethod
    def get_all_products(order_by_name=False) -> 'List[Product]':
        if order_by_name:
            return [ResourceUtils.get_product_from_model(product) for product
                    in db.session.query(ProductModel).order_by(ProductModel.name).all()]
        else:
            return [ResourceUtils.get_product_from_model(product) for product
                    in db.session.query(ProductModel).all()]

    @staticmethod
    def get_basket_by_reference_number(reference_number: 'str') -> Basket:
        """ Build the resources from database query """

        basket_model = db.session.query(BasketModel).options(joinedload('items').joinedload('product').
                                                             joinedload('prices')).filter(BasketModel.reference_number
                                                                                          == reference_number).one()
        items = []
        for item in basket_model.items:
            product = ResourceUtils.get_product_from_model(item.product)
            item = Item.create(amount=item.amount, product=product)
            items.append(item)

        return Basket(
            reference_number=basket_model.reference_number,
            owner_name=basket_model.owner_name,
            created_at=basket_model.created_at,
            updated_at=basket_model.updated_at,
            items=items
        )

    @staticmethod
    def add_product(product: 'Product'):
        """ Persist product resource to database """
        prices = []
        for price in product.prices:
            price_model = PriceModel(
                amount=price.amount,
                price_type=price.price_type
            )
            prices.append(price_model)

        product_model = ProductModel(
            name=product.name,
            description=product.description,
            prices=prices,
            id=product.id
        )
        db.session.add(product_model)
        db.session.commit()

    @staticmethod
    def search_product_by_name(name: 'str') -> Product:
        product_model = db.session.query(ProductModel).yield_per(50).order_by(ProductModel.name).\
            filter(ProductModel.name == name).all()

        if not product_model:
            raise ProductNotFoundException("Product not found with name: {}".format(name))
        product_model = product_model[0]

        return ResourceUtils.get_product_from_model(product_model)

    @staticmethod
    def search_product_by_substring(substring: 'str') -> 'List[Product]':
        product_models = db.session.query(ProductModel).yield_per(50).order_by(ProductModel.name).\
            filter(ProductModel.name.contains(substring))

        for product in product_models:
            yield ResourceUtils.get_product_from_model(product)

    @staticmethod
    def remove_product_by_id(product_id):
        db.session.query(ProductModel).filter(ProductModel.id == product_id).delete()

    @classmethod
    def update_product_by_id(cls, product_id, name, description, prices):
        product = db.session.query(ProductModel).filter(ProductModel.id == product_id).one()
        product.name = name
        product.description = description

        for price in prices:
            price_model = db.session.query(PriceModel).filter(PriceModel.price_type == PriceType(price["price_type"]),
                                                              ProductModel.id == product.id).one()
            price_model.amount = price['amount']

        db.session.commit()

