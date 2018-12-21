from uiautoTest import uiautoTest
from loadUtil import load_file
import stomp
import time
topic_name='/topic/interTopic'

error=[]
fail=[]
success=[]
skip=[]

datas=load_file("D:\\UIauto\\testdemo.xlsx")
config=datas.get('config')
cases=datas.get("cases")


class SampleListener(stomp.ConnectionListener):
    def __init__(self, conn, lists):
        self.conn = conn
        self.lists = lists

    def on_message(self, headers, message):
        # print ('headers: %s' % headers)
        print('message: %s' % message)
        if message == 'stop':
            self.on_disconnected()
        elif message=='begin':
            auto.setconfig(config.get('logfile'), config.get('imgpath'), config.get('appname'))
        else:
            for case in self.lists:
                if case.get('mq')==message:
                    time.sleep(2)
                    auto.execute( case.get('action'), case.get('control'),
                                 case.get('value'))

    def on_error(self, headers, message):
        print('[%s]received an error %s' % (message, time.strftime("%Y-%m-%d %H:%M:%S")))

    def on_disconnected(self):
        self.conn.disconnect()
        # connect_and_subscribe(self.conn)
def receive_from_topic(lists):
    conn=stomp.Connection([('127.0.0.1', 61613)])
    conn.set_listener('',SampleListener(conn,lists))
    conn.start()
    conn.connect()
    print('等待mq消费')
    conn.subscribe(destination=topic_name, id='4', ack='auto')
    while True:
        pass
        # conn.subscribe(destination=topic_name,id=4,ack='auto')
    # conn.disconnect()

auto=uiautoTest()

receive_from_topic(cases)





