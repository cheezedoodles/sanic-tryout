import os
import uuid
from sanic import Sanic, text
from sanic.response import json
from sanic.exceptions import SanicException

from sanic_jwt import initialize, protected, inject_user

from tortoise.contrib.sanic import register_tortoise

from auth import registration, authenticate, retrieve_user
from models import Products, BankAccounts
from utils import ROWS_PER_PAGE


app = Sanic(__name__)
app.config.DB_URL = os.environ.get('DB_URL')
app.config.PRIVATE_KEY = os.environ.get('PRIVATE_KEY')

initialize(
    app,
    access_token_name='jwt',
    user_id='id',
    authenticate=authenticate,
    retrieve_user=retrieve_user
)
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


@app.get("/account/create")
@protected()
@inject_user()
async def create_account(request, user):
    bill_id = uuid.uuid4()
    account = await BankAccounts.create(user_id=user['id'],
                                        bill_id=bill_id)
    return json({'account_id': account.id}, status=200)


# @app.post("/payment/webhook")
# @protected()
# @inject_user()
# async def replenish_balance(request, user):
#     return json({'signature': '',
#                  'transaction_id': '',
#                  'user_id': '',
#                  'bill_id': '',
#                  'amount': ''})


register_tortoise(
    app,
    db_url=app.config.DB_URL,
    modules={'models': ['models']},
    generate_schemas=True
)


if __name__ == "__main__":
    app.run(port=5000)
