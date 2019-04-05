#   -*- coding: utf-8 -*-
#   $Header$

from .. import default
import os

class default(default):
    _dirs = default._dirs + [os.path.dirname(__file__)] # 模板搜索路径，属于类静态变量，所以宁愿每个类写死
    #print('大肠埃希菌ult', dir(default.__class__), default._dirs)  # 这儿的defult， 从命名空间上来看，还是上级目录的default

    def __init__(self, *k, **kw):
        # 是先初始化，还是最后初始化？
        #print(self._dirs)
        #print('k kw', k, kw)
        super(default, self).__init__(*k, *kw)

__import__(__name__, {}, {}, [x for x in os.listdir(__name__.replace('.', os.sep)) if x.count('.')<1])
