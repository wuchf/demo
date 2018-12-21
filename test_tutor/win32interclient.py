import win32file
import win32pipedemo
import pywintypes
import time
#命名管道为半双工，所以为了实现和client端通信，需要两个ipc通道
#命名管道默认是堵塞的，要想使用费堵塞式，使用FILE_FLAG_OVERLAPPED模式（没有找到该模式）

PIPE_NAME=r"\\.\pipe\ss-answer-tool-D27DFDD9-E25D-4976-A4D3-6179C2000B4C"
def pipe_client():
    print("pipe client")
    quit = False

    while not quit:
        try:
            handle = win32file.CreateFile(
                PIPE_NAME,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            res = win32pipedemo.SetNamedPipeHandleState(handle, win32pipedemo.PIPE_READMODE_MESSAGE, None, None)
            print (res)
            if res == 0:
                print(f"SetNamedPipeHandleState return code: {res}")
            while True:
                print ('recv')
                resp = win32file.ReadFile(handle, 64*1024)
                print(f"message: {resp}")
        except pywintypes.error as e:
            if e.args[0] == 2:
                print("no pipe, trying again in a sec")
                time.sleep(1)
            elif e.args[0] == 109:
                print("broken pipe, bye bye")
                quit = True

# def read2(self):
    #     try:
    #         overlapped = win32file.OVERLAPPED()
    #         overlapped.hEvent = win32event.CreateEvent(None, 1, 0, None)
    #         while True:
    #             try:
    #                 conn2=win32pipe.ConnectNamedPipe(self.local_pipe,None)
    #                 if conn2==0:
    #                     continue
    #                 rc,data2=win32file.ReadFile(self.local_pipe,PIPE_BUFFER_SIZE,overlapped)
    #                 if data2 is None or len(data2)<2:
    #                     # continue
    #                     break
    #                 print (len(data2))
    #                 print('receive local msg:',data2.tobytes())
    #                 # print (bytes(data2[1:100]))
    #                 # print (data2.tobytes())
    #                 # print(memoryview(data2))
    #                 if data2:
    #                     print('info')
    #                     win32file.WriteFile(self.named_pipe, data2.tobytes())
    #                 else:
    #                     print ('heart')
    #                     win32file.WriteFile(self.named_pipe, b'8|0|202')
    #                 # win32event.WaitForSingleObject(overlapped.hEvent, win32event.INFINITE)
    #             except BaseException as e:
    #                 print("read2 exception:", e)
    #                 break
    #     finally:
    #         print('haha')
    #         # try:
    #         #     print ("关闭local")
    #         #     win32pipe.DisconnectNamedPipe(self.local_pipe)
    #         # except:
    #         #     pass


class client():
    def __init__(self):
        self.file_handle = win32file.CreateFile(PIPE_NAME,
                                           win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                           win32file.FILE_SHARE_WRITE, None,
                                           win32file.OPEN_EXISTING, 0, None)

    def write(self,msg):
        try:
            print ('send msg:', msg)
            win32file.WriteFile(self.file_handle, str2bytes(msg))
            time.sleep(1)
        finally:
            pass
    def read(self):
        while True:
            try:
                data=win32file.ReadFile(self.file_handle,PIPE_BUFFER_SIZE,None)
                print('receive msg:', data)
            finally:
                pass

    def close(self):
        try:
            win32file.CloseHandle(self.file_handle)
        except:
            pass
def pipe_write(msg):
    print("pipe client")
    quit = False

    while not quit:
        try:
            handle = win32file.CreateFile(
                PIPE_NAME,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            res = win32pipedemo.SetNamedPipeHandleState(handle, win32pipedemo.PIPE_READMODE_MESSAGE, None, None)
            if res == 0:
                print(f"SetNamedPipeHandleState return code: {res}")
            print(f"writing message")
            win32file.WriteFile(handle, str2bytes(msg))
            time.sleep(1)
                # resp = win32file.WriteFile(handle, str2bytes(msg))
                # print(f"message: {resp}")
        except pywintypes.error as e:
            if e.args[0] == 2:
                print("no pipe, trying again in a sec")
                time.sleep(1)
            elif e.args[0] == 109:
                print("broken pipe, bye bye")
                quit = True


if __name__ == '__main__':
    pipe_client()



self.local_pipe = win32pipedemo.CreateNamedPipe(
            PIPE_LOCAL,
            win32pipedemo.PIPE_ACCESS_DUPLEX,
    win32pipedemo.PIPE_TYPE_MESSAGE | win32pipedemo.PIPE_READMODE_MESSAGE | win32pipedemo.PIPE_WAIT,
            win32pipedemo.PIPE_UNLIMITED_INSTANCES,
            # 1,
            PIPE_BUFFER_SIZE,
            PIPE_BUFFER_SIZE,
            600,
            None)



def read2(self):
    print("pipe server")
    try:
        while True:
            print("waiting for local client")
            win32pipedemo.ConnectNamedPipe(self.local_pipe, None)
            print("got local client")
            resp = win32file.ReadFile(self.local_pipe, PIPE_BUFFER_SIZE)
            print(f"message: {resp}")
            print(f'write {resp[1]}')
            _str = tobuff(2018, 2018, resp[1])
            win32file.WriteFile(self.named_pipe, _str + resp[1])
    except Exception as e:
        print('失败了，原因为{}'.format(e))
        traceback.print_exc()
        # win32pipe.ConnectNamedPipe(self.local_pipe, None)
    # finally:
    #     print('关闭local管道')
    #     win32file.CloseHandle(self.local_pipe)