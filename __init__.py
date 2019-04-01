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


