#!
#   -*- coding: utf-8 -*-

# rewrite db.api for new hummingbird. 2019/04/19

import sys, time, multiprocessing, traceback, os, threading
import array

#from . import cfg

# 在多进程环境中，会在每个进程都导入一次？
print('I am @', os.getpid(), __name__)

class MyRecord(object):
    """A class to access the record of MyTable's table"""

    def __init__(self, data, columns):
        data = [(type(i)==array.array and [i.tostring()] or [i])[0] for i in data]
        [x for x in map(self.__setattr__, columns, data)]

class MyTable(object):
    """A class to access cirrodata
    表都通过db.table的形式调用，在db中定义，而不是直接调用模块中的定义"""
    _primary_key = 'id'

    def __init__(self, _id=None, _table="", _select_columns='*', _values_1=True, rows=10, page=1, *k, **kw):
        if _id is not None:
            kw[self._primary_key] = _id
        self.rows, self.page = int(rows), int(page)-1
        self._values_1 = _values_1
        self.__dict__['_table'] = _table or self.__class__.__name__
        self._select_columns = _select_columns
        #self._select_columns = _select_columns.split(',') if _select_columns else self.__class__._columns[:]   # self.__class__.columns 必须在类定义时获取表的全量字段
        #self._columns = [i.strip() for i in self._select_columns]
        self.__dict__['_debug'] = kw.pop('_debug', 0)
        self._select(*k, **kw)

    def _select(self, *k, **kw):
        """select函数，一般用于初始化本类的取数，对应select语句，条件可以没有主键（默认为id）"""

        sql = "select %s from %s " % (self._select_columns, self._table)
        #sql = "select %s from %s " % (','.join(self._select_columns), self._table)
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
        self.__dict__['_columns'] = result['columns']

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
            #print ('self.__class__._columns', self.__class__._columns)
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
        # CirroData con_str: db host port user passwd
        self._k, self._kw = k, kw
        self.Table = type('Table', (MyTable, ), {})
        self.Table._db = self
        print('db init @', db_type, os.getpid())

    def __del__(self):
        """测试中止或重启时,会否激活本方法,以便作一些清场处理"""

        print('db del', self, os.getpid())

    def __getattr__(self, table):
        tables = self.Table(_select_columns="table_name, owner, table_type, schema_name, database_name, type_name", table_name=table.upper(), _table="V$USER_TABLES", _debug=1, rows=-1)
        if not len(tables):
            raise AttributeError("'db' object has no arribute '%s'" % table)
        # 需要改进以便访问bonc_user模式里的表（默认是XC33000）
        table_cls = type(table, (self.Table, ), {})
        # 实测行云从2.6.1开始，其python api接口返回在的cur.description能够正确访问和包含字段类型等信息，所以不用再提前获取字段了
        #cols = self.Table(_table="v$user_tab_columns", table_name=table.upper(), schema_name=tables[0].schema_name, _select_columns="table_name,data_type,data_size,schema_name,database_name,column_type,column_name", rows=-1)
        #table_cls._desc = [[i.column_name.lower(), i.data_type, i.data_size] for i in cols]
        #table_cls._columns = [i.column_name.lower() for i in cols]
        self.__dict__[table] = table_cls
        return self.__dict__[table]

    #@classmethod
    #@cfg.rpc
    def _execute(self, sql="", values=[]):
        """调用外部定义的数据库独立的execute函数，返回结果是一个字典，形如{"success":True, 'data':cursor.fetchall()}
        根据数据类型，可以决定是在进程中执行，还是线程池中执行，或是就在当前执行，以及通过returned_manager类进行执行。
        """

        if '__mp_main__' in sys.modules:
            # 如果是在多进程环境中，则将语句转到进程池中执行
            if hasattr(sys.modules['__mp_main__'], 'pools'):
                pools = sys.modules['__mp_main__'].pools
                return pools.apply(execute,(self._db_type, self._connect_str, sql,values))
        return execute(self._db_type, self._connect_str, sql, values)

def execute(db_type='CirroData', connect_str="", sql="", values=[]):
    """数据库执行SQL语句的接口，有可能调用其他线程的函数来取得结果，结果为列表类型"""

    from jpype import startJVM, java, shutdownJVM, isJVMStarted
    import jaydebeapi
    jvm_path="F:\\disk2\\xingyun\\jre\\lib\\server\\jvm.dll"
    jar_path="F:\\disk2\\xingyun\\PYTHON_API"
    jar_path="F:\\disk2\\xingyun\\PYTHON_api_sp"    # 2.6.1 新接口，主要改进有：cur.description 可以返回字段了。据说可能执行存储过程，但没有找到调用方法
    # 如下这种用法，都只是在当前进程执行。如果要将本方法改为多进程，可能需要较大的改动。行云必须改动，因为行云的cur是不支持多线程的，执行SQL语句会挂处整个进程。
    if isJVMStarted()==0:
        startJVM(jvm_path, "-ea", "-Djava.ext.dirs=%s" % jar_path)
    connect_str = connect_str.split()
    conn = jaydebeapi.connect('com.bonc.xcloud.jdbc.XCloudDriver','jdbc:xcloud:@%s' %connect_str[0],connect_str[1:3], 'd:\\disk2\\xingyun\\pYTHON_API_sp\\XCloundJDBC.jar')
    cur = conn.cursor()
    result = {'process':multiprocessing.current_process().name,'thread':threading.currentThread().name}
    result['sql'], result['values'] = sql, values
    try:
        #sql = sql.replace('%s','?')
        cur.execute(sql, values)
        print('sql, values', sql, values)
        print('columns', cur.description)
        try:
            data = cur.fetchall()
        except jaydebeapi.Error:    # 无记录的情况下
                data = [[0]]
        result['success'] = True
        result['data'] = data
        result['columns'] = [i[0].lower() for i in cur.description]
    except:
        result['success'] = False
        result['error'] = traceback.format_exc()
        #result['data'] = [[0]]
    #cur.close()
    #conn.close()
    return result

if __name__ == '__main__':
    # 行云数据库测试，配置参数从db_xy.py中导入。该不文件不加入上传git清单
    import db_xy
    db = db('CirroData',db_xy.con_str)
    stime=  time.time()
    print(db._execute('select * from dual'))
    print('Time spend: ', time.time()-stime)
    stime=  time.time()
    print(db._execute('select  acc_nbr, user_name from latn_33_serv_offer where main>? limit(0,?)', (10,5)))
    print('Time spend: ', time.time()-stime)
    stime=  time.time()
    print(db._execute('select  acc_nbr, user_name from latn_33_serv_offer where main>? order by ? limit(0,?)', (10, 'acc_nbr',5)))
    print('Time spend: ', time.time()-stime)
    stime=  time.time()
    print(db._execute('select * from dual'))
    print('Time spend: ', time.time()-stime)
    stime=  time.time()
    t = db.latn_33_serv
    t._primary_key = 'acc_nbr'
    res = t('18983306330', _select_columns='acc_nbr, user_name, obd_no')
    print(len(res))
    print(res.acc_nbr, res.user_name)
    res = db._execute("""drop_if_exists (?)""",('latn_33_serv',))
    print('tgm_serv: ', res)
    sys.exit()

