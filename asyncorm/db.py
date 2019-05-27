import aiomysql

from asyncorm.utils import connection_loop


# loop = asyncio.get_event_loop()


class Database():

    async def __init(self, name):
        self.conn = await aiomysql.connect(host='127.0.0.1',
                                           port=3306,
                                           user='root',
                                           password='12345',
                                           db=name,
                                           loop=connection_loop
                                           )
        self.cur = await self.conn.cursor()
        self.b = 3

    def __init__(self, name):
        connection_loop.run_until_complete(self.__init(name))
        # asyncio.run(self.__init())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

    @property
    async def connection(self):
        return await self.conn

    @property
    async def cursor(self):
        return await self.cur

    async def commit(self):
        await self.conn.commit()

    async def execute(self, sql, params=None):
        await self.cur.execute(sql, params or ())

    async def fetchall(self):
        return await self.cur.fetchall()

    def fetchone(self):
        return self.cur.fetchone()

    async def parse(self, sql, class_):
        await self.cur.execute(sql)
        res_tuple = await self.cur.fetchall()
        print(res_tuple)
        res_desc = [i[0] for i in self.cur.description]
        res_d = [class_(**dict(zip(res_desc, res_tuple[i]))) for i in range(len(res_tuple))]
        return res_d

    async def query_constructor(self, query, table, cond,fk, id=None):
        if query.startswith('SELECT'):
            params = ['{}="{}"'.format(x, y) for x, y in cond.items()]
            params = (" AND ".join(params))
            return query.format(table, params)

        elif query.startswith('INSERT'):
            keys_list = [x for x in cond.keys()]
            values_list = [y for y in cond.values()]
            columns = (",".join(keys_list))
            values = str(values_list)[1:-1]
            return query.format(table, columns, values)
        elif query.startswith('DELETE'):
            return await query.format(table, cond)
        elif query.startswith('UPDATE'):
            col_vals = ["{}='{}'".format(x, y) for x, y in cond.items()]
            col_vals = (",".join(col_vals))
            return query.format(table, col_vals, id)
        elif query.startswith('CREATE TABLE'):
            par_type_lst = ["{} {}".format(x, y) for x, y in cond.items()]
            par_type_lst = (",".join(par_type_lst))
            table_name = table.__name__
            sub_query = [',FOREIGN KEY ({}) REFERENCES {}(id)'.format(x, y) for x, y in fk.items()]
            sub_query = (",".join(sub_query))
            print(sub_query)
            return query.format(table_name, par_type_lst,sub_query)
