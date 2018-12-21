import stomp

# topic_name='/topic/interTopic' #互动的topic
# answer_name='/topic/answerTopic'#答题器的topic
# listener_name='sampleListener'

def send_inter_topic(topic_name,ip,msg):
    conn=stomp.Connection([(ip, 61613)])
    conn.start()
    conn.connect()
    print("mq发送的信息为 ==%s"%msg)
    try:
        conn.send(destination=topic_name,body=msg)
    except Exception as e:
        print ("mq发送信息失败，失败原因为：%s"%e)
    conn.disconnect()
if __name__ == '__main__':
    # send_to_queue('hahaha')
    # receive_from_queue()
    # receive_from_queue2()

    # receive_from_topic()
    # send_inter_topic('结束是非')
    topic_name = '/topic/interTopic'  # 互动的topic
    ip="10.2.34.18"
    send_inter_topic(topic_name,ip,'stop')
    # send_inter_topic('stop')
    # receive_from_topic2()
    # send_answer_topic("0")

