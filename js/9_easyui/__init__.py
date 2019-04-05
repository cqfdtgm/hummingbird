# -*- coding: utf-8 -*-
# $Header: D:\\RCS\\D\\python_study\\cherrypy\\dragonfly.py,v 1.2 2011-10-06 23:17:31+08 administrator Exp administrator $

name = 'easyui演示' # 这个变量如果中间有空格的话, 在easyui tree里, 不能直接作用<a href加的链接, 很奇怪.

from .. import default

class default(default):
    def __init__(self, *k, **kw):
        super(default, self).__init__(*k, **kw)
        if len(self._k):
            self._dir = self._k[0]
            self._k = ('dir',)
        else:
            self._dic['left_tree'] = self.left_tree()

    def dir(self, *k, **kw):
        dir = os.path.dirname(os.path.abspath(self.__file__))
        dir = os.sep.join((dir, 'demo-mobile', self._dir))
        self._dic['dir'] = self._dir
        self._dic['files'] = os.listdir(dir)
        #self._dic['left_json'] = self.left_json()
        #self.__name__ =__name__
        #print ('init for easyui...')
        #print(sorted(globals().keys()))

    def left_tree(self):
        """以树形列表的形式,返回demo目录下的目录结构和html文件列表.
        以children表示子女, id表示层级, text表示本层的名称
        文件增加了点击时的链接"""

        result = []
        tree_dic = {}
        for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(self.__file__))+'\\demo-mobile', True):
            packge = '.'.join(root.split(os.path.sep)[1:])
            dic = tree_dic[packge] = dict(children=[], text=os.path.basename(root))
            if root == os.path.dirname(os.path.abspath(__file__))+'\\demo-mobile':
                dic['id'] = 1
                result.append(tree_dic[packge])
                continue
            parent = tree_dic['.'.join(root.split(os.path.sep)[1:-1])]
            dic['id'] = parent['id']*10+len(parent['children'])+1
            for f in files: 
                dic_f = dict(text=f)
                dic_f['id'] = dic['id']*10+len(dic['children'])
                dic['children'].append(dic_f)
            parent['children'].append(dic)
        return result

class left_tree(default):
    """test for self.left_tree's content"""

    def __iter__(self):
        yield json.dumps(self.left_tree())

__import__(__name__, {}, {}, [x.split('.')[0] for x in os.listdir(__name__.replace('.', os.sep))])

# $Log$
