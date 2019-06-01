import json

from aiohttp import web

from authorization.auth import AuthMs

auth = AuthMs()


async def registration(request):
    try:
        email = request.query['email']
        password = request.query['password']
        name = request.query['name']
        response_obj = {'status': 'ok', 'data': {'email': email, 'password': password, 'name': name}}
        r = await auth.make_request("signup", data=response_obj)
        return web.Response(text=json.dumps(r), status=200)
    except Exception as e:
        response_obj = {'status': '<400>', 'reason': e}
        return web.Response(text=json.dumps(response_obj), status=500)


async def login(request):
    try:
        email = request.query['email']
        password = request.query['password']
        response_obj = {'email': email, 'password': password}
        r = await auth.make_request("login", data=response_obj)
        return web.Response(text=json.dumps(r), status=200)
    except Exception as e:
        response_obj = {'status': '<400>', 'data': e}
        return web.Response(text=json.dumps(response_obj), status=500)


async def current(request):
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        response_obj = {'token': token}
        # print(token.split(' ')[1])
        r = await auth.make_request("validate", data=response_obj)
        return web.Response(text=json.dumps(r), status=200)
    except Exception as e:
        response_obj = {'status': '<400>', 'data': e}
        return web.Response(text=json.dumps(response_obj), status=500)


async def search(request, app):
    try:
        query = request.query['q']
        limit = request.query['limit']
        offset = request.query['offset']
        search_object = {'query': {'match': {'text': query}}, 'size': limit, 'from': offset}
        res = await app['es'].search(index='index_url', body=json.dumps(search_object))
        return web.Response(text=json.dumps(res.get('hits').get('hits')), status=200)

    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)
