import os
from sanic import Sanic, text
from sanic.response import json
from sanic.exceptions import SanicException

from sanic_jwt import initialize, protected

from tortoise.contrib.sanic import register_tortoise

from auth import registration, authenticate
from models import Products
from utils import ROWS_PER_PAGE


app = Sanic(__name__)
app.config.DB_URL = os.environ.get('DB_URL')
initialize(app, access_token_name='jwt', authenticate=authenticate)
app.blueprint(registration)


@app.get("/")
@protected()
async def hello_world(request):
    return text('welcome')


@app.get("/goods/page/<page:int>")
async def get_goods(request, page):
    """
    returns a list of goods (in quantity of ROWS_PER_PAGE)
    """
    if page <= 0:
        raise SanicException("Invalid page number", status_code=400)
    limit = ROWS_PER_PAGE * page
    offset = ROWS_PER_PAGE * (page - 1)
    # next = page + 1
    products = await Products.all().offset(offset=offset)\
                                   .limit(limit=limit)\
                                   .values()
    # if len(products) < ROWS_PER_PAGE:
    #     next = None
    # products.append({'next': next})
    return json(products)


register_tortoise(
    app,
    db_url=app.config.DB_URL,
    modules={'models': ['models']},
    generate_schemas=True
)


if __name__ == "__main__":
    app.run(port=5000)
