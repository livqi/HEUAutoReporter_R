import requests,re,json,datetime,os
from lxml import etree
push_text=""
proxies={
        "http":None,
        "https":None
    }
stulist= {}
try:
    stu=os.environ['STULIST'].strip("#").split('#')
    SCKEY=os.environ['SCKEY']
except Exception as e:
    print(e)
    print("读取环境变量失败，宁是否正确设置了Secrets？")
    exit()
for a in range(len(stu)):
    try:
        stulist[a]={}
        stulist[a]['STUID']=stu[a].split(" ")[0]
        stulist[a]['PASSWORD']=stu[a].split(" ")[1]
    except Exception as e:
        print(e)
        print("分割账号密码失败，宁的Secrets格式确实不对")
        exit()
    try:
        xiegang="\\"
        requests.packages.urllib3.disable_warnings()
        headers={
            "Host": "cas-443.wvpn.hrbeu.edu.cn",
            "Connection": "keep-alive",
            "Origin": "https://cas-443.wvpn.hrbeu.edu.cn",
            "Upgrade-Insecure-Requests": "1",
            "Cookie":"",
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "https://cas-443.wvpn.hrbeu.edu.cn/cas/login",
        }
        body={
            "username":stulist[a]["STUID"],
            "password":stulist[a]["PASSWORD"],
            "_eventId":"submit",
        }
        req=requests.session()
        q=req.get("https://cas-443.wvpn.hrbeu.edu.cn/cas/login",proxies=proxies,verify=False)#请求登录
        headers["Cookie"]=q.headers["Set-Cookie"].split(";")[0]+";"+q.headers["Set-Cookie"].split("Path")[1].split(" ")[1]#添加Cookie：INGRESSCOOKIE+JSESSIONID
        #print("Cookie已更新为"+headers["Cookie"])
        tree=etree.HTML(q.text)#添加lt，logintype，execution
        lt=tree.xpath('/html/body/input[2]/@value')
        logintype=tree.xpath('//*[@id="login-type"]/@value')
        execution=tree.xpath('/html/body/input[5]/@value')
        body["lt"]=lt[0]
        body["source"]=logintype[0]
        body["execution"]=execution[0]
        print("==========开始登录第" + str(a + 1) + "个账号==========")
        q=req.post("https://cas-443.wvpn.hrbeu.edu.cn/cas/login",proxies=proxies,data=body,headers=headers,verify=False)

        headers["Cookie"]+=q.headers["Set-Cookie"].split(";")[9].split(" ")[1]+";"#添加Cookie：CASTGC
        p=req.get("https://wvpn.hrbeu.edu.cn/users/sign_in")#获取_webvpn_key和webvpn_username，_astraeus_session
        if re.search('(B|S|[0-9])(Z|[0-9])[0-9]{8}%', p.request.headers["Cookie"]):#这里匹配的学号是webvpn_username的
            print("已登录账号："+re.search('(B|S|[0-9])(Z|[0-9])[0-9]{8}(?=%)',p.request.headers["Cookie"]).group(0))
        else:
            print(stulist[a]["STUID"]+stulist[a]["PASSWORD"]+"登录失败")
            push_text+=stulist[a]["STUID"]+"登录失败，账号密码已经输出，请到Github Actions执行界面查看\n\n"
            break
        headers["Cookie"]+=p.request.headers["Cookie"]
        #print("Cookie已更新为"+headers["Cookie"])
        q=req.get("https://one.wvpn.hrbeu.edu.cn/infoplus/form/JCXBBJSP/start",proxies=proxies,verify=False)#开始创建流程
        csrfToken=etree.HTML(q.text).xpath("/html/head/meta[4]/@content")[0]
        body={"formData":"{\"_VAR_URL\":\"https://one.wvpn.hrbeu.edu.cn/infoplus/form/JCXBBJSP/start\",\"_VAR_URL_Attr\":\"{}\"}",
            "idc": "JCXBBJSP",
            "csrfToken":csrfToken,
            "release":"",
              }
        #创建新表单，获取创建的表单地址
        info=json.loads(req.post("https://one.wvpn.hrbeu.edu.cn/infoplus/interface/start",data=body,proxies=proxies,verify=False).text)
        if info['errno']==0:
            formAddress=info['entities'][0]
            print("创建表单成功，地址："+formAddress)
            #print(info)
        else:
            print("表单创建失败"+str(info))
            break
        formhtml=req.get(formAddress,proxies=proxies,verify=False).text#打开表单
        stedId=re.search("[0-9]{7};", formhtml).group(0)[:-1]

        body={
               "stepId":stedId,
               "csrfToken":csrfToken,
               "admin":"false",
        }
        req.get("https://one.wvpn.hrbeu.edu.cn/infoplus/alive",data=body,proxies=proxies,verify=False)#这个貌似没用，但是抓包时看到有这样一个请求了，也有不一样的返回值
        req.headers['Referer']=formAddress
        idontknowwhatsthis=json.loads(req.post("https://one.wvpn.hrbeu.edu.cn/infoplus/interface/render",data=body,proxies=proxies,verify=False).text)["entities"][0]["data"]
        #我也不知道这是啥东西，反正就是返回了好长一坨信息，还把我的自动缩进卡死了...不过这些信息下面正好可以用到。
        print(idontknowwhatsthis)
        fieldLYyc1=datetime.datetime.now().timestamp()#获取现在的时间
        fieldBBcxrqFrom=datetime.datetime.strptime(str(datetime.date.today()),"%Y-%m-%d").timestamp()#获取今天0点的时间
        fieldBBcxrqTo=fieldBBcxrqFrom
        fieldBBcxsjFrom=fieldLYyc1-fieldBBcxrqFrom+120#报备时间为当前时间+120秒
        fieldBBcxsjTo="79200"
        form={"_VAR_EXECUTE_INDEP_ORGANIZE_Name":str(idontknowwhatsthis["_VAR_EXECUTE_INDEP_ORGANIZE_Name"]),
               "_VAR_ACTION_ACCOUNT":str(idontknowwhatsthis["_VAR_ACTION_ACCOUNT"]),
               "_VAR_ACTION_INDEP_ORGANIZES_Codes":str(idontknowwhatsthis["_VAR_ACTION_INDEP_ORGANIZES_Codes"]),
               "_VAR_ACTION_REALNAME":str(idontknowwhatsthis["_VAR_ACTION_REALNAME"]),
               "_VAR_ACTION_INDEP_ORGANIZES_Names":str(idontknowwhatsthis["_VAR_ACTION_INDEP_ORGANIZES_Names"]),
               "_VAR_OWNER_ACCOUNT":str(idontknowwhatsthis["_VAR_OWNER_ACCOUNT"]),
               "_VAR_ACTION_ORGANIZES_Names":str(idontknowwhatsthis["_VAR_ACTION_ORGANIZES_Names"]),
               "_VAR_STEP_CODE":str(idontknowwhatsthis["_VAR_STEP_CODE"]),
              "_VAR_ACTION_ORGANIZE":str(idontknowwhatsthis["_VAR_ACTION_ORGANIZE"]),
               "_VAR_OWNER_USERCODES":str(idontknowwhatsthis["_VAR_OWNER_USERCODES"]),
               "_VAR_EXECUTE_ORGANIZE":str(idontknowwhatsthis["_VAR_EXECUTE_ORGANIZE"]),
               "_VAR_EXECUTE_ORGANIZES_Codes":str(idontknowwhatsthis["_VAR_EXECUTE_ORGANIZES_Codes"]),
               "_VAR_NOW_DAY":str(idontknowwhatsthis["_VAR_NOW_DAY"]),
               "_VAR_ACTION_INDEP_ORGANIZE":str(idontknowwhatsthis["_VAR_ACTION_INDEP_ORGANIZE"]),
               "_VAR_OWNER_REALNAME":str(idontknowwhatsthis["_VAR_OWNER_REALNAME"]),
               "_VAR_ACTION_INDEP_ORGANIZE_Name":str(idontknowwhatsthis["_VAR_ACTION_INDEP_ORGANIZE_Name"]),
               "_VAR_NOW":str(idontknowwhatsthis["_VAR_NOW"]),
               "_VAR_ACTION_ORGANIZE_Name":str(idontknowwhatsthis["_VAR_ACTION_ORGANIZE_Name"]),
               "_VAR_EXECUTE_ORGANIZES_Names":str(idontknowwhatsthis["_VAR_EXECUTE_ORGANIZES_Names"]),
               "_VAR_OWNER_ORGANIZES_Codes":str(idontknowwhatsthis["_VAR_OWNER_ORGANIZES_Codes"]),
               "_VAR_ADDR":str(idontknowwhatsthis["_VAR_ADDR"]),
               "_VAR_URL_Attr":str(idontknowwhatsthis["_VAR_URL_Attr"]),
               "_VAR_ENTRY_NUMBER":str(idontknowwhatsthis["_VAR_ENTRY_NUMBER"]),
               "_VAR_EXECUTE_INDEP_ORGANIZES_Names":str(idontknowwhatsthis["_VAR_EXECUTE_INDEP_ORGANIZES_Names"]),
               "_VAR_STEP_NUMBER":str(idontknowwhatsthis["_VAR_STEP_NUMBER"]),
               "_VAR_POSITIONS":str(idontknowwhatsthis["_VAR_POSITIONS"]),
               "_VAR_OWNER_ORGANIZES_Names":str(idontknowwhatsthis["_VAR_OWNER_ORGANIZES_Names"]),
               "_VAR_URL":str(idontknowwhatsthis["_VAR_URL"]),
               "_VAR_EXECUTE_ORGANIZE_Name":str(idontknowwhatsthis["_VAR_EXECUTE_ORGANIZE_Name"]),
               "_VAR_EXECUTE_INDEP_ORGANIZES_Codes":str(idontknowwhatsthis["_VAR_EXECUTE_INDEP_ORGANIZES_Codes"]),
               "_VAR_RELEASE":str(idontknowwhatsthis["_VAR_RELEASE"]),
               "_VAR_EXECUTE_POSITIONS":str(idontknowwhatsthis["_VAR_EXECUTE_POSITIONS"]),
               "_VAR_TODAY":str(idontknowwhatsthis["_VAR_TODAY"]),
               "_VAR_NOW_MONTH":str(idontknowwhatsthis["_VAR_NOW_MONTH"]),
               "_VAR_ACTION_USERCODES":str(idontknowwhatsthis["_VAR_ACTION_USERCODES"]),
               "_VAR_ACTION_ORGANIZES_Codes":str(idontknowwhatsthis["_VAR_ACTION_ORGANIZES_Codes"]),
               "_VAR_EXECUTE_INDEP_ORGANIZE":str(idontknowwhatsthis["_VAR_EXECUTE_INDEP_ORGANIZE"]),
               "_VAR_NOW_YEAR":str(idontknowwhatsthis["_VAR_NOW_YEAR"]),
               "groupZMCLList":[],
               "groupBGLList":[0],
               "groupGYLList":[0],
               "groupQTLList":[0],
               "groupZZLList":[0],
               "fieldJBsqr":stulist[a]["STUID"],
               "fieldJBsqr_Name":str(idontknowwhatsthis["_VAR_OWNER_REALNAME"]),#申请人
               "fieldJBszxy":"12000",
               "fieldJBszxy_Name":"软件学院",
               "fieldJBxh":stulist[a]["STUID"],
               "fieldJBlxfs":"17777777777",#申请人电话
               "fieldJBszgy":"十公寓",#所在公寓
               "fieldJBfdyxm":"0600010269",#导员账号
               "fieldJBfdyxm_Name":"王蕾",
               "fieldJBfdylxdh":"17777777777",#导员电话
               "fieldJBjcxlx":"1",#1是报备:-)2是审批
               "fieldBBh1":"1",#这是个啥？？？
               "fieldBByc1":"",
               "fieldBByc2":"",
               "fieldBByc3":"",
               "fieldLYyc1":str(fieldLYyc1),#当前时间
               "fieldBBcxsy":"玩",#出校目的
               "fieldBBsylb":"7",#出校原因1：因公出校  2：病假  3：事假  4：求职  5：实习  6：返家  7：其他
               "fieldBBycsj":"",
               "fieldBBcxrqFrom":str(fieldBBcxrqFrom).split(".")[0],#授权开始日期
               "fieldBBcxsjFrom":str(fieldBBcxsjFrom).split(".")[0],#授权开始时间（现在的时间戳-今天0点的）
               "fieldBBcxrqTo":str(fieldBBcxrqTo).split(".")[0],#授权结束时间戳
               "fieldBBcxsjTo":str(fieldBBcxsjTo).split(".")[0],#授权结束时间（结束的时间戳-今天0点的）
               "fieldBBsheng":"230000",#省邮编
               "fieldBBsheng_Name":"黑龙江省",
               "fieldBBshi":"230100",#市邮编
               "fieldBBshi_Name":"哈尔滨市",
               "fieldBBshi_Attr":"{"+xiegang+"_parent"+xiegang+":"+xiegang+"230000"+xiegang+"}",
               "fieldBBdiqu":"230103",#区邮编 Shit...为啥要分别提交三个邮编
               "fieldBBdiqu_Name":"南岗区",
               "fieldBBdiqu_Attr":"{"+xiegang+"_parent"+xiegang+":"+xiegang+"230000"+xiegang+"}",
               "fieldBBxxdz":"南通大街",#详细地址
               "fieldLYyc":"",
               "fieldJLly":"",
               "fieldLYbgl":"false",
               "fieldBGLmc":[""],
               "fieldBGLmc_Name":[""],
               "fieldBGLfjh":[""],
               "fieldLYbgyc":"",
               "fieldLYgyl":"false",
               "fieldGYLmc":[""],
               "fieldGYLmc_Name":[""],
               "fieldGYLfjh":[""],
               "fieldLYgyyc":"",
               "fieldLYqtl":[""],
               "fieldQTLmc":[""],
               "fieldQTLmc_Name":[""],
               "fieldQTLfjh":[""],
               "fieldLYqtyc":"",
               "fieldDel":"",
               "fieldLYzzl":"false",
               "fieldZZLmc":[""],
               "fieldZZLmc_Name":[""],
               "fieldZZLfjh":[""],
               "fieldLYzzyc":"",
               "fieldLYrqFrom":"",
               "fieldLYsjFrom":"",
               "fieldLYrqTo":"",
               "fieldLYsjTo":"",
               "fieldSPyc":"",
               "fieldFDYspyj":"",
               "fieldFDYspr":"",
               "fieldFDYsprq":"",
               "fieldFSJspyj":"",
               "fieldFSJspr":"",
               "fieldFSJspsj":"",
               "_VAR_URL_Name":formAddress,
               "_VAR_ENTRY_NAME":"__进出校报备及审批",
               "_VAR_ENTRY_TAGS":"null"
               }
        body["actionId"]=1
        body["formData"]=str(form).replace("'","\"")#提交时把字典中的单引号换成双引号
        body["boundFields"]: "fieldFDYsprq,fieldJBszgy,fieldBBshi,fieldLYqtl,fieldBBsheng,fieldLYqtyc,fieldLYzzl,fieldDel,fieldJBszxy,fieldFSJspsj,fieldLYrqFrom,fieldLYgyl,fieldGYLfjh,fieldFSJspr,fieldQTLmc,fieldLYbgl,fieldBBcxrqFrom,fieldJBjcxlx,fieldJLly,fieldLYzzyc,fieldBBsylb,fieldFDYspyj,fieldLYyc,fieldZMCLUrl,fieldBBcxsjFrom,fieldBBycsj,fieldBBdiqu,fieldJBsqr,fieldLYsjTo,fieldJBlxfs,fieldJBxh,fieldBBcxsy,fieldSPyc,fieldLYyc1,fieldZZLfjh,fieldBBcxsjTo,fieldBGLfjh,fieldFSJspyj,fieldLYrqTo,fieldBByc2,fieldBByc3,fieldQTLfjh,fieldBByc1,fieldJBfdyxm,fieldBBh1,fieldBBcxrqTo,fieldLYbgyc,fieldZZLmc,fieldLYgyyc,fieldLYsjFrom,fieldGYLmc,fieldBBxxdz,fieldJBfdylxdh,fieldBGLmc,fieldFDYspr"
        #print(body["formData"])
        results=req.post("https://one.wvpn.hrbeu.edu.cn/infoplus/interface/listNextStepsUsers",data=body,proxies=proxies,verify=False)#提交
        result=json.loads(results.text)
        print(result)
        if result["errno"]==0:
            #报备成功
            push_text+=stulist[a]["STUID"]+"报备成功，报备时间为"+datetime.datetime.fromtimestamp(fieldLYyc1+120).strftime("%Y-%m-%d %H:%M:%S")+\
                datetime.datetime.fromtimestamp(fieldBBcxrqFrom).strftime("%Y-%m-%d")+"22:00:00"+"表单地址："+formAddress+"\n\n"
            pass
        else :
            #报备失败
            push_text+=stulist[a]["STUID"]+"报备失败，返回结果为"+str(result)+"表单地址："+formAddress+"\n\n"
            pass
    except Exception as e:
        print(stulist[a]["STUID"]+"报备失败，程序可能出错了："+str(e))
        push_text+=stulist[a]["STUID"]+"报备失败，有可能是程序出错了："+str(e)+"\n\n"
        pass
if SCKEY != '':#server酱推送
    payload = {'title': "HEU自动报备_R", 'desp': push_text}
    requests.get("https://sctapi.ftqq.com/" + SCKEY + ".send", params=payload)
