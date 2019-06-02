from aiohttp import web
from aioelasticsearch import Elasticsearch
from api.views import registration, login, current, index,stat,search




if __name__ == '__main__':
    app = web.Application()
    app.router.add_post('/api/signup', registration)
    app.router.add_post('/api/login', login)
    app.router.add_get('/api/current', current)
    app.router.add_post('/api/index', index)
    app.router.add_get('/api/stat',stat)
    app.router.add_get('/api/search', search)
    web.run_app(app)
