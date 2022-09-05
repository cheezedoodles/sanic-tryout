from sanic import Blueprint
from sanic.response import json
from sanic_jwt import protected, inject_user

from tortoise import connections
from tortoise.query_utils import Prefetch
from tortoise.exceptions import DoesNotExist

from models import Products, BankAccounts, Transactions, Users
from utils import admin_only

admin = Blueprint('admin', url_prefix='/admin')


@admin.get('/products')
@protected()
@inject_user()
@admin_only()
async def get_products(request, user):
    """
    endpoint for listing all the products
    """
    products = await Products.all().values()
    return json(products, status=200)


@admin.get('/userinfo')
@protected()
@inject_user()
@admin_only()
async def get_user_info(request, user):
    """
    endpoint used for retrieving user info and their accounts
    """
    conn = connections.get("default")
    users = await conn.execute_query_dict(
        'SELECT users.id, username, is_superuser, is_active, bill_id, balance FROM users JOIN bankaccounts on user_id=user_id;'
    )  # remove raw sql
    for user in users:
        user['bill_id'] = str(user['bill_id'])
    return json(users, status=200)


@admin.post('/userstate')
@protected()
@inject_user()
@admin_only()
async def change_user_state(request, user):
    """
    endpoint used for changing is_active model attribute
    """
    username = request.json.get('username', None)
    state = request.json.get('state', None)
    try:
        user = await Users.get(username=username)
    except DoesNotExist:
        return json({'status': 'incorrect username'}, status=400)
    if state in (0, 1):
        user.is_active = state
        await user.save()
        return json({'status': 'changed successfully'}, status=200)
    return json({'status': 'invalid state value'}, status=400)


@admin.route('/modify/<product_id:int>', methods=["POST", "PATCH", "DELETE"])
@protected()
@inject_user()
@admin_only()
async def modify_product(request, user, product_id):
    """
    endpoint that allows you to modify products:
    POST: {all(name, description, price)}
    PATCH: {any(name, description, price)}
    DELETE: {}
    """
    name = request.json.get('name', None)
    description = request.json.get('description', None)
    price = request.json.get('price', None)
    if request.method == "POST":
        if all((name, description, price)):
            await Products.create(name=name, description=description, price=price)
            return json({'status': 'product saved'}, status=201)
        return json({'status': 'required values are not present'}, status=400)
    elif request.method == "PATCH":
        product = await Products.get(id=product_id)
        if name:
            product.name = name
        if description:
            product.description = description
        if price:
            product.price = price
        await product.save()
        return json({}, status=200)
    elif request.method == "DELETE":
        product = await Products.get(id=product_id)
        await product.delete()
        return json({}, status=200)
    return json({'status': 'error'}, status=400)
