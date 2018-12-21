from ftplib import FTP
import win32api

def ftpConn(host,username,password):
    ftp=FTP()
    ftp.connect(host)
    ftp.login(username,password)
    return ftp

def downloadfile(ftp, remotepath,remotefile, localfile):
    bufsize = 1024
    ftp.cwd(remotepath)
    fp = open(localfile, 'wb') # 以写的模式在本地打开文件
    ftp.retrbinary('RETR'+remotefile, fp.write, bufsize)# 接收服务器上文件并写入本地文件

    # ftp.set_debuglevel(0) # 关闭调试模式
    fp.close()

def uploadfile(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR'+remotepath, fp, bufsize)
    # ftp.set_debuglevel(0)
    fp.close()



