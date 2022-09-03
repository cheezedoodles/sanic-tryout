async def make_verification_link(id, username):
    link = str(id)+username
    return link

async def verify_link(link, id, username):
    if link == str(id)+username:
        return True
    return False