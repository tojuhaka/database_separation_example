import json

from flask import Flask
from flask.ext.restful import reqparse
from flask_restful import fields, abort
from flask_restful import Resource, Api, marshal_with

from database import db, Base
from database_interface import DatabaseInterface, ProductNotFoundException
from resources import Product, Price, PriceType

app = Flask(__name__)
api = Api(app)


HOSTNAME = 'http://localhost:5000' # TODO: find from request


class Relationships(fields.Raw):
    def format(self, value):
        return {
            'prices': {
                'data': [{'type': 'price', 'id': pr.id} for pr in value]
            }
        }

class ProductLinks(fields.Raw):
    def format(self, value):
        return {
            'self': '{}/products/product/{}'.format(HOSTNAME, value)
        }

class Included(fields.Raw):
    def format(self, value):
        _list = []
        for price in value:
            _list.append({
                'type': 'price',
                'id': price.id,
                'attributes': {
                    'amount': price.amount,
                    'price_type': str(price.price_type)
                },
                'links': {
                    'self': '{}/prices/{}'.format(HOSTNAME, price.id)
                }
            })
        return _list

product_fields = {
    'type': fields.String('product'),
    'name':   fields.String,
    'description':    fields.String,
    'id': fields.Integer,
    'relationships': Relationships(attribute='prices'),
    'links': ProductLinks(attribute='id'),
    'included': Included(attribute='prices')

}


parser = reqparse.RequestParser()
parser.add_argument('data', type=str)
parser.add_argument('sort', type=bool, default=False)


class ProductsAPI(Resource):
    @marshal_with(product_fields, envelope='data')
    def get(self):
        arguments = parser.parse_args()
        return DatabaseInterface.get_all_products(arguments['sort'])

    def post(self):
        arguments = parser.parse_args()
        data = json.loads(arguments['data'])

        product = Product(
            name=data['name'],
            description=data['description'],
            prices=[Price(pr['amount'], PriceType(pr['price_type'])) for pr in data['prices']]
        )

        DatabaseInterface.add_product(product)

        return {'task': arguments['data']}


class ProductByIdAPI(Resource):
    @marshal_with(product_fields)
    def get(self, id):
        # TODO: get by product id
        abort(404, message="Product with id {} does not exist".format(id))

    def delete(self, id):
        DatabaseInterface.remove_product_by_id(id)
        return {'message': 'Deleted product with id: {}'.format(id)}

    def put(self, id):
        arguments = parser.parse_args()
        data = json.loads(arguments['data'])

        DatabaseInterface.update_product_by_id(id, data['name'], data['description'], data['prices'])


class ProductByNameAPI(Resource):
    @marshal_with(product_fields)
    def get(self, name):
        """ Possible to search with wild card also /products/na*. If star is is missing then the exact
            match will be searched """
        try:
            if name.endswith('*'):
                result = [i for i in DatabaseInterface.search_product_by_substring(name[:-1])]
                if not result:
                    abort(404, message="Product with name {} does not exist".format(name))
                return result
            else:
                return DatabaseInterface.search_product_by_name(name)
        except ProductNotFoundException:
            abort(404, message="Product with name {} does not exist".format(name))


api.add_resource(ProductByNameAPI, '/products/product/<string:name>')
api.add_resource(ProductByIdAPI, '/products/product/<int:id>')
api.add_resource(ProductsAPI, '/products')

if __name__ == '__main__':
        db.connect('sqlite:///:memory:')
        Base.metadata.create_all(db._engine)
        app.run(debug=False)
