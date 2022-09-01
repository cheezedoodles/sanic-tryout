from sanic import Sanic, response

from tortoise.contrib.sanic import register_tortoise

from models import User

app = Sanic(__name__)


@app.get("/")
async def hello_world(request):
    users = await User.all()
    return response.json({'users': [str(user) for user in users]})


register_tortoise(
    app, 
    db_url='postgres://postgres:postgrespw@localhost:49153', 
    modules={'models': ['models']}, 
    generate_schemas=True
)


if __name__ == "__main__":
    app.run(port=5000)