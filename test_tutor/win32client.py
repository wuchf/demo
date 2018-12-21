import win32pipe
import win32file
import time
import threading
import struct
from concurrent.futures import  ThreadPoolExecutor ,as_completed
import json
import traceback
import logging
import random
import re
# from memory_profiler import profile
# from collections import deque

from mqsendUtil import send_inter_topic as send

PIPE_NAME=r"\\.\pipe\ss-answer-tool-D27DFDD9-E25D-4976-A4D3-6179C2000B4C"

PIPE_BUFFER_SIZE=655355


# answer_name='/topic/answerTopic'#答题器的topic

init = '{"command":"init","preferred-device-type":"any"}'
active = '{"id":"7a451010-1b03-459d-a62b-1bcfbb1f2727","event":"activated","device":"%s"}'
avadevice = '{"avaliable-device":"audio","event":"device-inited","id":"5a0e3a0f-0976-4735-96eb-e578b4f26666","ready":true}'
choiceanswer = '{"custom":"","data":null,"device":"%s","event":"key-pressed","extra":"","id":"7d479ba3-7868-4e4e-a00f-297261f02020","key":"%s"}'
judgeanswer = '{"custom":"","data":null,"device":"%s","event":"key-pressed","extra":"","id":"7d479ba3-7868-4e4e-a00f-297261f02021","key":"%s"}'
centeranswer = '{"custom":"","data":null,"device":"%s","event":"key-pressed","extra":"","id":"7d479ba3-7868-4e4e-a00f-297261f02022","key":"G"}'


# datas=deque()
datas=[]
lock=threading.Lock()
class server():
    def __init__(self,queue,devicesnum,answertype,minnum,maxnum):
        self.named_pipe=win32pipe.CreateNamedPipe(PIPE_NAME,
                                                      win32pipe.PIPE_ACCESS_DUPLEX | win32file.FILE_FLAG_OVERLAPPED,  #打开管道模式
                                                      win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT | win32pipe.PIPE_READMODE_MESSAGE,  #管道模式，传输数据模式
                                                      win32pipe.PIPE_UNLIMITED_INSTANCES,  #最大俩捏客户端的个数
                                                      PIPE_BUFFER_SIZE,  #输出缓冲区大小
                                                      PIPE_BUFFER_SIZE,  #输入缓冲区大小
                                                      600,  #默认超时时间
                                                      None)
        self.flag = True
        self.num = devicesnum
        self.answertype = answertype
        self.max=maxnum
        self.min=minnum
        self.q=queue  #当pad端退出之后，发送结束之类给互动端脚本，互动段发送queue是队列不为空
        # self.conn=win32pipe.ConnectNamedPipe(self.named_pipe, None)
    #@profile
    def heart(self):
        try:
            while self.q.empty():
                self.write_to_ipc('')
                time.sleep(4)
            logging.info("心跳停止循环")
        finally:
            try:
                print('关闭通道')
                win32pipe.DisconnectNamedPipe(self.named_pipe)
            except:
                pass
    # @profile
    def read(self):
        while  self.q.empty():
            try:
                conn = win32pipe.ConnectNamedPipe(self.named_pipe, None)
                # print(conn)
                if conn:
                    # with lock:
                    #     print("读取信息")
                    #     data=win32file.ReadFile(self.named_pipe, PIPE_BUFFER_SIZE, None)
                    #     print(f'ipc管道从互动端收到的信息为=={data}')
                    try:
                        with ThreadPoolExecutor() as pool:
                            _res=pool.submit(win32file.ReadFile, self.named_pipe, PIPE_BUFFER_SIZE, None)
                            # print(_res)
                            #当本机压力太大的时候，如果timeout时间太短，会收不到信息
                            data = _res.result(timeout=4)
                    except Exception as e:
                        data=None
                        print("readfile 失败，信息为：%s"%e)
                    if data is None or len(data) < 2:
                        continue
                    if (len(data[1]) > 12):
                        # datas.append(data[1])
                        if hex(data[1][0]) in ['0xe4', '0x08', '0xe2']:
                            _res = data[1][12:]
                        elif data[1][0] == '{':
                            _res = data[1]
                        else:
                            _res = None
                        print("保存的信息为：%s"%_res)
                        if _res:
                            # datas.append(_res)
                            self.write(_res)
                else:
                    time.sleep(0.1)
                    print("读取命名管道还未连接")
                    continue
            except Exception as e:
                print ("失败啦，信息为%s"%e)
        logging.info("读取信息停止循环")


    #@profile
    def write(self,data):
        # while self.flag:
        #     if len(datas)<=0:
        #         continue
        #     print(datas)
        #     # data=datas.popleft()
        #     data=datas.pop(0)
        #     print(f"处理的数据为:{data}")
            self.stop = False
            try:
                res = json.loads(data)
                print("json 信息为：%s"%res)
                command = res['command']
                if command == 'stop':
                    print("发送了结束答题指令")
                    self.stop=True
                elif command == 'init':
                    print("激活答题器")
                    self.write_to_ipc(avadevice)
                    time.sleep(5)
                    # 等待1s后进行激活
                    for i in range(1, int(self.num) + 1):
                        self.write_to_ipc(active % i)
                        time.sleep(0.1)
                elif command == 'ask':
                    if res['type'] == 'single-choice' and res['device'] == "0":
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
                            self.write_to_ipc(choiceanswer % (i, answer))
                            if self.stop:
                                print(f"答题器【{i}】还没有答题结束，但是互动已经发送了stop执行，停止答题")
                                break

                    elif res['type'] == 'true-false' and res['device'] == "0":
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
                            self.write_to_ipc(judgeanswer % (i, answer))
                            if self.stop:
                                print(f"答题器【{i}】还没有答题结束，但是互动已经发送了stop执行，停止答题")
                                break
                    elif res['type'] == 'continous-red-envelope':
                        logging.info("多次投票类型题目")
                        for i in range(1, int(self.num) + 1):
                            # 随机按键次数
                            for j in range(random.randint(int(self.min), int(self.max)+1)):
                                self.write_to_ipc(centeranswer % i)
                                if self.stop:
                                    print(f"答题器【{i}】还没有答题结束，但是互动已经发送了stop执行，停止答题")
                                    break
                            time.sleep(0.1)
                            break
                    elif res['type'] == 'red-envelope' and res['device'] == "0":
                        # 中间键G
                        logging.info("投票类型题目")
                        for i in range(1, int(self.num) + 1):
                            self.write_to_ipc(centeranswer % i)
                            if self.stop:
                                print(f"答题器【{i}】还没有答题结束，但是互动已经发送了stop执行，停止答题")
                                break
                else:
                    pass
            except Exception as e:
                print('出现错误啦，错误信息为%s' % e)
                traceback.print_exc()
    #@profile
    def write_to_ipc(self,data):
        #print (f'socket服务端收到的信息为=={data}')
        try:
            conn = win32pipe.ConnectNamedPipe(self.named_pipe, None)
            if conn:
                print("write_to_ipc 的信息为%s"%data)
                # print(data)
                if(len(data)>0):
                    _str = tobuff(2018, 2018, data)
                    try:
                        with lock:
                            print(f'ipc管道发给互动端的信息为=={_str+bytes(data,encoding="utf-8")}')
                            win32file.WriteFile(self.named_pipe, _str + bytes(data,encoding="utf-8"))
                            print("writefile finish")
                    except Exception as e:
                        print("答题信息出错：%s"%e)
                else:
                    _str = tobuff(8, 202, b'{}')
                    print(f'写入ipc管道的信息为== {_str}')
                    try:
                        with lock:
                            print('heart begin')
                            win32file.WriteFile(self.named_pipe, _str)
                            print("heart finish")
                    except Exception  as e:
                        print("心跳出错:%s"%e)
        except BaseException as e:
            print("write_to_ipc 出错了:", e)
#@profile
def tobuff(type,command,json):
    #取消左右的{}
    try:
        leng = len(json.decode())
    except Exception as e:
        leng = len(json)
    # 将数据转化为buffer格式
    if leng<=2:
        _str = struct.pack('iii', type, 0, command)
    else:
        _str = struct.pack('iii', type, leng, command)
    return _str
#@profile
def run(queue,devicenum,type,minnum,maxnum):
    ser = server(queue,devicenum,type,minnum,maxnum)
    # ser.Run()
    threads = []
    t1 = threading.Thread(target=ser.heart, args=())
    threads.append(t1)
    t2 = threading.Thread(target=ser.read, args=())
    threads.append(t2)
    # t3 = threading.Thread(target=ser.write, args=())
    # threads.append(t3)
    for i in range(len(threads)):
        threads[i].start()
    for i in range(len(threads)):
        threads[i].join(0.5)

if __name__ == '__main__':
    run(1,0,0,50)


