#! 
#   -*- coding: utf-8   -*-

if __name__ == '__main__':
    import os, sys, cherrypy, multiprocessing, threading, time
    print('main pid', os.getpid())
    main_pid = os.getpid()  # �����ط���ȡ: sys.modules['__mp_main__'].main_pid
    sys.pid = main_pid
    pools = multiprocessing.Pool(4)     # ֻ����__main__�п����̳أ��������ģ���еĺ���ʹ�ô˽��̳��أ�
    time.sleep(5)
    conf = os.path.abspath(__file__)[:-2] + 'conf'
    fp = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(fp))
    os.chdir(os.path.dirname(fp))
    Root = __import__(os.path.basename(fp))
    cherrypy.quickstart(Root,config=conf)
    sys.exit()  #   ��һ�������Ժ� ������ִ�к���ģ��Ӷ��������ظ�����
else:
    print('name: ', __name__, os.getpid())
