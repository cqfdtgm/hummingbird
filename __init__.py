#   -*- coding: utf-8 -*-
#   $Header$


if __name__ == '__main__':
    import cherrypy
    import os, sys
    conf = os.path.abspath(__file__)[:-2] + 'conf'
    fp = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(fp))
    os.chdir(os.path.dirname(fp))
    Root = __import__(os.path.basename(fp))
    cherrypy.quickstart(Root,config=conf)
    sys.exit()

class default(object):
    exposed = True
    _cls_cnt = 0

    def __init__(self, *k, **kw):
        self.__class__._cls_cnt += 1
        pass

    def __iter__(self):
        yield 'Hello world!'

    def __del__(self):
        print(self._cls_cnt, self.__class__._cls_cnt)
        self.__class__._cls_cnt -= 1
        pass

if __name__ not in ('__main__', '_mp__main__'):
    import os
    print(__name__, os.getcwd())
    #print(__name__, {}, {}, [x for x in os.listdir(__name__, replace('.', os
    # 尝试导入所有下级目录， 会自动映射为下级URL。
    __import__(__name__, {}, {}, [x for x in os.listdir(__name__.replace('.', os.sep)) if x.count('.')<1])
    #def x
