# import stomp
# import time
# queue_name='/queue/sampleQueue'
# topic_name='/topic/interTopic'
# listener_name='sampleListener'
# flag=True
# class SampleListener(stomp.ConnectionListener):
#     def __init__(self,conn):
#         self.conn=conn
#     def on_message(self, headers, message):
#         # print ('headers: %s' % headers)
#         print ('message: %s' % message)
#         if message=='stop':
#             self.on_disconnected()
#
#     def on_error(self, headers, message):
#         print('[%s]received an error %s' % (message, time.strftime("%Y-%m-%d %H:%M:%S")))
#
#     def on_disconnected(self):
#         self.conn.disconnect()
#         # connect_and_subscribe(self.conn)
#
#
# def receive_from_topic():
#     conn=stomp.Connection([('127.0.0.1', 61613)])
#     conn.set_listener('',SampleListener(conn))
#     conn.start()
#     conn.connect()
#     conn.subscribe(destination=topic_name, id=4, ack='auto')
#     while True:
#         pass
#         # conn.subscribe(destination=topic_name,id=4,ack='auto')
#     # conn.disconnect()
#
# if __name__ == '__main__':
#     receive_from_topic()



# -*- coding:UTF-8 -*-
import atexit
import time
import logging

import stomp



# logger = logging.getLogger(__name__)


class AMQListener(stomp.ConnectionListener):
    def __init__(self, amq):
        super(AMQListener, self).__init__()
        self.amq = amq

    def on_error(self, headers, message):
        print('Python received an error "%s"' % message)

    def on_message(self, headers, message):
        print("Python received: %s" % message)
        # self.amq.send("Hello ActiveMQ")
        self.amq.term = True


class AMQConnection(object):
    HOST = "localhost"
    PORT = 61613
    DEST_REQ = "demoRequest"
    # DEST_RESP = "demoResponse"

    def __init__(self):
        self.conn = stomp.Connection([(self.HOST, self.PORT)])
        self.conn.set_listener(self.DEST_REQ, AMQListener(self))
        self.conn.start()
        self.conn.connect()
        print('wait to subscribe')
        self.conn.subscribe(self.DEST_REQ, '1', 'auto')
        print("Python subscribed!")
        atexit.register(self.close)
        self.term = False

    def run_forever(self):
        while not self.term:
            time.sleep(5)

    # def send(self, content):
    #     print("Python sending...")
    #     self.conn.send(self.DEST_RESP, body=content)
    #     print("Python sent!")

    def close(self):
        self.conn.disconnect()
        print("Python disconnected")


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    amq = AMQConnection()
    amq.run_forever()