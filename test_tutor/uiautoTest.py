from uiautoUtil import wintest
from loadUtil import load_file

class uiautoTest():
    def __init__(self):
        self.win=wintest()

    def setconfig(self,filename,imgpath,saveimg):
        self.win.setcong(filename, imgpath,saveimg)
        # self.win.start(app)

    def execute(self,action,control,value):
        if action=='start':
            res=self.win.start(value)
        elif action=='click':
            res =self.win.click_act(control)
        elif action=='dbclick':
            res =self.win.dbclick_act(control)
        elif action=='eclick':
            res=self.win.existclick(control)
        elif action=='sendkey':
            res =self.win.sendkey(value,control)
        elif action=='select':
            res =self.win.select_act(value,control)
        elif action=='waitchange':
            if ','in value:
                _val=value.split(',')
                type=_val[0]
                info=_val[1]
            else:
                type = value
                info = ""
            res =self.win.waitchange(type,control,info)
        elif action=='capture':
            res =self.win.captureimg(value)
        elif action=='clickpic':
            res=self.win.click_pic(value)
        elif action=='picexist':
            res=self.win.assert_pic_exist(value)
        elif action=='sleep':
            res=self.win.sleeptm(value)
        elif action=='kill':
            res=self.win.killapp()
        else:
            print(f"执行失败，输入的action错误，错误的action为=={action}")
            res=False
        return res
    def validate(self,value1,operation,value2,action):
        if action=='picexist':
            res = self.win.assert_pic_exist(value1)
        elif action=='notpicexist':
            res = self.win.assert_pic_not_exist(value1)
        else:
            res="action 信息不正确"
        return res



if __name__ == '__main__':
    datas = load_file("D:\\UIauto\\testdemo.xlsx")
    config = datas.get('config')
    cases = datas.get("cases")

    auto = uiautoTest()
    auto.setconfig(config.get('logfile'), config.get('imgpath'), config.get('appname'))




