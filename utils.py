ROWS_PER_PAGE = 5


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
