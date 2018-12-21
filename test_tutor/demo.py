# from pywinauto import application
# app=application.Application().start("C:\\Users\\wcf\\AppData\\Local\\Programs\\shuangshi-blackboard\\双师未来黑板.exe")
# app.notepad.TypeKeys("12345")
# app.notepad.menu_select(r"文件->另存为(A)")
# app.SaveAs.ComboBox5.select("UTF-8")
# app.SaveAs.edit1.set_text("Example-utf8.txt")
# app.SaveAs.Save.click()

import uiautomator2
from uiautomator import Device

import time
import sys

import stomp


topic_name='/topic/interTopic'
class MyListener(stomp.WaitingListener()):
    def on_error(self, headers, message):
        print('received an error "%s"' % message)
    def on_message(self, headers, message):
        print('received a message "%s"' % message)


# conn = stomp.Connection()
# conn.set_listener('', MyListener())
# conn.start()
# # conn.connect('admin', 'password', wait=True)
# conn.connect()
# conn.subscribe(destination='/queue/test', id=1, ack='auto')
#
# # conn.send(body=' '.join(sys.argv[1:]), destination='/queue/test')
# conn.send(body='hahahah ', destination='/queue/test')
#
# time.sleep(2)
# conn.disconnect()
def receive_from_topic():
    conn=stomp.Connection([('127.0.0.1', 61613)])
    conn.set_listener('',MyListener())
    conn.start()
    conn.connect()
    conn.subscribe(destination=topic_name,id=3,ack='auto')

    while True:
        try:
            time.sleep(900000)
        except:
            break

    # send_inter_topic('999')
    # time.sleep(3)
    # conn.disconnect()


    def run(self,case,res=[],check_res=[]):
        for step in case['steps']:
            _res = test.execute(step['action'], step['control'], step['value'])
            res.append(_res)
        if all(res):  # 如果都执行成功
            if case['mq']:
                send(topic_name, case['mq'])
            if case['validate']:  # 有验证的信息
                for _validate in case['validate']:
                    _check = test.validate(_validate['value1'], _validate['operation'], _validate['value2'],
                                           _validate['action'])
                    check_res.append(_check)
            else:
                check_res.append(True)
                # success.append(case['name'])
        else:
            error.append(case['name'])

    def on_message(self, headers, message):
        # print ('headers: %s' % headers)
        print('message: %s' % message)
        if message == 'stop':
            self.on_disconnected()
        elif message=='begin':
            test.setconfig(config.get('logfile'), config.get('imgpath'), config.get('appname'))
        else:
            # for case in self.lists:
            #     if case.get('mq')==message:
            #         time.sleep(2)
            #         auto.execute( case.get('action'), case.get('control'),
            #                      case.get('value'))
            for case in cases:
                print(case['no'])
                res = []  # 保存步骤执行结果
                check_res = []  # 保存验证结果
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
                                _res = test.validate(_skip['value1'], _skip['operation'], _skip['value2'],
                                                     _skip['action'])
                            _skip_res.append(_res)
                        print('skipif 执行后的结果为{}'.format(_skip_res))
                        if all(_skip_res):  # 执行条件都成功了，才运行用例
                            self.run(case,res,check_res)
                        else:
                            skip.append(case['name'])
                if not all(check_res):
                    fail.append(case['name'])
                # 步骤都成功，验证都成功，用例执行成功
                # 当用例skip之后，res和check_res为空，需处理
                if all(res) and all(check_res) and res and check_res:
                    success.append(case['name'])