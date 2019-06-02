from time import time
import asyncio
from asyncorm.orm import *
from asyncorm.utils import connection_loop
import datetime

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
    https = BooleanField(blank=False)
    time = DateField(blank=False)
    pages_count = IntField(blank=False)
    avg_time_per_page = FloatField(blank=False)
    max_time_per_page = FloatField(blank=False)
    min_time_per_page = FloatField(blank=False)
import datetime
async def run():
 pass


if __name__ == '__main__':
    begin = time()
    connection_loop.run_until_complete(run())
    print(time() - begin)
