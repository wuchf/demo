from pywinauto import application
from airtest.core.api import *
from uiautomation import *
import os
import time
import logging

class wintest():

    def setcong(self,logfile="",imgpath="",saveimg=""):
        Logger.SetLogFile(logfile)
        imgpath=imgpath.strip().rstrip("\\")
        if imgpath:
            if os.path.exists(imgpath):
                pass
            else:
                os.makedirs(imgpath)
        self.imgpath=imgpath
        saveimg = saveimg.strip().rstrip("\\")
        if saveimg:
            if os.path.exists(saveimg):
                pass
            else:
                os.makedirs(saveimg)
        self.saveimg = saveimg

    def start(self,tool_name):
        try:
            self.app = application.Application()
            app=os.path.join(os.getenv("APPDATA"),tool_name.lstrip("\\"))
            self.app.start(app)
            self.window = PaneControl(ClassName='Qt5QWindowIcon')
            # self.window = PaneControl(kwargs)
            self.handle=self.window.Handle
            logging.error ("windows 的handle为{}".format(self.handle))
            self.window.SetFocus()
            # 可以判断window是否存在，如果不判断，找不到window的话会抛出异常
            if WaitForExist(self.window, 3):
                Logger.Log("项目-{}-已打开".format(tool_name.split('\\')[-1]))
                self.app.connect(handle=self.handle)
                self.app.window_(handle=self.handle)
                self.app.top_window()
                return True
            else:
                logging.error("项目-{}-在3s之内未打开".format(tool_name.split('\\')[-1]))
                # sys.exit(0)
                return False
        except Exception as e:
            logging.error ('启动失败，原因为：%s'%e)
            return False

    def findcontrol(self,kwargs):
        """
        获取控件
        :param kwargs: 控件定位信息
        :return:  控件
        """
        con_type=""
        className=""
        name=""
        depth=0xFFFFFFFF
        index=1
        # logging.error(kwargs)
        for _ele in kwargs.split(','):
            _e=_ele.split('=')
            # logging.error (_e)
            if _e[0].lower() in ['con','control']:
                con_type=_e[1]
            elif _e[0].lower()in['clsname','classname','class']:
                className=_e[1]
            elif _e[0].lower()in['name','n']:
                name=_e[1]
            elif _e[0].lower()in['dep','depth']:
                depth=int(_e[1])
            elif _e[0].lower()in['index','in']:
                index=int(_e[1])
            else:
                logging.error('元素定位信息错误，错误信息为=={},不在【control,class,name,depth,index】中'.format(_e[0]))
        try:
            if con_type=='button':
                return self.window.ButtonControl(ClassName=className, SubName=name, searchDepth=depth, foundIndex=index)
            elif con_type=='edit':
                return self.window.EditControl(ClassName=className, SubName=name, searchDepth=depth, foundIndex=index)
            elif con_type=='text':
                return self.window.TextControl(ClassName=className, SubName=name, searchDepth=depth, foundIndex=index)
            elif con_type=='combobox':
                return self.window.ComboBoxControl(ClassName=className, SubName=name, searchDepth=depth, foundIndex=index)
            elif con_type=="":
                return self.window.ButtonControl(ClassName=className, SubName=name, searchDepth=depth, foundIndex=index)
            elif con_type=='pane':
                return PaneControl(ClassName=className, SubName=name, searchDepth=depth, foundIndex=index)
        except Exception as e:
            msg="查找信息失败，失败原因为=={}".format(e)
            logging.error (msg)
            return msg

    def click_act(self,kwargs):
        """
        单击控件
        :param con:  单击的控件
        :return: None
        """
        try:
            self.findcontrol(kwargs).Click()
            return True
        except Exception as e:
            msg=f"执行click操作失败，失败原因为=={e}"
            logging.error (msg)
            return msg

    def existclick(self,kwargs):
        try:
            con=self.findcontrol(kwargs)
            if not isinstance(con,str):
                con.Click()
            return True
        except Exception as e:
            msg=f"执行existclick操作失败，失败原因为=={e}"
            logging.error(msg)
            return msg

    def dbclick_act(self,kwargs):
        """
        双击控件
        :param con: 双击的控件
        :return: None
        """
        try:
            self.findcontrol(kwargs).DoubleClick()
            return True
        except Exception as e:
            msg=f"执行dbclick操作失败，失败原因为=={e}"
            logging.error(msg)
            return msg

    def sendkey(self,value,kwargs):
        """
        输入值
        :param con: 输入的控件
        :param value: 输入的值
        :return: None
        """
        try:
            element=self.findcontrol(kwargs)
            element.Click()
            self.clear(kwargs)
            element.SendKeys(value)
            return True
        except Exception as e:
            msg=f"执行sendkey操作失败，失败原因为=={e}"
            logging.error(msg)
            return msg

    def clear(self,kwargs):
        """
        清空输入框中的信息
        :param kwargs:
        :return:
        """
        val=self.getvalue("value",kwargs)
        if val:
            for i in range(len(val)):
                key='{BACK}'
                Win32API.SendKeys(key)


    def getvalue(self,type,kwargs):
        """
        返回当前控件的属性
        :param con: 选中的控件
        :param type:要返回的属性值
        :return:
        """
        try:
            element=self.findcontrol(kwargs)
            element.Click()
            if type=="name":
                return element.Name
            if type=="value":
                return element.CurrentValue()
        except Exception as e:
            msg=f"执行getvalue操作失败，失败原因为=={e}"
            logging.error(msg)
            return msg


    def select_act(self,value,kwargs):
        """
        在下拉列表中选择指定值
        :param con: 控件
        :return: None
        """
        try:
            if isinstance(value,int):
                value=str(value)
            # self.click_act(con)
            element=self.findcontrol(kwargs)
            while True:
                _val = element.CurrentValue()
                # logging.error(_val)
                # logging.error(_val == value)
                if _val == value:
                    break
                else:
                    element.Select(name=value, waitTime=3)
            return True
        except Exception as e:
            msg=f"执行select操作失败，失败原因为=={e}"
            logging.error(msg)
            return msg

    # def listdown(self,con,value):
    #     self.click_act(con)
    #     self.click_act(con)
    #     # live_city.Click()
    #     tmp = self.getvalue(con,'value')
    #     key = '{Down}'
    #     while self.getvalue(con,'value') != value:
    #         Win32API.SendKeys(key)
    #         if tmp == self.getvalue(con,'value'):
    #             if key == '{Down}':
    #                 key = '{Up}'
    #             else:
    #                 raise Exception('下拉框控件{}未找到{}'.format(con,value))

    def captureimg(self,name):
        """
        截取图片
        :param name: 图片名称，不需要后缀
        :return:none
        """
        try:
            logging.error(self.saveimg+"//"+name+".png")
            self.window.CaptureToImage(self.saveimg+"//"+name+".png")
            return True
        except Exception as e:
            msg=f"执行getvalue操作失败，失败原因为=={e}"
            logging.error(msg)
            return msg

    def waitexist(self,control,timeout,capture=False,exit=False):
        """
        等待控件出现
        :param control: 控件名称
        :param timeout: 等待时间，单位为秒
        :param capture: 如果控件在指定时间中未出现，是否截图，默认为false
        :param exit: 如果控件在指定时间中未出现，是否退出程序，默认为false
        :return:
        """
        if WaitForExist(control, timeout):
            logging.ingo("控件-{}-在{}s中已存在".format(control,timeout))
            return True
        else:
            logging.ingo("控件-{}-在{}s中未存在".format(control,timeout), ConsoleColor.Yellow)
            # sys.exit(0)
            if capture:
                self.captureimg(control)
            if exit:
                sys.exit(0)
            return False
    def waitdisappear(self,control, timeout,capture=False,exit=False):
        """
        等待控件消失
        :param control: 控件名称
        :param timeout: 等待时间，单位为秒
        :param capture: 如果控件在指定时间中未消失，是否截图，默认为false
        :param exit: 如果控件在指定时间中未消失，是否退出程序，默认为false
        :return:
        """
        if WaitForDisappear(control, timeout):
            logging.ingo("控件-{}-在{}s中已消失".format(control,timeout))
        else:
            logging.ingo("控件-{}-在{}s中未消失".format(control,timeout), ConsoleColor.Yellow)
            # sys.exit(0)
            if capture:
                self.captureimg(control)
            if exit:
                sys.exit(0)
    def waitchange(self,type,kwargs,value=""):
        """
        等待控件信息改变
        :param con: 控件信息
        :param type: 检测的属性，如name或者value等
        :param value: 改变后的值，默认不指定具体的取值
        :return: None
        """
        #todo 再看一下，感觉函数写的不对
        try:
            #改变之前的值
            _bval=self.getvalue(type,kwargs)
            # if not value:
            #     if value in _bval:
            #         return
            #     else:

            while True:
                #改变之后的值
                _fval=self.getvalue(type,kwargs)
                if _bval!=_fval:
                    if value=="":
                        return True
                    else:
                        if _fval==value:
                            return True
                else:
                    time.sleep(1)
        except Exception as e:
            msg=f"执行waitchange操作失败，失败原因为=={e}"
            logging.error(msg)
            return msg
    def sleeptm(self,value):
        time.sleep(int(value))
        return True

    def killapp(self):
        self.app.kill()
        return True

    def click_pic(self,png):
        """
        单机图片，使用airtest框架
        :param png:
        :return:
        """
        try:
            connect_device('windows:///')
            touch(Template(self.imgpath+"//"+png))
            return True
        except Exception as e:
            msg=f"执行click_pic操作失败，失败原因为=={e}"
            logging.error(msg)
            return msg

    def assert_pic_exist(self,png):
        '''
        检测图片是否存在，使用airtest框架
        :param png:
        :return:
        '''
        try:
            connect_device('windows:///')
            assert_exists(Template(self.imgpath+"//"+png))
            snapshot(self.saveimg + '//' + png)
            return True
        except Exception as e:
            msg=f"执行assert_pic_exist操作失败，失败原因为=={e}"
            logging.error(msg)
            return msg

    def assert_pic_not_exist(self,png):
        '''
        检测图片是否存在，使用airtest框架
        :param png:
        :return:
        '''
        try:
            connect_device('windows:///')
            assert_not_exists(Template(self.imgpath+"//"+png))
            return True
        except Exception as e:
            msg=f"执行assert_pic_not_exist操作失败，失败原因为=={e}"
            logging.error(msg)
            return msg

if __name__ == '__main__':
    # pass
    filename="e:\winlog.txt"
    imgpath="e:\img"
    app=r'\TALLiveClient-Student\bin\TALLive.exe'
    win=wintest()
    win.setcong(filename,imgpath)
    win.start(app)
    # like=win.button_con(name="理  科",depth=5)
    # win.click_act(like)
    # name=win.edit_con(depth=8,index=1)
    # win.sendkey(name,"testf0055")
    # pwd=win.edit_con(depth=7,index=1)
    # win.sendkey(pwd,"1234567a")
    # area=win.combobox_con(depth=7,index=2)
    # # val=win.getvalue(area)
    # # logging.error (val)
    # win.select_act(area,"北京")
    # log_btn=win.button_con(name="登录",depth=6,index=2)
    # win.click_act(log_btn)
    # win.captureimg("login")

    #选择直播间-老师

