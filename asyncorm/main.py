from time import time

from asyncorm.orm import *
from asyncorm.utils import connection_loop


class User(Model):
    # id = IntField()
    email = StringField(blank=False)
    password = StringField(blank=False)
    name = StringField(blank=False)
    created_date = DateField(blank=False)
    last_login_date = DateField(blank=False)


class Token(Model):
    token = StringField(blank=False)
    user_id = ForeignKey(references=User)
    expire_date = DateField(blank=False)

class CrawlerStats(Model):
    domain = StringField(blank=False)
    author_id = ForeignKey(references=User)
    https = IntField(blank=False)
    time = DateField(blank=False)
    pages_count = IntField(blank=False)
    avg_time_per_page = FloatField(blank=False)
    max_time_per_page = FloatField(blank=False)
    min_time_per_page = FloatField(blank=False)
import datetime
async def run():
    await User.create_table()
    # a.save()
    # await User.objects.create(email='email@email.ru',password='12345',name='Artem'
    #                           ,created_date=datetime.datetime.now(),last_login_date='2018-09-09')
    await Token.create_table()
    await CrawlerStats.create_table()
    # a = await User.objects.all()
    # print(a)

if __name__ == '__main__':
    begin = time()
    connection_loop.run_until_complete(run())
    print(time() - begin)
