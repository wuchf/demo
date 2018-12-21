import win32pipe
import win32file
import time
import threading
import struct
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED, ALL_COMPLETED
import gc
import logging

import socket

from mqsendUtil import send_inter_topic as send

PIPE_NAME = r"\\.\pipe\ss-answer-tool-D27DFDD9-E25D-4976-A4D3-6179C2000B4C"
PIPE_LOCAL = r'\\.\pipe\test'
PIPE_BUFFER_SIZE = 1024

answer_name = '/topic/answerTopic'  # 答题器的topic

lock2 = threading.Lock()


class server():
    def __init__(self, mqip):
        self.named_pipe = win32pipe.CreateNamedPipe(PIPE_NAME,
                                                    win32pipe.PIPE_ACCESS_DUPLEX | win32file.FILE_FLAG_OVERLAPPED,
                                                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT | win32pipe.PIPE_READMODE_MESSAGE,
                                                    win32pipe.PIPE_UNLIMITED_INSTANCES,
                                                    PIPE_BUFFER_SIZE,
                                                    0,
                                                    600,
                                                    None)
        # self.file_handle = win32file.CreateFile(PIPE_NAME,
        #                                         win32file.GENERIC_READ | win32file.GENERIC_WRITE,
        #                                         win32file.FILE_SHARE_WRITE, None,
        #                                         win32file.OPEN_EXISTING, 0, None)

        self.ip = mqip
        self.flag = True
        # global lock

    def read1(self, lock):
        try:
            while self.flag:
                print("读取信息")
                try:
                    # print("waiting for inter client")
                    conn = win32pipe.ConnectNamedPipe(self.named_pipe, None)
                    # print("got inter client")
                    if conn:
                        _str = tobuff(8, 202, b'{}')
                        # print(f'写入ipc管道的信息为== {_str}')
                        # lock.acquire()
                        with lock:
                            print('发送心跳 开始')
                            win32file.WriteFile(self.named_pipe, _str)
                            print("发送心跳 结束")
                        time.sleep(1)
                        future = []
                        with ThreadPoolExecutor(max_workers=50) as pool:
                            # for i in range(10):
                            # future.append(pool.submit(win32file.ReadFile, self.named_pipe, PIPE_BUFFER_SIZE, None))
                            # print(i)
                            future = [pool.submit(win32file.ReadFile, self.named_pipe, PIPE_BUFFER_SIZE, None) for i in range(5)]
                        # future.append(win32file.ReadFile(self.named_pipe, PIPE_BUFFER_SIZE, None))
                        # s = win32file.ReadFile(self.named_pipe, PIPE_BUFFER_SIZE, None)
                        # print(s)
                        # future.append(s)
                        # pool.shutdown()
                        # threading.Thread(target=win32file.ReadFile(self.named_pipe, PIPE_BUFFER_SIZE, None)).start()
                        #
                        # future.append(s)
                        # print(s)
                        # time.sleep(1)
                        print("readfile 结束")
                        for d in future:
                            try:
                                # data = d
                                data = d.result(timeout=1)
                                print(data)
                            except Exception as e:
                                print("错误信息为%s" % e)
                                continue
                            if data is None or len(data) < 2:
                                del data
                                # pass
                            print(f'ipc管道从互动端收到的信息为=={data}')
                            if (len(data[1]) > 12):
                                if hex(data[1][0]) in ['0xe4', '0x08', '0xe2']:
                                    _res = data[1][12:]
                                elif data[1][0] == '{':
                                    _res = data[1]
                                else:
                                    _res = None
                                # _res = "{'test': '%s'}" % '0x00'
                                print(f"给答题器发送的信息为=={_res}")
                                if _res:
                                    send(answer_name, self.ip, _res)
                                del data
                        # lock.release()
                    # time.sleep(0)
                    # gc.collect()
                except BaseException as e:
                    print("read1 exception:", e)
                    break
            print("命名管道要关闭通道啦")
        finally:
            try:
                print('关闭通道')
                win32pipe.DisconnectNamedPipe(self.named_pipe)
            except:
                pass

    def read3(self, lock):
        # global lock
        try:
            ip_port = ('127.0.0.1', 9999)
            sk = socket.socket()
            sk.bind(ip_port)
            sk.listen(5)
            conn, addr = sk.accept()
            print('socket accept')
            while self.flag:
                print('写信息')
                data = conn.recv(PIPE_BUFFER_SIZE)
                print(f'socket服务端收到的信息为=={data}')
                if (len(data) > 0):
                    if data.decode() != 'finish':
                        _str = tobuff(2018, 2018, data)
                        print(f'ipc管道发给互动端的信息为=={_str+data}')
                        # with lock:
                        # lock.acquire()
                        with lock:
                            print('writefile ing...')
                            win32file.WriteFile(self.named_pipe, _str + data)
                        # lock.release()
                        print("writefile 结束")
                    else:
                        self.flag = False
                        break
                # else:
                #     _str = tobuff(8, 202, b'{}')
                #     print(f'写入ipc管道的信息为== {_str}')
                #     with lock:
                #         win32file.WriteFile(self.named_pipe, _str)
                #     print("发送心跳 结束")

            # 死循环跳出
            print('socket监听结束啦')
            sk.close()
        except:
            print('===========================================')

    def heart(self, lock):
        try:
            while self.flag:
                print("心跳")
                try:
                    conn = win32pipe.ConnectNamedPipe(self.named_pipe, None)
                    if conn:
                        _str = tobuff(8, 202, b'{}')
                        print(f'写入ipc管道的信息为== {_str}')
                        with lock:
                            win32file.WriteFile(self.named_pipe, _str)
                        print("写入心跳结束")
                        time.sleep(5)
                    else:
                        time.sleep(0.1)
                        print("心跳命名管道还未连接")
                        continue
                except BaseException as e:
                    print("read1 exception:", e)
                    break
            print("命名管道要关闭通道啦")
        finally:
            try:
                print('关闭通道')
                win32pipe.DisconnectNamedPipe(self.named_pipe)
            except:
                pass


def tobuff(type, command, json):
    # 取消左右的{}
    leng = len(json.decode())
    # 将数据转化为buffer格式
    if leng <= 2:
        _str = struct.pack('iii', type, 0, command)
    else:
        _str = struct.pack('iii', type, leng, command)
    return _str


def run(ip):
    ser = server(ip)
    # ser.Run()
    threads = []
    lock = threading.Lock()
    # t3 = threading.Thread(target=ser.heart, args=(lock,))
    # threads.append(t3)
    t2 = threading.Thread(target=ser.read3, args=(lock,))
    threads.append(t2)
    t1 = threading.Thread(target=ser.read1, args=(lock,))
    threads.append(t1)

    for i in range(len(threads)):
        threads[i].start()
    for i in range(len(threads)):
        threads[i].join(3)


if __name__ == '__main__':
    ip = "10.12.15.184"
    run(ip)
