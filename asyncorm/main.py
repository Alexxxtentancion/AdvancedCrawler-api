from asyncorm.orm import *
from time import time
import asyncio
from asyncorm.utils import connection_loop
class Author(Model):
    # id = IntField()
    first_name = StringField(blank=True)
    patronymic = StringField(blank=True)
    last_name = StringField(blank=True)
    country = StringField(blank=True)
    _float = FloatField(blank=True)
    date_of_birth = DateField(blank=True)



async def run():
    # await Author.create_table()
    # a = Author(first_name="Паша", last_name="Петров", _float=3.0, date_of_birth="2000-03-13")
    # await a.save()

    await Author.objects.create(first_name="Паша", last_name="Петров", _float=3.0, date_of_birth="2000-03-13")
    await Author.objects.all()


if __name__ == '__main__':
    begin = time()
    connection_loop.run_until_complete(run())
    print(time()-begin)