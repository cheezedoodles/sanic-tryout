import os

from Crypto.Hash import SHA1

ROWS_PER_PAGE = 5
PRIVATE_KEY = os.environ.get('PRIVATE_KEY')


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


async def generate_signature(transaction_id, user_id, bill_id, amount):
    """
    generates a signature when replenishing balance
    """
    signature = SHA1.new()
    byte_string = f'{PRIVATE_KEY}:\
                    {transaction_id}:\
                    {user_id}:\
                    {bill_id}:\
                    {amount}'\
                    .encode()
    signature.update(byte_string)
    return signature.hexdigest()
