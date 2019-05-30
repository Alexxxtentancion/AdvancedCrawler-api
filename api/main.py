from aiohttp import web
from aioelasticsearch import Elasticsearch
from api.views import registration,login


if __name__ == '__main__':
    app = web.Application()
    app.router.add_post('/api/registration', registration)
    app.router.add_post('/api/login',login)
    web.run_app(app)