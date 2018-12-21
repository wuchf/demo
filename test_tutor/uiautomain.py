import atexit
import stomp
import time
import os
import logging

from uiautoTest import *
from mqsendUtil import send_inter_topic as send
from loadUtil import *
from reportUtil import *

#互动交互mq
topic_name='/topic/interTopic'
#反馈互动结果mq
reback_name='/topic/rebackTopic'
# logging.info(cases)

error = []  # 保存用例步骤执行失败的用例名
fail = []  # 保存用例验证失败的用例名
success = []  # 保存用例执行成功的用例名（步骤执行成功，验证通过)
skip = []  # 保存没有被执行的用例（包含tm为0的用例和skipif中需要跳过的用例)

# logger.log_info('hahahahhahhaha')
class SampleListener(stomp.ConnectionListener):
    def __init__(self, conn, lists,config,fun,queue):
        self.conn = conn
        self.lists = lists
        self.conf=config
        self.fn=fun
        self.q=queue

    def run(self,case,res=[],check_res=[]):
        for step in case['steps']:
            _res = self.fn.execute(step['action'], step['control'], step['value'])
            res.append(_res)
        if len(res)==len([x for x in res if x==True]):  # 如果都执行成功
            # if case['mq']:
            send(reback_name,self.conf.get('mqip'), case['mq']+'ok')#mq回馈执行结果
            if case['validate']:  # 有验证的信息
                for _validate in case['validate']:
                    _check = self.fn.validate(_validate['value1'], _validate['operation'], _validate['value2'],
                                           _validate['action'])
                    check_res.append(_check)
            else:
                check_res.append(True)
                # success.append(case['name'])
        else:
            error.append((case['name'],[x for x in res if x!=True]))
            send(reback_name,self.conf.get('mqip'), case['mq'] + 'fail')

    def on_message(self, headers, message):
        # logging.info ('headers: %s' % headers)
        logging.info('message: %s' % message)
        #互动段发送stop指令，即脚本运行结束，定制mq接受，也给答题器脚本发送停止指令
        if message == 'stop':
            self.conn.term=True
            ##通知答题器结束，结束ipc通道
            print("结束")
            logging.info("结束")
            self.q.put("finish")
        elif message=='begin':
            self.fn.setconfig(self.conf.get('logfile'), self.conf.get('imgpath'),self.conf.get('saveimg'))
            send(reback_name,self.conf.get('mqip'),'beginok')
        else:
            for case in self.lists:
                if message==case['mq']:##只有在收到指定的mq值之后才会运行
                    res = []  # 保存步骤执行结果
                    check_res = []  # 保存验证结果
                    logging.info(f'用例编号为==%s' % case['no'])
                    if case['tm']:
                        tm = int(case['tm'])
                    else:
                        tm = 1
                    if tm == 0:  # 如果tm为0，就直接跳过不执行
                        skip.append((case['name'],"执行次数为0，不执行直接跳过"))
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
                            logging.info('skipif 执行后的结果为{}'.format(_skip_res))
                            if len(_skip_res)==len([x for x in _skip_res if x==True]):  # 不执行条件都成功了，才运行用例
                                skip.append((case['name'],'运行不执行条件，结果为{}，跳过'.format(_skip_res)))
                            else:
                                self.run(case, res, check_res)
                    if len(check_res)!=len([x for x in check_res if x==True]):
                        fail.append((case['name'],[x for x in check_res if x!=True]))
                    # 步骤都成功，验证都成功，且用例名不再skip中，用例执行成功
                    if len(res)==len([x for x in res if x==True]) and len(check_res)==len([x for x in check_res if x==True]) and case['name'] not in [x[0] for x in skip]:
                        success.append(case['name'])

    def on_error(self, headers, message):
        logging.info('[%s]received an error %s' % (message, time.strftime("%Y-%m-%d %H:%M:%S")))

class amqconnection(object):
    def __init__(self,lists,config,fun,queue):
        self.conn = stomp.Connection([(config.get('mqip'), 61613)])
        self.conn.set_listener("", SampleListener(self,lists,config,fun,queue))
        self.conn.start()
        self.conn.connect()
        logging.info("等待mq消费")
        self.conn.subscribe(topic_name, "4", "auto")
        atexit.register(self.close)
        self.term = False

    def run_forver(self):
        while not self.term:
            time.sleep(5)

    def close(self):
        self.conn.disconnect()
        logging.info("mq链接断开")


def run(config,cases,queue):
    tm_start=time.time()
    test = uiautoTest()
    amq=amqconnection(cases,config,test,queue)
    amq.run_forver()
    tm_end=time.time()
    print(f'执行成功=={success}')
    print(f'执行失败=={error}')
    print(f'验证失败=={fail}')
    print(f'跳过不执行=={skip}')
    _result={"success":success,"error":error,"fail":fail,"skip":skip}
    print(_result)
    tm=tm_end-em_start
    print(tm)
    fp=open("tutor_pc_result.html",'wb')
    res = result(tm, fp, title="UI自动化测试报告", tutorpc=_result)
    res.generatereport()


if __name__ == '__main__':
    filename="D:\\UIauto\\test.json"
    # filename = sys.argv[1]
    logging.info(filename)
    con = load_file(filename)
    logging.info(con)
    cases = con.get('testcases')
    config = con.get('config')
    run(config,cases)
