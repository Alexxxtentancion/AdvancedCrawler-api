import json

from aioelasticsearch import Elasticsearch
from aiohttp import web

from asyncorm.main import CrawlerStats
from authorization.interface import AuthInterface
from crawlerMS.interface import CrawlerInterface

auth = AuthInterface()


async def registration(request):
    try:
        email = request.query['email']
        password = request.query['password']
        name = request.query['name']
        response_obj = {'email': email, 'password': password, 'name': name}
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


async def index(request):
    try:
        try:
            token = request.headers.get('Authorization').split(' ')[1]
            response_obj = {'token': token}
            print(response_obj)
            val = await auth.make_request("validate", data=response_obj)
            if val['status'] == 'success':
                domain = request.query['domain']
                response_obj = {'domain': domain, "user": val.get('data')}
                print(response_obj)
                r = await CrawlerInterface.make_nowait_request("index", data=response_obj)
                return web.Response(text=json.dumps(r), status=200)
            else:
                return web.Response(text=json.dumps(val), status=200)
        except:
            response_obj = {'status': 'forbidden', 'data': {}}
            return web.Response(text=json.dumps(response_obj), status=500)

    except Exception as e:
        response_obj = {'status': '<400>', 'data': {}}
        return web.Response(text=json.dumps(response_obj), status=500)


async def stat(request):
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        response_obj = {'token': token}
        print(response_obj)
        val = await auth.make_request("validate", data=response_obj)
        print(val)
        if val['status'] == 'success':
            print('lskcns')
            data = await CrawlerStats.objects.filter(author_id=val['data'].get('id'))
            response_data = [{"domain": data.domain, "pages_count": data.pages_count,
                              "avg_time_per_page": data.avg_time_per_page,
                              "max_time_per_page": data.max_time_per_page} for data in data]
            return web.Response(text=json.dumps({"status": "ok ", "data": response_data}), status=200)
        else:
            return web.Response(text=json.dumps(val), status=200)
    except Exception as e:
        response_obj = {'status': 'forbidden', 'data': {}, 'reason': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)


async def search(request):
    try:
        try:
            query = request.query['q']
            limit = request.query['limit']
            offset = request.query['offset']
            if int(limit) > 100:
                raise Exception
        except Exception as e:
            return web.Response(text=json.dumps({"status": "bad_request", "data": {},"reason":str(e)}), status=400)
        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        search_object = {'query': {'match': {'text': query}}, 'size': limit, 'from': offset}
        data = await CrawlerStats.objects.all()
        index_list = list(set([x.domain.translate({ord(i): None for i in """"[*\>:\<'"|/?]"""}) for x in data]))
        docs_list = []
        for index in index_list:
            res = await es.search(index=index, body=json.dumps(search_object))
            docs_list.append(res.get('hits').get('hits'))
        return web.Response(text=json.dumps({"status": "ok", "data": docs_list}), status=200)

    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)
