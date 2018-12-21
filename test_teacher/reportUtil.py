import sys
import os

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
        .content{
            padding:100px;
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
      text: '测试统计数据'   
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
       ['fail',    %(fail)d],
       ['skip',    %(skip)d],
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
   
   $('#all').find('table').find('tr').on('click', function(e){
        e.preventDefault();
        $(this).next('tr.content').toggle()
    }); 
});

</script>

'''
HTML_BODY = '''
<div class="container" >
<h2>UI自动化测试报告</h2>
    <div class="col-md-12">
        <div class="col-md-3">
            <h3>测试概要信息</h3>
            <p> 总计运行时间：%(time)s</p>
            <p> 运行用例集数：%(total)s</p>
            <p> 学生作答数：%(ans)s</p>
            <p> 用例成功数：%(success)s</p>
            <p> 用例失败数：%(fail)s</p>
            <p> 未验证：%(skip)s</p>
        </div>
        <div class="col-md-9">
            <div id="chart" style="width: 550px; height: 300px; margin: 0 auto"></div>
        </div>
    </div>
    <div id='all'>
    <h3>详细信息</h3>
        <table class="table table-striped table-bordered table-hover" width="100">
                <th >用例集</th>
                <th >作答次数</th>
                <th >pass</th>
                <th >fail</th>
                <th >skip</th>
                %(tr)s
        </table>
    </div>
    </div>
'''

TABLE_INFO = '''
    <tr class="active">
        <td width="10%%">%(case)s</td>
        <td width="10%%">%(num)s</td>
        <td width="10%%"class="pass">%(pass)s</td>
        <td width="10%%"class="fail">%(fail)s</td>
        <td width="10%%"class="skip">%(skip)s</td>
    </tr>
    <tr class='content' style="display: none"><td colspan="5">%(detail)s</td></tr>
'''

DETAIL_INFO='''
    <table class="table table-striped table-bordered" width="100">
        <caption>平台端%(platform)s的结果</caption>
        <tr>
            <td class="success">验证成功：</td><td class="success">%(success)s</td>
            <td class="danger">验证失败：</td><td class="danger">%(fail)s</td>
            <td class="warning">未验证：</td><td class="warning">%(skip)s</td>
        </tr>
        %(img)s
    </table>

'''
IMG_INFO='''
    <tr>
        <td>
            <img  name="pic" src="%s" height="200" width="200"/>
        </td>
    </tr>
'''

class result():
    DEFAULT_TITLE = '测试报告'
    # teacher = None, tutor = None, student = None, tea_pc = None,
    def __init__(self,cases,answer,time, stream=sys.stdout, title=None,**kwargs):
        self.stream = stream
        if title:
            self.title = title
        else:
            self.title = self.DEFAULT_TITLE
        self.cases=cases
        self.answers=answer
        self.time = time
        self.results=kwargs
        self.success=0
        self.fail=0
        self.skip=0
        self.ans=0

    def detail(self,name):
        details=[]
        for plat, res in self.results.items():
            info = {}
            for k, v in res.items():
                if k == name:
                    info["platform"] = plat
                    info["success"] = len([x for x in v.values() if x == "pass"])
                    info["fail"] = len([x for x in v.values() if x == "fail"])
                    info["skip"] = len([x for x in v.values() if x == "skip"])
            if info:
                if info["fail"]!=0:
                    path="D:\\work\\result\\%s"%plat
                    imgs=[]
                    for i in {x:y for x,y in v.items() if y == "fail"}:
                        f_list = os.listdir(path)
                        for l in f_list:
                            if l.startswith(name+"-"+i):
                                img=IMG_INFO%(path+"\\"+l)
                        imgs.append(img)
                    info["img"]="".join(imgs)
                else:
                    info["img"]=""
                detail=DETAIL_INFO%info
                details.append(detail)
        return details

    def _generate_data(self):
        # 所有信息
        rows = []
        for i in self.cases:
            info={"case":"","pass":0,"fail":0,"skip":0}
            info["num"]=self.answers[i]
            info["detail"]=''.join(self.detail(i))
            for plat, res in self.results.items():
                for k, v in res.items():
                    if k==i:
                        info["case"]=k
                        info["pass"] += len([x for x in v.values() if x == "pass"])
                        info["fail"] += len([x for x in v.values() if x == "fail"])
                        info["skip"] += len([x for x in v.values() if x == "skip"])
            self.success += info["pass"]
            self.fail += info["fail"]
            self.skip += info["skip"]
            self.ans+=info["num"]
            row = TABLE_INFO % info
            rows.append(row)

        body = HTML_BODY % dict(
            tr=''.join(rows),
            # title=self.title,
            time=self.time,
            total=len(self.cases),
            success=self.success,
            fail=self.fail,
            skip=self.skip,
            ans=self.ans,
        )
        return body


    def chart(self):
        total=self.skip+self.fail+self.success
        chart = HTML_SCRIPT % dict(
            fail=self.fail/ total * 100,
            success=self.success / total * 100,
            skip=self.skip / total * 100,
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

    def generaterdetail(self,name):
        print (name)
        a={}
        for plat,res in self.results.items():
            for k,v in res.items():
                if k==name:
                    a[plat]=v
        print (a)

    def getfile(self,path,pre):
        f_list = os.listdir(path)
        for l in f_list:
            if l.startswith(pre):
                print (l)





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
    case=["login","zuoti"]
    answer={"login":0,"zuoti":10}
    res = result(case,answer,time,fp,title="UI自动化测试报告",teacher=teacher,teacherpc=teacherpc,tutor=tutor)
    # result()
    res.generatereport()
    # print (res.chart())
    # res.generaterdetail("zuoti")


