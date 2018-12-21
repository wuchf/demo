import multiprocessing
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor
import sys
from queue import Queue
from uiautomain import run as autotest
from win32server import run as ipcserver
from socketcli import run as client
# import client
from win32client import run as ipc
from loadUtil import *
import logging


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
# logging.basicConfig(filename='my.log', level=logging.DEBUG, format=LOG_FORMAT)

if __name__ == '__main__':
    filename="../test.json"
    # filename = sys.argv[1]
    #print(filename)
    con = load_file(filename)
    #print(con)
    cases = con.get('testcases')
    config = con.get('config')
    ip=config['mqip']
    logfile=config['logfile']
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format=LOG_FORMAT)
    #如果配置环境中devicenum为""，则默认只有一个答题器
    devicenum=config['devicenum'] if config['devicenum'] else 0
    #作答类型，1：选择题作答A，判断题做法T，2：选择题作答B，判断题作答F，3：选择题作答C，判断题做法T，4：选择题作答D，判断题做法F,其他值：随机作答，如选择，随机按A，B，C，D，如判断题，随机选择T，F，
    answertype=config['answertype']
    minnum = config['minnum']
    maxnum = config['maxnum']
    answertype = config['answertype']
    # ip=sys.argv[2]
    logging.info (ip)
    futures = list()
    q=Queue()
    with ThreadPoolExecutor() as pool:
        # pool.submit(ipcserver,ip)
        # pool.submit(client,ip,devicenum,answertype)
        pool.submit(ipc,q,devicenum,answertype,minnum,maxnum)
        pool.submit(autotest,config,cases,q)