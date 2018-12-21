import xlrd
from collections import defaultdict
import json
import os

def load_file(path):
    if not os.path.isfile(path):
        print( "{}文件不存在".format(path))
    file_end=os.path.splitext(path)[1].lower()
    if file_end=='.json':
        return load_json_file(path)
    elif file_end=='.xlsx':
        return load_excel_file(path)
    else:
        print('文件格式不支持，{}'.format(path))
def load_json_file(path):
    lines=[]
    with open(path,encoding='utf-8') as f:
        for line in f.readlines():
            lines.append(line)
    try:
        return json.loads('\n'.join(lines))
    except Exception as e:
        raise e
def load_excel_file(path):
    workbook = xlrd.open_workbook(path)
    config_sheet = workbook.sheet_by_index(0)
    testcases_sheet = workbook.sheet_by_index(1)
    data={}
    _config = {}
    for i in range(config_sheet.nrows):

        conf=config_sheet.row_values(i)
        _config[conf[0]]=conf[1]
    data['config']=_config
    testcases = []
    header=testcases_sheet.row_values(0)

    for i in range(1,testcases_sheet.nrows):
        testcase={}
        row=testcases_sheet.row_values(i)
        testcase[header[0]] = int(row[0])
        testcase[header[1]] = row[1]
        testcase[header[2]] = row[2]
        testcase[header[3]] = row[3]
        testcase[header[4]] = row[4]
        # if isinstance(row[4],str):
        #     testcase[header[4]] = row[4]
        # else:
        #     testcase[header[4]] = int(row[4])
        testcase[header[5]] = row[5]
        testcase[header[6]] = row[6]
        testcase[header[7]] = row[7]
        testcases.append(testcase)
    data['cases']=testcases
    print (data)
    return data

def getResult_2(values):
    res = []
    names = set([values[i]['name'] for i in range(0, len(values))])
    print (names)
    for name in names:
        tmp = defaultdict(list)
        for i in range(0, len(values)):
            # 获取相同的IP所在的字典
            if name == values[i]['name']:
                tmp[name].append(values[i])  # 更新字典
        res.append(tmp)
    print(res)
    return res
def getResult_1(values):
    res = []
    names = set([ values[i]['name'] for i in range(0,len(values))])
    for name in names:
        tmp = []
        for i in range(0,len(values)):
            #获取相同的IP所在的字典
            if name == values[i]['name']:
                tmp.append(values[i]) #追加列表
        res.append(tmp)
    # print (res)
    return res

if __name__ == '__main__':
    # load_excel_file("D:\\UIauto\\testdemo.xlsx")
    jj=load_json_file("d:\\UIauto\\test.json")
    print (jj)
    # aa=[{'name': '选择学科', 'step': {'action': 'click', 'control': 'button,,理  科,5,', 'value': ''}}, {'name': '登录', 'step': {'action': 'sendkey', 'control': '"edit","","",8,1', 'value': 'testf0055'}}, {'name': '登录', 'step': {'action': 'sendkey', 'control': '"edit","","",7,1', 'value': '1234567a'}}, {'name': '登录', 'step': {'action': 'select', 'control': '"combobox","","",7,2', 'value': '广州'}}, {'name': '登录', 'step': {'action': 'click', 'control': '"button","","登录",6,2', 'value': 'testf0058'}}]
    # # print ([ k : x.get(k)  for k in x.keys for x in aa])
    # getResult_1(aa)