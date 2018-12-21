import socket

import atexit
import stomp
import time
import traceback
import json
import random
import logging

answer_topic = '/topic/answerTopic'

init = '{"command":"init","preferred-device-type":"any"}'
active = '{"id":"7a451010-1b03-459d-a62b-1bcfbb1f2727","event":"activated","device":"%s"}'
avadevice = '{"avaliable-device":"audio","event":"device-inited","id":"5a0e3a0f-0976-4735-96eb-e578b4f26666","ready":true}'
choiceanswer = '{"custom":"","data":null,"device":"%s","event":"key-pressed","extra":"","id":"7d479ba3-7868-4e4e-a00f-297261f02020","key":"%s"}'
judgeanswer = '{"custom":"","data":null,"device":"%s","event":"key-pressed","extra":"","id":"7d479ba3-7868-4e4e-a00f-297261f02021","key":"%s"}'
centeranswer = '{"custom":"","data":null,"device":"%s","event":"key-pressed","extra":"","id":"7d479ba3-7868-4e4e-a00f-297261f02022","key":"G"}'

textmessage = []

sk = socket.socket()

def client(msg):
    print('===========================================================', msg)
    logging.info(f"socket客户端发送的信息为=={msg}")
    sk.sendall(bytes(msg, encoding='utf8'))
    # sk.close()


class SampleListener(stomp.ConnectionListener):
    def __init__(self, amq, devicesnum, answertype):
        self.conn = amq
        self.num = devicesnum
        self.answertype = answertype

    def on_message(self, headers, message):
        # logging.info ('headers: %s' % headers)
        print('收到互动端的反回信息为== %s' % message)
        try:
            res = json.loads(message)
            command = res['command']
            if command == 'stop':
                pass
            elif command == 'init':
                client(avadevice)
                time.sleep(5)
                # 等待10s后进行激活
                for i in range(1, int(self.num) + 1):
                    # time.sleep(10)
                    client(active % i)
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
                        client(choiceanswer % (i, answer))
                        # time.sleep(2)

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
                        client(judgeanswer % (i, answer))
                elif res['type'] == 'continous-red-envelope':
                    logging.info("多次投票类型题目")
                    for i in range(1, int(self.num) + 1):
                        # 随机按键次数
                        for j in range(random.randint(1, 10)):
                            client(centeranswer % i)
                elif res['type'] == 'red-envelope' and res['device'] == "0":
                    # 中间键G
                    logging.info("投票类型题目")
                    for i in range(1, int(self.num) + 1):
                        client(centeranswer % i)
            elif command == 'finish':  # z互动端不直接发起断开的指令，所以直接从脚本发起
                print('finish')
                client("finish")  # 发送finish，表示数据传输已完成，断开连接
                self.conn.term = True
            else:
                pass
        except Exception as e:
            logging.info('出现错误啦，错误信息为%s' % e)
            traceback.print_exc()

    def on_error(self, headers, message):
        logging.info('[%s]received an error %s' % (message, time.strftime("%Y-%m-%d %H:%M:%S")))

    # def on_disconnected(self):
    # self.conn.disconnect()
    # connect_and_subscribe(self.conn)


# mq接受不断开
def receive_from_topic(ip, devicesnum, answertype):
    conn = stomp.Connection([(ip, 61613)])
    conn.set_listener('', SampleListener(conn, devicesnum, answertype))
    conn.start()
    conn.connect()
    logging.info('等待互动端返回消息')
    conn.subscribe(destination=answer_topic, id="4", ack='auto')
    while True:
        pass
        # conn.subscribe(destination=topic_name,id=4,ack='auto')
    # conn.disconnect()


class amqconnection(object):
    def __init__(self, ip, devicesnum, answertype):
        self.conn = stomp.Connection([(ip, 61613)])
        self.conn.set_listener("", SampleListener(self, devicesnum, answertype))
        self.conn.start()
        self.conn.connect()
        logging.info("等待互动端返回消息")
        self.conn.subscribe(answer_topic, "4", "auto")
        atexit.register(self.close)
        self.term = False

    def run_forver(self):
        while not self.term:
            time.sleep(5)

    def close(self):
        self.conn.disconnect()
        logging.info("mq链接断开")


def run(ip, devicesnum, answertype):
    # receive_from_topic(ip)
    ip_port = ('127.0.0.1', 9999)
    sk.connect(ip_port)
    amq = amqconnection(ip, devicesnum, answertype)
    amq.run_forver()


if __name__ == '__main__':
    ip = "10.12.15.184"
    # run(ip)
