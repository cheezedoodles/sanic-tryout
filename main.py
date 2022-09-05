import os
import uuid
from sanic import Sanic, text
from sanic.response import json
from sanic.exceptions import SanicException

from sanic_jwt import initialize, protected, inject_user

from tortoise.contrib.sanic import register_tortoise
from tortoise.exceptions import DoesNotExist

from auth import registration, authenticate, retrieve_user
from models import Products, BankAccounts, Transactions, Users
from utils import ROWS_PER_PAGE, generate_signature


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


@app.get("/products/page/<page:int>")
async def get_products(request, page):
    """
    returns a list of products (in quantity of ROWS_PER_PAGE)
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


@app.post("/products/<product_id:int>")
@protected()
@inject_user()
async def buy_product(request, product_id, user):
    """
    endpoint for buying a product:
    requires a bill_id that has required amount of money,
    otherwise returns 400
    """
    bill_id = request.json.get('bill_id', None)
    try:
        product = await Products.get(pk=product_id)
    except DoesNotExist:
        return json({}, status=400)

    account = await BankAccounts.get_or_none(bill_id=bill_id,
                                             user_id=user['id'])
    if account and account.balance >= product.price:
        account.balance -= product.price
        await account.save()
        return json({"balance": account.balance}, status=200)
    return json({}, status=400)


@app.get("/account/create")
@protected()
@inject_user()
async def create_account(request, user):
    """
    creates a new bank account
    """
    bill_id = uuid.uuid4()
    account = await BankAccounts.create(user_id=user['id'],
                                        bill_id=bill_id)
    return json({'bill_id': str(account.bill_id)}, status=200)


@app.post("/payment/webhook")
@protected()
async def replenish_balance(request):
    """
    endpoint that replenishes balance: creates a transaction and
    returns information about it
    expects bill_id and amount, returns 400 otherwise
    """
    bill_id = request.json.get('bill_id', None)
    username = request.json.get('username', None)
    amount = request.json.get('amount', None)
    try:
        user = await Users.get(username=username)
    except DoesNotExist:
        return json({'Error': 'Incorrect username'}, status=400)
    if bill_id and amount:
        account = await BankAccounts.get_or_create(user_id=user.id,
                                                   bill_id=bill_id)
        account = account[0]
        transaction = await Transactions.create(account_id_id=account.id,
                                                amount=amount)
        account.balance += amount
        await account.save()
        signature = await generate_signature(transaction_id=transaction.id,
                                             user_id=user.id,
                                             bill_id=bill_id,
                                             amount=amount)
        return json({'signature': signature,
                     'transaction_id': transaction.id,
                     'user_id': user.id,
                     'bill_id': bill_id,
                     'amount': amount}, status=201)
    return json({}, status=400)


@app.get('/balance')
@protected()
@inject_user()
async def show_balance(request, user):
    accounts = await BankAccounts.filter(user_id=user['id'])\
                                 .values('id', 'bill_id', 'balance')
    for account in accounts:
        account['bill_id'] = str(account['bill_id'])
    return json(accounts, status=200)


@app.get('/transactions')
@protected()
@inject_user()
async def show_transactions(request, user):
    user_id = user['id']
    transactions = await Transactions.raw(
        f"select * from transactions where account_id_id in (select id from bankaccounts where user_id={user_id});"
    )  # remove raw SQL
    queryset = []
    for transaction in transactions:
        item = {
                "transaction_id": transaction.id,
                "amount": transaction.amount
               }
        queryset.append(item)
    return json(queryset, status=200)

register_tortoise(
    app,
    db_url=app.config.DB_URL,
    modules={'models': ['models']},
    generate_schemas=True
)


if __name__ == "__main__":
    app.run(port=5000)
