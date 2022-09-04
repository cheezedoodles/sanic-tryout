from sanic import Blueprint, text

from tortoise.exceptions import DoesNotExist
from sanic_jwt.exceptions import AuthenticationFailed

from models import Users
from utils import make_verification_link, verify_link

registration = Blueprint('register', url_prefix='/register')


@registration.post('/')
async def register(request):
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        raise AuthenticationFailed('Missing username and/or password.')

    try:
        await Users.get(username=username)
    except DoesNotExist:
        user = await Users.create(username=username, password=password)
        link = await make_verification_link(user.id, user.username)
        # remove hardcoded url
        url = request.headers.get("host") \
            + '/register' + f'/{user.username}' \
            + f'/{link}'
        return text(url)

    return text('This username is already taken')


@registration.get('/<username:str>/<usertoken:str>')
async def activate_user(request, username, usertoken):
    user = await Users.get(username=username)
    id = user.id

    verified = await verify_link(usertoken, id, username)
    if verified:
        user.is_active = 1
        await user.save()
        return text('Verified successfully')

    return text('Invalid link')


async def authenticate(request, *args, **kwargs):
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        raise AuthenticationFailed('Missing username and/or password.')

    try:
        user = await Users.get(username=username).values()
    except DoesNotExist:
        raise AuthenticationFailed('User not found')

    if password != user['password']:
        raise AuthenticationFailed('Incorrect password')
    return user
