import os
from sanic import Sanic, text

from sanic_jwt import initialize, protected

from tortoise.contrib.sanic import register_tortoise

from auth import registration, authenticate


app = Sanic(__name__)
app.config.DB_URL = os.environ.get('DB_URL')
initialize(app, access_token_name='jwt', authenticate=authenticate)
app.blueprint(registration)


@app.get("/")
@protected()
async def hello_world(request):
    return text('welcome')


register_tortoise(
    app,
    db_url=app.config.DB_URL,
    modules={'models': ['models']},
    generate_schemas=True
)


if __name__ == "__main__":
    app.run(port=5000)
