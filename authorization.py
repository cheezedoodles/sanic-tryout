import jwt
from sanic import Blueprint, text
from tortoise.exceptions import DoesNotExist

from models import Users
from auth import make_verification_link, verify_link


registration = Blueprint('register', url_prefix='/register')


@registration.post('/')
async def register(request):
    username = request.json['username']
    password = request.json['password']
    try:
        await Users.get(username=username)
    except DoesNotExist:
        user = await Users.create(username=username, password=password)
        link = await make_verification_link(user.id, user.username)
        url = request.headers.get("host") + '/register' + f'/{user.username}' + f'/{link}'
        return text(url)
    return text('This username is already taken')

@registration.get('/<username:str>/<usertoken:str>')
async def activate_user(request, username, usertoken):
    user = await Users.get(username=username)
    id = user.id
    if verify_link(usertoken, id, username):
        user.is_active = 1
        await user.save()
        return text('Verified successfully')
    return text('Invalid link')
