from sanic import Sanic, response

from tortoise.contrib.sanic import register_tortoise

from models import Users
from authorization import registration

app = Sanic(__name__)

app.blueprint(registration)


@app.get("/")
async def hello_world(request):
    users = await Users.all()
    return response.json({'users': [str(user) for user in users]})


register_tortoise(
    app, 
    db_url='postgres://postgres:postgrespw@localhost:49157/shop_app', 
    modules={'models': ['models']}, 
    generate_schemas=True
)


if __name__ == "__main__":
    app.run(port=5000)