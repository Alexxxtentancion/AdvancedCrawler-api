from aiohttp import web
from aioelasticsearch import Elasticsearch
from api.views import registration, login, current, index,stat,search

async def connect_elasticsearch(app):
    app['es'] = Elasticsearch([{'host': 'localhost', 'port': 9200}])


if __name__ == '__main__':
    app = web.Application()
    app.on_startup.append(connect_elasticsearch)
    app.router.add_post('/api/signup', registration)
    app.router.add_post('/api/login', login)
    app.router.add_get('/api/current', current)
    app.router.add_post('/api/index', index)
    app.router.add_get('/api/stat',stat)
    app.router.add_get('/api/search', search)
    web.run_app(app)
