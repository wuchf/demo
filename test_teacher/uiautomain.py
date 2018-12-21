import atexit
import stomp
import time
import os

from uiautoTest import *
from mqsendUtil import send_inter_topic as send
from loadUtil import *

topic_name='/topic/interTopic'
reback_name='/topic/rebackTopic'
# print(cases)

error = []  # 保存用例步骤执行失败的用例名
fail = []  # 保存用例验证失败的用例名
success = []  # 保存用例执行成功的用例名（步骤执行成功，验证通过)
skip = []  # 保存没有被执行的用例（包含tm为0的用例和skipif中需要跳过的用例)


class SampleListener(stomp.ConnectionListener):
    def __init__(self, conn, lists,config,fun):
        self.conn = conn
        self.lists = lists
        self.conf=config
        self.fn=fun

    def run(self,case,res=[],check_res=[]):
        for step in case['steps']:
            _res = self.fn.execute(step['action'], step['control'], step['value'])
            res.append(_res)
        if all(res):  # 如果都执行成功
            # if case['mq']:
            send(reback_name,self.conf.get('mqip'), self.conf.get('name')+'_'+case['mq']+'ok')#mq回馈执行结果
            if case['validate']:  # 有验证的信息
                for _validate in case['validate']:
                    _check = self.fn.validate(_validate['value1'], _validate['operation'], _validate['value2'],
                                           _validate['action'])
                    check_res.append(_check)
            else:
                check_res.append(True)
                # success.append(case['name'])
        else:
            error.append(case['name'])
            send(reback_name,self.conf.get('mqip'), self.conf.get('name')+'_'+case['mq'] + 'fail')

    def on_message(self, headers, message):
        # print ('headers: %s' % headers)
        print('message: %s' % message)
        if message == 'stop':
            print('结束啦')
            self.conn.term=True
            # self.on_disconnected()
        elif message=='begin':
            self.fn.setconfig(self.conf.get('logfile'), self.conf.get('imgpath'), self.conf.get('saveimg'))
            send(reback_name,self.conf.get('mqip'),self.conf.get('name')+'_beginok')
        else:
            # for case in self.lists:
            #     if case.get('mq')==message:
            #         time.sleep(2)
            #         auto.execute( case.get('action'), case.get('control'),
            #                      case.get('value'))
            for case in self.lists:
                if message==case['mq']:##只有在收到指定的mq值之后才会运行
                    res = []  # 保存步骤执行结果
                    check_res = []  # 保存验证结果
                    print(f'用例编号为==%s' % case['no'])
                    if case['tm']:
                        tm = int(case['tm'])
                    else:
                        tm = 1
                    if tm == 0:  # 如果tm为0，就直接跳过不执行
                        skip.append(case['name'])
                    for i in range(tm):
                        if not case['skipif']:  # 无执行用例的条件
                            self.run(case,res,check_res)
                        else:
                            _skip_res = []
                            for _skip in case['skipif']:
                                # 对于执行用例条件，可以判断已经执行过的用例名称，一执行过的用例执行通过了或者失败了才会运行
                                if _skip['operation'] in ['notin', 'ni']:
                                    _res = _skip['value1'] not in success
                                elif _skip['operation'] in ['in']:
                                    _res = _skip['value1'] in success
                                else:
                                    _res = self.fn.validate(_skip['value1'], _skip['operation'], _skip['value2'],
                                                         _skip['action'])
                                _skip_res.append(_res)
                            print('skipif 执行后的结果为{}'.format(_skip_res))
                            if all(_skip_res):  # 执行条件都成功了，才运行用例
                                self.run(case,res,check_res)
                            else:
                                skip.append(case['name'])
                    if not all(check_res):
                        fail.append(case['name'])
                    # 步骤都成功，验证都成功，且用例名不再skip中，用例执行成功
                    if all(res) and all(check_res) and case['name'] not in skip:
                        success.append(case['name'])

    def on_error(self, headers, message):
        print('[%s]received an error %s' % (message, time.strftime("%Y-%m-%d %H:%M:%S")))

    # def on_disconnected(self):
    #     self.conn.disconnect()
    #     # connect_and_subscribe(self.conn)
#不停止
def receive_from_topic(lists,config,fun):
    conn=stomp.Connection([(config.get('mqip'), 61613)])
    conn.set_listener('',SampleListener(conn,lists,config,fun))
    conn.start()
    conn.connect()
    print('等待mq消费')
    conn.subscribe(destination=topic_name, id='4', ack='auto')
    while True:
        # print("flag的取值为%s"%flag)
        pass
    # print('mq等待接受结束了')
        # conn.subscribe(destination=topic_name,id=4,ack='auto')
    # conn.disconnect()


class amqconnection(object):
    def __init__(self,lists,config,fun):
        self.conn = stomp.Connection([(config.get('mqip'), 61613)])
        self.conn.set_listener("", SampleListener(self,lists,config,fun))
        self.conn.start()
        self.conn.connect()
        print("等待mq消费")
        self.conn.subscribe(topic_name, "4", "auto")
        atexit.register(self.close)
        self.term = False

    def run_forver(self):
        while not self.term:
            time.sleep(5)

    def close(self):
        self.conn.disconnect()
        print("mq链接断开")


def run(config,cases):
    # 编译xcode
    # iproxy指令
    test = uiautoTest()
    amq=amqconnection(cases,config,test)
    amq.run_forver()
    # receive_from_topic(cases,config,test)

    print(f'执行成功=={success}')
    print(f'执行失败=={error}')
    print(f'验证失败=={fail}')
    print(f'跳过不执行=={skip}')

if __name__ == '__main__':
    filename = "C:\\Users\\test1\\Desktop\\uitest\\test.json"
    # filename = sys.argv[1]
    print(filename)
    con = load_file(filename)
    print(con)
    cases = con.get('testcases')
    config = con.get('config')
    ip = config['mqip']
    autotest(config, cases)