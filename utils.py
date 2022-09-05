from Crypto.Hash import SHA1
from sanic import Sanic

ROWS_PER_PAGE = 5
# app = Sanic.get_app('main')


async def make_verification_link(id, username):
    """
    creates a link for account activation
    """
    link = str(id)+username
    return link


async def verify_link(link, id, username):
    """
    verifies that the link is valid
    """
    if link == str(id)+username:
        return True
    return False


# async def generate_signature(transaction_id, user_id, bill_id, amount):
#     signature = SHA1.new()\
#                     .update(f'{app.config.PRIVATE_KEY}:{transaction_id}:{user_id}:{bill_id}:{amount}'.encode())\
#                     .hexdigest()
#     return signature
