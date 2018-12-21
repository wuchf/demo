import psutil
import os,datetime,time

def getMemCpu():
    data=psutil.virtual_memory()
    total=data.total
    free=data.available
    # print(total)
    # print(free)
    disk=psutil.disk_usage('/')
    net=psutil.net_io_counters()
    mem="memory usage:%d"%(int(round(data.percent)))+"%" +"  "
    cpu="cpu:%0.2f"%psutil.cpu_percent(interval=1)+"%" + "  "
    disk_use="disk:%d"%(int(round(disk.percent)))+"%" +"  "
    net_use="net send:%d,net recv:%d"%(net.bytes_sent,net.bytes_recv)
    return mem+cpu+disk_use+ net_use
def run():
    while True:
        info=getMemCpu()
        time.sleep(0.2)
        print(info)

if __name__ == '__main__':
    run()