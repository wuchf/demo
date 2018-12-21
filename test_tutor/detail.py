import sys

HTML_TMP = '''
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.bootcss.com/jquery/2.1.1/jquery.min.js"></script>
    <script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <script src="http://cdn.hcharts.cn/highcharts/highcharts.js"></script>
    <style type="text/css">
        #chart{
            width: 550px;
            height: 500px;
            margin: 0;
        }
        .fail{
            color: red;
            font-weight:bold
            }
        .pass{
            color: green;
            font-weight:bold
            }
        .skip{
            color: yellow;
            font-weight:bold
            }
        td{
            {#max-width: 80px;#}
            word-wrap: break-word;
            table-layout:fixed;
            word-break:break-all;
        }
    </style>
    <title>%(title)s</title>
</head>
<body>
%(script)s
%(body)s
</body>
'''
HTML_SCRIPT = '''
<script language="JavaScript">
    $(document).ready(function() {  
   var chart = {
       plotBackgroundColor: null,
       plotBorderWidth: null,
       plotShadow: false
   };
   var title = {
      text: '测试结果比例'   
   };      
   var tooltip = {
      pointFormat: '{series.name}：{point.percentage:.2f}%%'
   };
   var plotOptions = {
      pie: {
         allowPointSelect: true,
         cursor: 'pointer',
         dataLabels: {
            enabled: true,
            format: '<b>{point.name}</b>: {point.percentage:.2f}%%',
            style: {
               color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
            }
         }
      }
   };
   var series= [{
      type: 'pie',
      name: '比例',
      data: [
       ['error',    %(fail)d],
         {
            name: 'pass',
            y: %(success)d,
            sliced: true,
            selected: true
         },
      ]
   }];     

   var json = {};   
   json.chart = chart; 
   json.title = title;     
   json.tooltip = tooltip;  
   json.series = series;
   json.plotOptions = plotOptions;
   $('#chart').highcharts(json);  
});
function detail(name) {
    $.ajax({
        url: "detail.html",
        global: false,
        type: "get",
        data: ({
          id: name
        }),
        dataType: "html",
        async: false,
        success: function(msg) {
          alert(msg);
        }
      })
    }
</script>

'''
HTML_BODY = '''
<div class="container" >
    <p><strong>%(title)s</strong></p>
    <p> 总计运行时间：%(time)s</p>
    <p> 运行用例数：%(total)s</p>
    <p> 学生作答数：%(ans)s</p>
    <div id='all'>
        <table class="table table-striped table-bordered table-hover" width="100">
            <caption>概要信息</caption>
                <th >用例名</th>
                <th >运行平台</th>
                <th >作答次数</th>
                <th >pass</th>
                <th >fail</th>
                <th >skip</th>
                %(tr)s
        </table>
    </div>

    <div id='detail' style="display: none">

    </div>

    <div id="chart"></div>
    </div>
'''
DETAIL_BODY = '''
    <div>
        <h4>功能%(case)s的详情</h4>
        <p>在端%(platform)s执行情况</p>
        %(info)s  
    </div>
'''

DETAIL_INFO = '''
    <div>
        失败信息 
    </div>
'''

TABLE_INFO = '''
    <tr>
        <td width="10%%" rowspan="%(n)s"><a onclick=detail(%(case)s)>%(case)s</a></td>
        <td width="10%%">%(platform)s</td>
        <td width="10%%">%(num)s</td>
        <td width="10%%"class="pass">%(pass)s</td>
        <td width="10%%"class="fail">%(fail)s</td>
        <td width="10%%"class="skip">%(skip)s</td>
    </tr>
'''


class result():
    DEFAULT_TITLE = '测试报告'

    # teacher = None, tutor = None, student = None, tea_pc = None,
    def __init__(self, time, stream=sys.stdout, title=None, **kwargs):
        self.stream = stream
        if title:
            self.title = title
        else:
            self.title = self.DEFAULT_TITLE
        self.time = time
        self.results = kwargs

    def _generate_data(self):
        # 所有信息
        '''
        teacherpc={"login":{"login":"pass"},"zuoti":{"title":"pass","pre-finish":"pass","pre-answer1":"fail","finish":"fail","answer1":"skip"}}
        :return:
        '''
        rows = []

        for plat, res in self.results.items():
            info = {}
            info["num"] = 2
            info["n"] = 1
            info['platform'] = plat
            for k, v in res.items():
                info["case"] = k
                info["pass"] = len([x for x in v.values() if x == "pass"])
                info["fail"] = len([x for x in v.values() if x == "fail"])
                info["skip"] = len([x for x in v.values() if x == "skip"])
                row = TABLE_INFO % info
                rows.append(row)

        body = HTML_BODY % dict(
            tr=''.join(rows),
            title=self.title,
            time=self.time,
            total=len(self.results),
            ans=1,
        )
        return body

    def chart(self):
        chart = HTML_SCRIPT % dict(
            fail=1 / 10 * 100,
            success=2 / 10 * 100,
        )
        return chart

    def generatereport(self):
        output = HTML_TMP % dict(
            title=self.title,
            body=self._generate_data(),
            script=self.chart()
        )
        self.stream.write(output.encode('utf-8'))
        self.stream.flush()

    def generaterdetail(self, name):
        print(name)
        a = {}
        for plat, res in self.results.items():
            for k, v in res.items():
                if k == name:
                    a[plat] = v
        print(a)


if __name__ == '__main__':
    fp = open("result.html", 'wb')
    time = '0.12'
    # results=[{'name': 'login', 'seqid': 1, 'expect': "'status','200'", 'result': 'fail', 'response': '{"avatar":null,"businessId":"40288b155f4d4c0c015f4d9a2eef00d1","userType":"2","loginName":"xiangjiaopi","token":"fab340e5229f4dc48e95ea583abd18cd","point":0,"areaCode":"020","areaName":"广州","liveNum":null,"classId":null,"classNum":null,"yunXinId":"40288b155f4d4c0c015f4d9a2eef00d1","yunXinToken":"9c0d6e6ec1ba4921a9677813000e7e03","stuNum":0}'}, {'name': 'login', 'seqid': 2, 'expect': '1000', 'result': 'pass', 'response': '{"message":"用户名或密码错误","status":"error"}'}]
    teacherpc = {"login": {"login": "pass"},
                 "zuoti": {"title": "pass", "pre-finish": "pass", "pre-answer1": "fail", "finish": "fail",
                           "answer1": "skip"}}
    studentpc = {"login": {"login": "pass"},
                 "zuoti": {"title": "pass", "tip": "pass", "pre_progress": "fail", "progress": "skip"}}
    teacher = {"login": {"login": "pass"}, "zuoti": {"open": "pass", "finish": "fail"}}
    tutor = {"login": {"login": "pass"}}
    res = result(time, fp, title="测试结果", teacher=teacher, teacherpc=teacherpc, tutor=tutor)
    # result()
    res.generatereport()
    # print (res.chart())
