# -*- coding: utf-8 -*-

# rewrite db.api for new hummingbird. 2019/04/19

import sys, time, multiprocessing, traceback
import array

class MyRecord(object):
    """A class to access the record of MyTable's table"""

    def __init__(self, data, columns):
        data = [(type(i)==array.array and [i.tostring()] or [i])[0] for i in data]
        [x for x in map(self.__setattr__, columns, data)]

class MyTable(object):
    """A class to access cirrodata
    表都通过db.table的形式调用，在db中定义，而不是直接调用模块中的定义"""
    _primary_key = 'id'

    def __init__(self, _id=None, _table="", _select_columns='', _values_1=True, rows=10, page=1, *k, **kw):
        if _id is not None:
            kw[self._primary_key] = _id
        self.rows, self.page = rows, page-1
        self._values_1 = _values_1
        self.__dict__['_table'] = _table or self.__class__.__name__
        self._select_columns = _select_columns.split(',') if _select_columns else self.__class__._columns[:]   # self.__class__.columns 必须在类定义时获取表的全量字段
        self._columns = [i.strip() for i in self._select_columns]
        self.__dict__['_debug'] = kw.pop('_debug', 0)
        self._select(*k, **kw)

    def _select(self, *k, **kw):
        sql = "select %s from %s " % (','.join(self._select_columns), self._table)
        self._values = []
        if len(kw):
            sql += " where "
            self._where_list, self._values = self._where_process(**kw)
            sql += " and ".join(self._where_list)
        if self.rows > 0:
            sql += " limit(%s,%s) " % (self.page*self.rows, self.rows)
        sql = sql.replace('%s','?') # 行云的占位符是 ?
        result = self._db._execute(sql, self._values)
        self.__dict__['_data'] = result['data']

    def _where_process(self, *k, **kw):
        """将关键字参数处理成为条件对，以便扩展到SQL语句中去"""

        #aa = kw.pop('table_of','a.')    # 表的昵称可能要统一由调用时指定，不能在后台增加
        where = []
        values = []
        for column,value in kw.items():
            if type(value) in (type(()),type([])):
                """if value is a list or a tuple, replace the '=' with 'in'. if the length is 1, then use '=' still."""
                # 20150703: add by tgm ,  支撑pgsql的大小写模糊查询
                if len(value) == 2 and value[0] in ( '>','<','>=','<=','!=','like','not like', '~*' ,'ilike' ):

                    where.append( "%s %s %s " % (column,value[0],'%s') )
                    values.append( value[1] )
                # 增加sqlite3的全文索引
                elif len(value)==2 and value[0]=='match' and self._db_type=='sqlite':
                    where.append("%s %s '%s' " % (column, value[0], ' '.join('%s' % i for i in value[1].split(' '))))
                elif len(value)==2 and value[0]=='is':  # is noll, is not null
                    where.append(" %s is %s " % (column, value[1]))
                elif len(value)==2 and value[0] == 'not in':
                    where.append("%s not in (%s) " % (column, ','.join(['%s']*len(value[1]))))
                    values += value[1]
                elif len(value)==2 and value[0] == 'full join !=':
                    where.append("a.%s != b.%s" % (column, value[1]))
                elif len(value)==2 and value[0] == 'full join =':
                    where.append("a.%s = b.%s " % (column, value[1]))
                # left join 有两种主要使用情况：
                # 1、两表结构相同或相近，为了比较同一条件下的结果集的异同，比如月表用户清单环比以得到增加和流失清单
                # 2、B表是A表某字段的扩展解释，比如组织性表，服务提供配置表等
                # 对于2，需要提供关联关键字段，并且要注意_select_columns中增加表别名作为前缀。对于1，则除了提供关联字段以外，还要指定B表的具体条件。
                #elif len(value==2 and value[0] == 'left join'
                elif len(value) == 3 and value[0]=='between':
                    where.append( "%s between %s and %s " % ( column,'%s','%s' ) )
                    values += value[1:3]
                elif len(value) > 0:
                    where.append( "%s in (%s) " % (column,','.join( ['%s']*len(value) ) ) )
                    values += value
                else:
                    where.append( "1!=1 " )
            elif type(value) in ( type(1),type(1.0),type(2**32) ):
                """if value type is int,decimal, or long, use '=' as the oprator."""
                where.append( "%s = %s " % (column,'%s') )
                values.append( value )
            elif type(value) in ( type(''), ):
                """if value type is string as endswith '%', then use 'like' as the oprator."""
                if value.endswith('%') or value.startswith('%'):
                    where.append( "%s like %s " % (column, '%s') )
                    values.append( value )
                else:
                    where.append( "%s=%s " % (column,'%s') )
                    values.append( value )
            elif type(value) in ( type(None), ):
                """if value is None, then use the 'is null or ='' '."""
                #where.append( " %s is null " % column )
                where.append( " (%s is null or %s='' or %s='None') " % (column,column,column) )
            else:
                """else use '='"""
                where.append( "%s = %s " % (column,'%s') )
                values.append( value )
        return where,values

    def __getattr__( self, name ):
        """return the value of the column in table, of course, name is not a proprity of the class, but is one of the table columns."""

        if name in self.__dict__:
            return self.__dict__[name]
        try:
            index = self.__dict__['_columns'].index( name.lower() )
        except:
            print ('name: 数据库可能无此字段', name, self.__dict__['_columns'])
            print ('self.__class__._columns', self.__class__._columns)
            raise
        s = [ i[index] for i in self._data ]
        s = [ (type(i)==array.array and [i.tostring()] or [i])[0] for i in s ]
        if self._values_1 and len(s) == 1:
            return s[0]
        elif len(s) == 0 and self._values_1:
            return ''
        else:
            return s

    def __getitem__(self, start):
        """rwrite for self[i] used. returned a MyRecord class, defined top of the file"""

        if isinstance(start, slice):
            return [MyRecord(self._data[i], self._columns) for i in range(self.__len__())[start]]
        else:
            return MyRecord(self._data[start], self._columns)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self

    def __next__(self):
        self.__dict__.setdefault('_nextValue', 0)
        try:
            value = self.__getitem__(self._nextValue)
        except IndexError:
            self._nextValue = 0
            raise StopIteration
        else:
            self._nextValue += 1
            return value
    next = __next__

class db(object):
    """数据库的接口类，表将会作为库的属性"""

    def __init__(self, db_type="CirroData", connect_str="", *k, **kw): 
        self._db_type = db_type
        self._connect_str = connect_str
        self._k, self._kw = k, kw
        self.Table = type('Table', (MyTable, ), {})
        self.Table._db = self
    
    def __getattr__(self, table):
        tables = self.Table(_select_columns="table_name, owner, table_type, schema_name, database_name, type_name", table_name=table.upper(), _table="V$USER_TABLES", _debug=1, rows=-1)
        if not len(tables):
            raise AttributeError("'db' object has no arribute '%s'" % table)
        table_cls = type(table, (self.Table, ), {})
        cols = self.Table(_table="v$user_tab_columns", table_name=table.upper(), schema_name=tables[0].schema_name, _select_columns="table_name,data_type,data_size,schema_name,database_name,column_type,column_name", rows=-1)
        table_cls._desc = [[i.column_name.lower(), i.data_type, i.data_size] for i in cols]
        table_cls._columns = [i.column_name.lower() for i in cols]
        self.__dict__[table] = table_cls
        return self.__dict__[table]

    def _execute(self, sql="", values=[]):
        """数据库执行SQL语句的接口，有可能调用其他线程的函数来取得结果，结果为列表类型"""
    
        from jpype import startJVM, java, shutdownJVM, isJVMStarted
        import jaydebeapi
        jvm_path="F:\\disk2\\xingyun\\jre\\lib\\server\\jvm.dll"
        jar_path="F:\\disk2\\xingyun\\PYTHON_API"
        # 如下这种用法，都只是在当前进程执行。如果要将本方法改为多进程，可能需要较大的改动。行云必须改动，因为行云的cur是不支持多线程的，执行SQL语句会挂处整个进程。
        if isJVMStarted()==0:
            startJVM(jvm_path, "-ea", "-Djava.ext.dirs=%s" % jar_path)
        if '_conn' not in self.__dict__:    # 这里不能用setdefault，因为总会执行后面的表达式
            print('init for conn')
            self.__dict__['_conn'] = jaydebeapi.connect('com.bonc.xcloud.jdbc.XCloudDriver','jdbc:xcloud:@136.6.206.33:1803/BONC',['XC330001','sjjs123456'])
        if '_cur' not in self.__dict__:
            print('init for cur:')
            self.__dict__['_cur'] = self._conn.cursor()
        #cur = conn.cursor()
        result = {'process':multiprocessing.current_process().name}
        result['sql'], result['values'] = sql, values
        try:
            #sql = sql.replace('%s','?')
            self._cur.execute(sql, values)
            print('sql, values', sql, values)
            try:
                data = self._cur.fetchall()
            except jaydebeapi.Error:    # 无记录的情况下
                    data = [[0]]
            result['success'] = True
            result['data'] = data
        except:
            result['success'] = False
            result['error'] = traceback.format_exc()
            #result['data'] = [[0]]
        return result

if __name__ == '__main__':
    db = db()
    stime=  time.time()
    print(db._execute('select * from dual'))
    print(time.time()-stime)
    stime=  time.time()
    print(db._execute('select  acc_nbr, user_name from latn_33_serv_offer where main>? limit(0,?)', (10,5)))
    print(time.time()-stime)
    stime=  time.time()
    print(db._execute('select  acc_nbr, user_name from latn_33_serv_offer where main>? order by ? limit(0,?)', (10, 'acc_nbr',5)))
    print(time.time()-stime)
    stime=  time.time()
    print(db._execute('select * from dual'))
    print(time.time()-stime)
    stime=  time.time()
    t = db.latn_33_serv
    t._primary_key = 'acc_nbr'
    res = t('18983306330')
    print(len(res))
    print(res.acc_nbr, res.user_name)
    sys.exit()

