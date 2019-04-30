#! 
#   -*- coding: utf-8   -*-

if __name__ == '__main__':
    import os, sys, cherrypy, multiprocessing, threading, time
    print('main pid', os.getpid())
    main_pid = os.getpid()  # 其他地方获取: sys.modules['__mp_main__'].main_pid
    sys.pid = main_pid
    pools = multiprocessing.Pool(4)     # 只能在__main__中开进程池，但如何让模块中的函数使用此进程池呢？
    time.sleep(5)
    conf = os.path.abspath(__file__)[:-2] + 'conf'
    fp = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(fp))
    os.chdir(os.path.dirname(fp))
    Root = __import__(os.path.basename(fp))
    cherrypy.quickstart(Root,config=conf)
    sys.exit()  #   这一句增加以后， 不会再执行后面的，从而避免了重复导入
else:
    print('name: ', __name__, os.getpid())
