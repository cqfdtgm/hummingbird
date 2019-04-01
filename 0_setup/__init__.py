#   -*- coding: utf-8 -*-
#   $Header$

from .. import default
import os

class default(default):

    def __init__(self, *k, **kw):
        # 是先初始化，还是最后初始化？
        super(default, self).__init__(self, *k, **kw)
        self.__class__._cls_cnt += 1
        pass

    def __iter__(self):
        yield 'hello 0_setup!'

        print(self._cls_cnt, self.__class__._cls_cnt)
        self.__class__._cls_cnt -= 1
        pass

__import__(__name__, {}, {}, [x for x in os.listdir(__name__.replace('.', os.sep)) if x.count('.')<1])
