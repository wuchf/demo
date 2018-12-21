from uiautoTest import uiautoTest

error = []  # 保存用例步骤执行失败的用例名
fail = []  # 保存用例验证失败的用例名
success = []  # 保存用例执行成功的用例名（步骤执行成功，验证通过)
skip = []  # 保存没有被执行的用例（包含tm为0的用例和skipif中需要跳过的用例)

def run(func,case, res=[], check_res=[]):
    for step in case['steps']:
        _res = func.execute(step['action'], step['control'], step['value'])
        res.append(_res)
    if all(res):  # 如果都执行成功
        # if case['mq']:
        # send(reback_name, self.conf.get('mqip'), self.conf.get('name') + '_' + case['mq'] + 'ok')  # mq回馈执行结果
        if case['validate']:  # 有验证的信息
            for _validate in case['validate']:
                _check = func.validate(_validate['value1'], _validate['operation'], _validate['value2'],
                                          _validate['action'])
                check_res.append(_check)
        else:
            check_res.append(True)
            # success.append(case['name'])
    else:
        error.append(case['name'])
        # send(reback_name, self.conf.get('mqip'), self.conf.get('name') + '_' + case['mq'] + 'fail')

def test(func,case):
    res = []  # 保存步骤执行结果
    check_res = []  # 保存验证结果
    print(f'用例编号为==%s' % case['no'])
    if case['tm']:
        tm = int(case['tm'])
    else:
        tm = 1
    if tm == 0:  # 如果tm为0，就直接跳过不执行
        skip.append(case['name'])
    for i in range(tm):
        if not case['skipif']:  # 无执行用例的条件
            run(func,case, res, check_res)
        else:
            _skip_res = []
            for _skip in case['skipif']:
                # 对于执行用例条件，可以判断已经执行过的用例名称，一执行过的用例执行通过了或者失败了才会运行
                if _skip['operation'] in ['notin', 'ni']:
                    _res = _skip['value1'] not in success
                elif _skip['operation'] in ['in']:
                    _res = _skip['value1'] in success
                else:
                    _res = func.validate(_skip['value1'], _skip['operation'], _skip['value2'],
                                            _skip['action'])
                _skip_res.append(_res)
            print('skipif 执行后的结果为{}'.format(_skip_res))
            if all(_skip_res):  # 执行条件都成功了，才运行用例
                run(func,case, res, check_res)
            else:
                skip.append(case['name'])
    if not all(check_res):
        fail.append(case['name'])
    # 步骤都成功，验证都成功，且用例名不再skip中，用例执行成功
    if all(res) and all(check_res) and case['name'] not in skip:
        success.append(case['name'])

if __name__ == '__main__':
    case={
			"no":0,
			"name":"启动",
			"skipif":[],
			"steps":[
			{
				"action":"start",
				"control":"",
				"value":"\\TALLiveClient-Student\\bin\\TALLive.exe"
			}
			],
			"validate":[],
			"mq":"启动",
			"tm":""
		}
    fun = uiautoTest()
    test(fun,case)
