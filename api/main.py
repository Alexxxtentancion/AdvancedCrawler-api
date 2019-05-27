from aiohttp import web
from aioelasticsearch import Elasticsearch
from api.views import registration,login


async def connect_elasticsearch(app):
    app['es'] = Elasticsearch([{'host': 'localhost', 'port': 9200}])

if __name__ == '__main__':
    app = web.Application()
    app.on_startup.append(connect_elasticsearch)
    app.router.add_post('/api/registration', registration)
    app.router.add_post('/api/login',login)
    web.run_app(app)