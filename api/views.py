from aiohttp import web
import json
import jwt
sharable_secret = 'secret'
async def registration(request):
    try:
        email = request.query['email']
        password = request.query['password']
        name = request.query['name']
        response_obj = {'status':'ok','data':{'email':email,'password':password,'name':name}}
        return web.Response(text=json.dumps(response_obj),status=200)
    except Exception as e:
        response_obj = {'status': '<400>', 'reason':e}
        return web.Response(text=json.dumps(response_obj), status=500)

async def login(request):
    try:
        email = request.query['email']
        password = request.query['password']
        token = jwt.encode({
        'username': email,
    }, sharable_secret)
        print(token.decode('ascii'))
        response_obj = {'status': 'ok', 'data': {'token':token.decode('ascii'),'expire':'<timestamp>'}}
        return web.Response(text = json.dumps(response_obj),status=200)
    except Exception as e:
        response_obj = {'status': '<400>', 'data': e}
        return web.Response(text=json.dumps(response_obj), status=500)

async def search(request,app):
    try:
        query = request.query['q']
        limit = request.query['limit']
        offset = request.query['offset']
        search_object = {'query': {'match': {'text': query}}, 'size': limit, 'from': offset}
        res = await app['es'].search(index='index_url', body=json.dumps(search_object))
        return web.Response(text=json.dumps(res.get('hits').get('hits')), status=200)

    except Exception as e:
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=500)


