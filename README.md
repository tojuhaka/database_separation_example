Simple product catalog software with isolated database code. The main beef of the software is to introduce by example how the database interactions should be isolated so that it easy to replace the database technology if needed. Also the business logic and API should be separated.

In database.py there are sqlalchemy specific classes. And database_interface.py acts as a clue between application specific logic and database logic. Api.py contains all the WEB related stuff. It would have been really fast to use only Flask and Flask-SQLAlchemy, but I wanted to implement this a little bit more abstract way so that we aren't stuck with web and database technologies so tightly. The downside is a little bit more code because we map the results from sqlalchemy to app-specific resources that are used by API. But that keeps all the parts web / db / resources isolated from each other.

Language: Python 3.6

Database solution: SQLite + SQLAlchemy

Framework for API: Flask Restful


`pip install -r requirements.txt`
`pytest tests.py`
`python api.py`


It would have been really fast to use only Flask and Flask-SQLAlchemy, but since there is plenty of time,
I wanted to implement this a little bit more abstract
way so that we aren't stuck with web and database technologies so tightly. The downside is a little bit more code because we map the results from sqlalchemy to app-speific resources that are used by API. But that keeps all the parts web / db / resources isolated from each other.


Usage examples:

create product:
`curl http://localhost:5000/products -d 'data={"name": "test-name", "description": "test-description", "prices": [{"amount": 5, "price_type": "one-time"}, {"amount": 4, "price_type": "recurring"}, {"amount": 20, "price_type": "usage"}]}' -X POST -v`

get all products:
`curl http://localhost:5000/products -X GET`

get product by exact name
`curl http://localhost:5000/products/product/test-name -X GET`

get product by name with wild card
`curl http://localhost:5000/products/product/te* -X GET`

delete product with id
`curl http://localhost:5000/products/product/2 -X DELETE`

update product:
`curl http://localhost:5000/products/product/1 -d 'data={"name": "changed-name", "description": "test-description", "prices": [{"amount": 50, "price_type": "one-time"}, {"amount": 4, "price_type": "recurring"}, {"amount": 100, "price_type": "usage"}]}' -X PUT`
