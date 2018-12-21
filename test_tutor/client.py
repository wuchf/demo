import socket
import win32file
import win32pipe
import atexit
import stomp
import time
import traceback
import json
import random
import logging

import struct

answer_topic='/topic/answerTopic'
PIPE_NAME=r"\\.\pipe\ss-answer-tool-D27DFDD9-E25D-4976-A4D3-6179C2000B4C"

init = '{"command":"init","preferred-device-type":"any"}'
active = '{"id":"7a451010-1b03-459d-a62b-1bcfbb1f2727","event":"activated","device":"%s"}'
avadevice = '{"avaliable-device":"audio","event":"device-inited","id":"5a0e3a0f-0976-4735-96eb-e578b4f26666","ready":true}'
choiceanswer = '{"custom":"","data":null,"device":"%s","event":"key-pressed","extra":"","id":"7d479ba3-7868-4e4e-a00f-297261f02020","key":"%s"}'
judgeanswer = '{"custom":"","data":null,"device":"%s","event":"key-pressed","extra":"","id":"7d479ba3-7868-4e4e-a00f-297261f02021","key":"%s"}'
centeranswer = '{"custom":"","data":null,"device":"%s","event":"key-pressed","extra":"","id":"7d479ba3-7868-4e4e-a00f-297261f02022","key":"G"}'


class pipe_write():
    def __init__(self):
        self.handle=win32file.CreateFile(PIPE_NAME,
                                         win32file.GENERIC_WRITE,
                                         win32file.FILE_SHARE_WRITE,None,
                                         win32file.OPEN_EXISTING,
                                         0,None)
    def write(self,msg):
        res=win32pipe.SetNamedPipeHandleState(self.handle,win32pipe.PIPE_READMODE_MESSAGE)
        if res==0:
            print(f"SetNamedPipeHandleState 返回的信息为：{res}")
        try:
            _str = tobuff(2018, 2018, msg)
            win32file.WriteFile(self.handle, _str + bytes(msg))
        except Exception as e:
            print("失败信息为%s"%e)
        
def tobuff(type,command,json):
    #取消左右的{}
    leng = len(json.decode())
    # 将数据转化为buffer格式
    if leng<=2:
        _str = struct.pack('iii', type, 0, command)
    else:
        _str = struct.pack('iii', type, leng, command)
    return _str

class SampleListener(stomp.ConnectionListener,pipe_write):
    def __init__(self,amq,devicesnum,answertype):
        self.conn=amq
        self.num=devicesnum
        self.answertype=answertype
        self.pipe=pipe_write()
    def on_message(self, headers, message):
        # logging.info ('headers: %s' % headers)
        logging.info('收到互动端的反回信息为== %s' % message)
        try:
            res = json.loads(message)
            command = res['command']
            if command=='stop':
                pass
            elif command=='init':
                self.pipe.write(avadevice)
                time.sleep(5)
                #等待10s后进行激活
                for i in range(1,int(self.num)+1):
                    # time.sleep(10)
                    self.pipe.write(active%i)
            elif command == 'ask':
                if res['type']=='single-choice' and res['device']=="0":
                    logging.info("选择题类型题目")
                    for i in range(1, int(self.num) + 1):
                        if self.answertype == 1:
                            answer = "A"
                        elif self.answertype == 2:
                            answer = "B"
                        elif self.answertype == 3:
                            answer = "C"
                        elif self.answertype == 4:
                            answer = "D"
                        else:
                            answer = random.choice(['A', 'B', 'C', 'D'])
                        self.pipe.write(choiceanswer%(i,answer))

                elif res['type']=='true-false' and res['device']=="0":
                    logging.info("判断类型题目")
                    for i in range(1, int(self.num) + 1):
                        if self.answertype == 1:
                            answer = "T"
                        elif self.answertype == 2:
                            answer = "F"
                        elif self.answertype == 3:
                            answer = "T"
                        elif self.answertype == 4:
                            answer = "T"
                        else:
                            answer = random.choice(['T', 'F'])
                        self.pipe.write(judgeanswer%(i,answer))
                elif res['type']== 'continous-red-envelope':
                    logging.info("多次投票类型题目")
                    for i in range(1, int(self.num) + 1):
                        #随机按键次数
                        for  j in range(random.randint(1,10)):
                            self.pipe.write(centeranswer % i)
                elif res['type']== 'red-envelope' and res['device']=="0":
                    #中间键G
                    logging.info("投票类型题目")
                    for i in range(1, int(self.num) + 1):
                        self.pipe.write(centeranswer%i)
            elif command == 'finish':#z互动端不直接发起断开的指令，所以直接从脚本发起
                # self.pipe.write("finish")#发送finish，表示数据传输已完成，断开连接
                self.conn.term=True
            else:
                pass
        except Exception as e:
            logging.info ('出现错误啦，错误信息为%s'%e)
            traceback.print_exc()

    def on_error(self, headers, message):
        logging.info('[%s]received an error %s' % (message, time.strftime("%Y-%m-%d %H:%M:%S")))

    # def on_disconnected(self):
        # self.conn.disconnect()
        # connect_and_subscribe(self.conn)

#mq接受不断开
def receive_from_topic(ip,devicesnum,answertype):
    conn=stomp.Connection([(ip, 61613)])
    conn.set_listener('',SampleListener(conn,devicesnum,answertype))
    conn.start()
    conn.connect()
    logging.info ('等待互动端返回消息')
    conn.subscribe(destination=answer_topic, id="4", ack='auto')
    while True:
        pass
        # conn.subscribe(destination=topic_name,id=4,ack='auto')
    # conn.disconnect()

class amqconnection(object):
    def __init__(self,ip,devicesnum,answertype):
        self.conn=stomp.Connection([(ip, 61613)])
        self.conn.set_listener("",SampleListener(self,devicesnum,answertype))
        self.conn.start()
        self.conn.connect()
        logging.info ("等待互动端返回消息")
        self.conn.subscribe(answer_topic,"4","auto")
        atexit.register(self.close)
        self.term=False

    def run_forver(self):
        while not self.term:
            time.sleep(5)

    def close(self):
        self.conn.disconnect()
        logging.info("mq链接断开")


def run(ip,devicesnum,answertype):
    # receive_from_topic(ip)
    amq=amqconnection(ip,devicesnum,answertype)
    amq.run_forver()
if __name__ == '__main__':
    ip = "10.12.15.184"
    # run(ip)