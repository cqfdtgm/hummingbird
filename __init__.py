#   -*- coding: utf-8 -*-
#   $Header$

import sys, os, os, cherrypy, cgi, time, json, psycopg2, chardet, traceback
import re, imp, random, queue, datetime, xlwt, xlrd, hashlib, pickle
import urllib, decimal, string, threading, multiprocessing
from mako.template import Template
from mako.lookup import TemplateLookup
# 将所有需要导入的模块一次性导入，并加入内置命名空间，可以作为全局变量使用
import mako.runtime
mako.runtime.UNDEFINED = 'UNDEFINED'

import tools, cfg

if __name__ == '__main__':
    pools = multiprocessing.Pool(4)     # 只能在__main__中开进程池，但如何让模块中的函数使用此进程池呢？
    conf = os.path.abspath(__file__)[:-2] + 'conf'
    fp = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(fp))
    os.chdir(os.path.dirname(fp))
    Root = __import__(os.path.basename(fp))
    cherrypy.quickstart(Root,config=conf)
    sys.exit()  #   这一句增加以后， 不会再执行后面的，从而避免了重复导入


class default(object):
    exposed = True
    _cls_cnt = 0    # 类总计数
    _dirs = [os.path.dirname(__file__)] # 模板搜索路径，不一定是文件夹路径，而是根据类继承的顺序，后续子模块以此为第一个元素，往后追加其文件夹。
    _dic = {'charset':'utf8', 'title':'蜂鸟企业信息管理系统'}   # 公共的字典，会被用作模板文件的命名空间
    _dic['easyui'] = '/js/9_easyui'
    _dic['cherrypy'] = cherrypy
    _dic['os'] = os
    _dic['threading'] = threading
    _dic['col'] = 'abc'
    _onlines = {}   # 在线人员列表
    _dic['_onlines'] = _onlines

    def __init__(self, *k, **kw):
        self.__class__._cls_cnt += 1
        self._k, self._kw = k, kw
        #print('self._k kw', self._k, self._kw, k, kw)
        #self._dic = {}
        self._dic['_sess'] = {}
        print('cookie: ', cherrypy.request.cookie)
        # 删除cookie的方法： 在响应头中将超时设为0
        self._dic['_table'] = 'test2'
        self._dic['_col'] ='col'
        self._dic['_db'] = 'db'
        self._dic['_real_table'] = 'real_table'
        #cherrypy.response.cookie['session_id']['expires'] = 0

    def index(self, *k, **kw):
        pass
        #return 'index'

    def login(self, *k, **kw):
        pass

    def log(self, *k, **kw):
        pass

    def sleep(self, *k, **kw):
        time.sleep(2)
        #return 'sleep'
        pass

    def users(self, *k, **kw):
        pass

    #@tools.rpc     -- 对类的方法不能使用这种包装方式，只能显式包装外部函数
    def debug(self, *k, **kw):
        #time.sleep(5)   #   在本线程中sleep，CP的其他线程仍然能够正常响应。
        cfg.rpc(cfg.f)(2)   # 要测试一下在线程池中执行行云SQL，会否阻断整个服务器, 以及，发往线程池的函数出错的话，进程池会否崩溃
        pass

    def _access(self):
        """权限访问检测方法.
        当登录时， 会根据用户名与角色表， 将该用户的角色，权限读取到session中。"""

        # 未登录用户只有登录处的Save和Update权限（注册和登录），其余地方只读。
        # 匿名用户有login处的Save（退出登录）权限，留言本的Save，其余只读。
        # 注册用户根据角色和权限关联取得。

        # 如果IP不在列表以内，直接出错，看客户端是否会失去响应。
        path = cherrypy.request.wsgi_environ['PATH_INFO']
        if 0:   #path.endswith('/'):
            raise   # 直接出错，能否达到象本端口没有开放一样的效果？
            # 不能，cherrypy 系统将错误返回到了客户端
        return True # 暂时关闭权限验证
        if path[-1]=='/' and len(path)>1:
            cherrypy.request.wsgi_environ['PATH_INFO'] = path.rstrip('/')
        if re.match('|'.join(cfg.guest_url), cherrypy.request.wsgi_environ['PATH_INFO']):  # 在访客可访问列表里
            return True
        if not self._sess.get('user','访客_').startswith('访客_') and re.match('|'.join(self._sess.get('urls',['$'])), cherrypy.request.wsgi_environ['PATH_INFO']):
            return True
        print('无权访问', cherrypy.request.wsgi_environ['PATH_INFO'], self._sess.get('url',['/$']), cfg.guest_url)
        return False

    def __iter__(self, modu=None):
        '''main func to make self as a iter,
        将后续URL映射到类的方法上去'''


        path = cherrypy.request.wsgi_environ['PATH_INFO']
        if 0:   #path.endswith('/'):
            time.sleep(0)
            return
            raise asdf
            raise cherrypy.HTTPError()
            return
            raise   # 直接出错，能否达到象本端口没有开放一样的效果？
            # 不能，cherrypy 系统将错误返回到了客户端
        if not self._access():
            raise cherrypy.HTTPError(403,'Forbidden')
            return
        # 在这儿做所有初始化完成，而业务方法还没有运行的一些批量设定
        if '_db' in self._kw:
            self._dic['_db'] = getattr(cfg, self._kw.pop('_db'))
        """ # 设计目的: 每个应用尽量不重写__iter__方法, 而是通过修改模板文件和self._dic内容来输出HTML.
        # 输出json内容的, 重写Json方法即可， 或前置部分处理 ， 或完全替代.
        # 表现和逻辑分开, 尽量不在.py文件中输出HTML代码.
        # 方法命名约定: 
        #  大写:数据库后台操作url, 返回json；
        #  小写:运行相关方法, 
        #    返回本方法同名的模板.
        #  无方法运行index方法，返回index.html模板.
        """
        
        #print('K KW @ last: ', self._k, self._kw)
        if not len(self._k):
            self._k = ('index',)
        method1 = self._k[0]
        print('mehod1', method1)
        print('_k, _kw', self._k, self._kw)
        try:
            result = getattr(self, method1)(*self._k[1:], **self._kw)
        except:
            yield 'Error @ __iter__ %s, %s / %s %s ' % (cgi.escape(str(self)), method1, self._k, self._kw)
            traceback.print_exc()
            yield traceback.format_exc().replace('\n', '<br>')
            return
        if method1[0].isupper(): # 是大写，返回json
            cherrypy.response.headers['Content-Type'] = 'text/plain'
            #print('JSON', method1[0], result)
            try:
                #yield result
                yield json.dumps(result, default=tools.decimal_default)
            except:
                yield result
        elif method1[0]=='_':    # 以下线开头的特殊方法, 注意要自行设置响应头
            yield from result
        elif method1.islower(): # 是小写，有对应模板
            #cherrypy.response.headers['Content-Type'] = 'text/html; charset=utf8'
            cherrypy.response.headers['Content-Type'] = 'application/json; charset=utf8'
            yield TemplateLookup(self._dirs).get_template(method1+'.html').render(**self._dic)
        else:   # 其他情况开头，直接报错
            raise 

    @cherrypy.tools.json_out()
    def Get(self, *k, **kw):
        """返回数据，以json格式"""
        return {'a':3.0003}

    def __del__(self):
        print(self._cls_cnt, self.__class__._cls_cnt)
        self.__class__._cls_cnt -= 1
        # 清理思路： 确保每个类实例处理一次HTTP调用，在类摧毁时，关闭或释放数据库连接
        pass

if __name__ not in ('__main__', '__mp_main__'):
    __import__(__name__, {}, {}, [x for x in os.listdir(__name__.replace('.', os.sep)) if x.count('.')<1])
