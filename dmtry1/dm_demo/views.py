from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from dm_demo.models import AdminTab
from dm_demo.models import AchievementTab
from dm_demo.models import Department
from dm_demo.models import AchievementAuthenTab
from dm_demo.models import ScholarTab
from dm_demo.models import ScholarAchievementTab
from dm_demo.models import SchAchAuthenTab
from dm_demo.models import ReportTab
from dm_demo.models import user_tab, student_tab
from dm_demo.models import authen_tab,user_authen_tab
from dm_demo.models import add_achievement_tab, new_achievement_tab, new_relation_tab
from dm_demo.models import collect_achievement_tab, collect_scholar_tab


from django.shortcuts import redirect
from django.contrib import messages
from django.core.mail import send_mail
import datetime

from collections import defaultdict
import csv
import json
relation_all_file = 'data/relation_all.csv'

"""
 django.http模块中定义了HttpResponse 对象的API
 作用：不需要调用模板直接返回数据
 HttpResponse属性：
    content: 返回内容,字符串类型
    charset: 响应的编码字符集
    status_code: HTTP响应的状态码
"""

"""
hello 为一个视图函数，每个视图函数必须第一个参数为request。哪怕用不到request。
request是django.http.HttpRequest的一个实例
"""

admin_id = ''
dep_info = ''
ach_info = ''
newach_auth = ''
sch_ach_auth = ''
user_counter = [[0, 0, 0] for i in range(12)]
user_sub = [[0, 0, 0] for i in range(12)]
# if datetime.datetime.now().month == 5:
#     print("yes")
ach_all = [-1]*7
ach_counter = [0]*12
ach_sub = [0]*12


def hello(request):
    return HttpResponse('Hello World')


def msg(request, name, age):
    return HttpResponse('My name is ' + name + ', i am ' + age + 'years old cl is my dad')


def homepage(request):
    # id = admin_id
    global user_counter
    global ach_all
    global user_sub
    global ach_counter
    global ach_sub
    month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    last0 = 0
    last1 = 0
    last2 = 0
    last_ach = 0
    if month == 1:
        last0 = user_counter[11][0]
        last1 = user_counter[11][1]
        last2 = user_counter[11][2]
        last_ach = ach_counter[11]
        user_counter = [[0, 0, 0] for i in range(12)]
        ach_all[0] = ach_all[2]
        ach_all[1] = ach_all[4]
        ach_all[2] = ach_all[6]
    else:
        last0 = user_counter[month-2][0]
        last1 = user_counter[month-2][1]
        last2 = user_counter[month-2][2]
        last_ach = ach_counter[month-2]
    user_counter[month-1][0] = user_tab.objects.count()
    user_counter[month-1][1] = ScholarTab.objects.count()
    user_counter[month-1][2] = student_tab.objects.count()
    ach_counter[month-1] = AchievementTab.objects.count()
    user_sub[month-1][0] = user_counter[month-1][0] - last0
    user_sub[month-1][1] = user_counter[month-1][1] - last1
    user_sub[month-1][2] = user_counter[month-1][2] - last2
    ach_all[3] = max(ach_counter[0], ach_counter[1], ach_counter[2])
    ach_all[4] = max(ach_counter[3], ach_counter[4], ach_counter[5])
    ach_all[5] = max(ach_counter[6], ach_counter[7], ach_counter[8])
    ach_all[6] = max(ach_counter[9], ach_counter[10], ach_counter[11])
    ach_sub[month-1] = ach_counter[month-1] - last_ach
    dict = {'admin_id': admin_id, 'user_counter': user_counter, 'user_sub': user_sub, 'year': year, 'month': month, 'ach_sub': ach_sub, 'ach_all': ach_all}
    return render(request, 'Dashio/index.html', {'dict': dict})


def login(request):
    if request.method == "GET":  # 如果提交方式为GET即显示login.html
        return render(request, "Dashio/login.html")
    else:  # 如果提交方式为POST
        id = request.POST.get('adminid')
        pwd = request.POST.get('password')
        if AdminTab.objects.filter(id=id).exists():
            if AdminTab.objects.filter(id=id)[0].password == pwd:
                global admin_id
                admin_id = id
                return redirect('/server/')
            else:
                return render(request, 'Dashio/login.html', {'script': "alert", 'wrong': '密码错误'})
        else:
            if id == '':
                return render(request, 'Dashio/login.html', {'script': "alert", 'wrong': '请填写登陆信息'})
            else:
                return render(request, 'Dashio/login.html', {'script': "alert", 'wrong': '该账号不存在'})


# 新加的内容
# 查看成果——对成果进行操作
def check_ach(request):
    if request.method == "GET":  # 如果提交方式为GET即显示check_achiev.html
        all_ach = AchievementTab.objects.filter()
        dict = {'all_achievements': all_ach, 'admin_id': admin_id}
        return render(request, 'Dashio/check_achiev.html', {'all_ach_dict': dict})
    else:  # 如果提交方式为POST
        all_ach = AchievementTab.objects.filter()
        return


# 删除某项成果
def delete_one_ach(request, id):
    AchievementTab.objects.filter(a_id=id).delete()
    return redirect('/checkachievement')


# 查看某项成果的详细信息
def check_one_ach(request, id):
    if request.method == "GET":
        ach_info = AchievementTab.objects.filter(a_id=id)[0]
        dict = {'admin_id': admin_id, 'ach_info': ach_info}
        return render(request, "Dashio/check_achiev_detail.html", {'check_ach': dict})
    else:
        return


# 修改某项成果
def edit_one_ach(request, id):
    global ach_info
    err_msg = ""
    a_id = id
    if request.method == "GET":
        ach_info = AchievementTab.objects.filter(a_id=id)[0]
        dict = {'admin_id': admin_id, 'ach_info': ach_info, 'err_msg': err_msg}
        return render(request, "Dashio/edit_achievement.html", {'edit_ach': dict})
    else:  # 如果提交方式为POST
        name = request.POST.get('name')
        year = request.POST.get('year')
        author_name = request.POST.get('authors')
        citation = request.POST.get('cite')
        j_a_name = request.POST.get('journal')
        file = request.POST.get('file')
        link = request.POST.get('link')
        if not year.isdigit():
            err_msg = "请填写正确发表年份"
            dict = {'admin_id': admin_id, 'ach_info': ach_info, 'err_msg': err_msg}
            return render(request, 'Dashio/edit_achievement.html', {'edit_ach': dict})
        elif not citation.isdigit():
            err_msg = "请填写正确引用数"
            dict = {'admin_id': admin_id, 'ach_info': ach_info, 'err_msg': err_msg}
            return render(request, 'Dashio/edit_achievement.html', {'edit_ach': dict})
        else:
            # 这里file需要换成file的存储位置！！！！！！！！
            # file_site = "no"
            AchievementTab.objects.filter(a_id=a_id).update(name=name, year=year, author_name=author_name, citation=citation,
                                      j_a_name=j_a_name, file=file, link=link)
            err_msg = "修改成果项成功"
            ach_info = AchievementTab.objects.filter(a_id=a_id)[0]
            dict = {'admin_id': admin_id, 'ach_info': ach_info, 'err_msg': err_msg}
            return render(request, 'Dashio/edit_achievement.html', {'edit_ach': dict})


# 添加成果
def add_achievement(request):
    err_msg = ""
    if request.method == "GET":
        dict = {'admin_id': admin_id, 'err_msg': err_msg}
        return render(request, "Dashio/add_achievement.html", {'add_ach': dict})
    else:  # 如果提交方式为POST
        name = request.POST.get('name')
        year = request.POST.get('year')
        author_name = request.POST.get('authors')
        citation = request.POST.get('cite')
        j_a_name = request.POST.get('journal')
        file = request.POST.get('file')
        link = request.POST.get('link')
        if not year.isdigit():
            err_msg = "请填写正确发表年份"
            dict = {'admin_id': admin_id, 'err_msg': err_msg}
            return render(request, 'Dashio/add_achievement.html', {'add_ach': dict})
        elif not citation.isdigit():
            err_msg = "请填写正确引用数"
            dict = {'admin_id': admin_id, 'err_msg': err_msg}
            return render(request, 'Dashio/add_achievement.html', {'add_ach': dict})
        else:
            if AchievementTab.objects.filter(name=name).exists():
                # 这里大概还需要检查作者？？？？
                err_msg = "该成果已存在"
                dict = {'admin_id': admin_id, 'err_msg': err_msg}
                return render(request, 'Dashio/add_achievement.html', {'add_ach': dict})
            else:
                # 这里file需要换成file的存储位置！！！！！！！！
                file_site = "no"
                AchievementTab.objects.create(name=name, year=year, author_name=author_name, citation=citation, j_a_name=j_a_name, file=file_site, link=link)
                err_msg = "添加成果项成功"
                dict = {'admin_id': admin_id, 'err_msg': err_msg}
                return render(request, 'Dashio/add_achievement.html', {'add_ach': dict})


# 显示所有新的成果认证申请信息
def check_newach_authen(request):
    if request.method == "GET":  # 如果提交方式为GET即显示check_achiev.html
        all_authen1 = AchievementAuthenTab.objects.filter()
        all_authen2 = SchAchAuthenTab.objects.filter()
        newauth = []
        for auth in all_authen2:
            newauth.append(NewSchAchAuthen(auth))
        dict = {'all_authen1': all_authen1, 'all_authen2': newauth, 'admin_id': admin_id}
        return render(request, 'Dashio/check_achiev_authen.html', {'ach_authen': dict})
    else:  # 如果提交方式为POST
        all_authen = AchievementTab.objects.filter()
        return


def check_one_newach_authen(request, id):
    global newach_auth
    if request.method == "GET":
        auth_info = AchievementAuthenTab.objects.filter(id=id)[0]
        newach_auth = auth_info
        scholar_id = auth_info.scholar_id
        scholar_name = ScholarTab.objects.filter(scholar_id=scholar_id)[0].name
        dict = {'admin_id': admin_id, 'auth_info': auth_info, 'scholar_name': scholar_name}
        return render(request, "Dashio/check_newachiev_details.html", {'check_newauth': dict})
    else:
        # 通过认证，加入成果表
        AchievementTab.objects.create(name=newach_auth.a_name, year=newach_auth.year,
                                      author_name=newach_auth.author_name, citation=newach_auth.citation,
                                      j_a_name=newach_auth.j_a_name, file=newach_auth.file, link=newach_auth.link)
        AchievementAuthenTab.objects.filter(id=id).delete()
        a_id = AchievementTab.objects.filter(name = newach_auth.a_name)[0].a_id
        newach_auth = AchievementAuthenTab.objects.filter(id=id)[0]
        ScholarAchievementTab.objects.create(scholar_id=newach_auth.scholar_id, a_id = a_id)
        # 将相同成果名的成果申请加入到关联申请表中
        auths = AchievementAuthenTab.objects.filter(a_name = newach_auth.a_name)
        for auth in auths:
            SchAchAuthenTab.objects.create(scholar_id=auth.scholar_id, a_id = a_id)
            AchievementAuthenTab.objects.filter(id = auth.id).delete()
        all_authen1 = AchievementAuthenTab.objects.filter()
        all_authen2 = SchAchAuthenTab.objects.filter()
        newauth = []
        for auth in all_authen2:
            newauth.append(NewSchAchAuthen(auth))
        err_msg = "成果认证成功"
        dict = {'all_authen1': all_authen1, 'all_authen2': newauth, 'admin_id': admin_id, 'err_msg': err_msg}
        return render(request, 'Dashio/check_achiev_authen.html', {'ach_authen': dict})


class NewSchAchAuthen():
    def __init__(self, auth):
        self.authen = auth
        self.a_name = AchievementTab.objects.filter(a_id=auth.a_id)[0].name
        self.scholar_name = ScholarTab.objects.filter(scholar_id=auth.scholar_id)[0].name


def check_one_sch_ach_authen(request, id):
    global sch_ach_auth
    if request.method == "GET":
        auth_info = SchAchAuthenTab.objects.filter(id=id)[0]
        sch_ach_auth = auth_info
        scholar_id = auth_info.scholar_id
        a_id = auth_info.a_id
        scholar_name = ScholarTab.objects.filter(scholar_id=scholar_id)[0].name
        ach_info = AchievementTab.objects.filter(a_id=a_id)[0]
        a_name = ach_info.name
        year = ach_info.year
        author_name = ach_info.author_name
        citation = ach_info.citation
        j_a_name = ach_info.j_a_name
        file = ach_info.file
        link = ach_info.link
        dict = {'admin_id': admin_id, 'auth_info': auth_info, 'scholar_name': scholar_name, 'a_name': a_name,
                'year': year, 'author_name': author_name, 'citation': citation, 'j_a_name':j_a_name,
                'file':file, 'link':link}
        return render(request, "Dashio/check_schach_authen_details.html", {'check_schach_auth': dict})
    else:
        sch_ach_auth = SchAchAuthenTab.objects.filter(id=id)[0]
        ScholarAchievementTab.objects.create(scholar_id=sch_ach_auth.scholar_id, a_id=sch_ach_auth.a_id)
        SchAchAuthenTab.objects.filter(id=id).delete()
        all_authen1 = AchievementAuthenTab.objects.filter()
        all_authen2 = SchAchAuthenTab.objects.filter()
        newauth = []
        for auth in all_authen2:
            newauth.append(NewSchAchAuthen(auth))
        err_msg = "成果关联认证成功"
        dict = {'all_authen1': all_authen1, 'all_authen2': newauth, 'admin_id': admin_id, 'err_msg':err_msg}
        return render(request, 'Dashio/check_achiev_authen.html', {'ach_authen': dict})


# 查看院系信息——对院系信息进行操作
def check_department(request):
    if request.method == "GET":  # 如果提交方式为GET即显示login.html
        all_dep = Department.objects.filter()
        dict = {'all_departments': all_dep, 'admin_id': admin_id}
        return render(request, 'Dashio/check_department.html', {'all_dep_dict': dict})
    else:  # 如果提交方式为POST
        return


# 删除某个院系
def delete_one_dep(request, id):
    Department.objects.filter(d_id=id).delete()
    return redirect('/checkdepartment')


# 查看某个院系的详细信息
def check_one_dep(request, id):
    if request.method == "GET":
        dep_info = Department.objects.filter(d_id=id)[0]
        dict = {'admin_id': admin_id, 'dep_info': dep_info}
        return render(request, "Dashio/check_dep_brief.html", {'check_dep': dict})
    else:
        return


# 修改某个院系
def edit_one_dep(request, id):
    global dep_info
    err_msg = ""
    d_id=id
    if request.method == "GET":
        dep_info = Department.objects.filter(d_id=id)[0]
        dict = {'admin_id': admin_id, 'dep_info': dep_info, 'err_msg': err_msg}
        return render(request, "Dashio/edit_department.html", {'edit_dep': dict})
    else:  # 如果提交方式为POST
        number = request.POST.get('number')
        name = request.POST.get('d_name')
        brief = request.POST.get('brief_info')
        if not number.isdigit():
            err_msg = "院系编号需要由数字组成"
            dict = {'admin_id': admin_id, 'dep_info': dep_info, 'err_msg': err_msg}
            return render(request, 'Dashio/edit_department.html', {'edit_dep': dict})
        elif len(number) != 2:
            err_msg = "院系编号需有2位数字"
            dict = {'admin_id': admin_id, 'dep_info': dep_info, 'err_msg': err_msg}
            return render(request, 'Dashio/add_department.html', {'edit_dep': dict})
        else:
            Department.objects.filter(d_id=id).update(number=number, name=name, brief=brief)
            err_msg = "院系信息修改成功"
            dep_info = Department.objects.filter(d_id=d_id)[0]
            dict = {'admin_id': admin_id, 'dep_info': dep_info, 'err_msg': err_msg}
            return render(request, 'Dashio/edit_department.html', {'edit_dep': dict})


# 添加某个院系
def add_department(request):
    err_msg = ""
    if request.method == "GET":
        dict = {'admin_id': admin_id, 'err_msg': err_msg}
        return render(request, "Dashio/add_department.html", {'add_dep': dict})
    else:  # 如果提交方式为POST
        number = request.POST.get('number')
        name = request.POST.get('d_name')
        brief = request.POST.get('brief_info')
        if not number.isdigit():
            err_msg = "院系编号需要由数字组成"
            dict = {'admin_id': admin_id, 'err_msg': err_msg}
            # return render(request, "Dashio/add_department.html", {'add_dep': dict})
            return render(request, 'Dashio/add_department.html', {'add_dep': dict})
        elif len(number) != 2:
            err_msg = "院系编号需有2位数字"
            dict = {'admin_id': admin_id, 'err_msg': err_msg}
            return render(request, 'Dashio/add_department.html', {'add_dep': dict})
        else:
            if Department.objects.filter(number=number).exists():
                err_msg = "该院系编号已存在"
                dict = {'admin_id': admin_id, 'err_msg': err_msg}
                return render(request, 'Dashio/add_department.html', {'add_dep': dict})
            elif Department.objects.filter(name=name).exists():
                err_msg = "该院系名称已存在"
                dict = {'admin_id': admin_id, 'err_msg': err_msg}
                return render(request, 'Dashio/add_department.html', {'add_dep': dict})
            else:
                Department.objects.create(number=number, name=name, brief=brief)
                err_msg = "添加院系成功"
                dict = {'admin_id': admin_id, 'err_msg': err_msg}
                return render(request, 'Dashio/add_department.html', {'add_dep': dict})


# 查看举报信息
def check_report(request):
    if request.method == "GET":  # 如果提交方式为GET即显示login.html
        all_report = ReportTab.objects.filter(flag=0)
        dict = {'all_reports': all_report, 'admin_id': admin_id}
        return render(request, 'Dashio/check_report.html', {'all_rep_dict': dict})
    else:  # 如果提交方式为POST
        return


# 删除某个举报信息
def delete_one_report(request, id):
    ReportTab.objects.filter(r_id=id).delete()
    return redirect('/checkreport')


# 通过某个举报信息
def check_one_report(request, id):
    if request.method == "GET":
        ReportTab.objects.filter(r_id=id).update(flag=1)
        return redirect('/checkreport')
    else:
        return


# 用户相关
# 查看学者用户
def scholar(request):
    all_scholar = ScholarTab.objects.all()
    dict = {'admin_id': admin_id, 'all_sch': all_scholar}
    return render(request, 'Dashio/scholar.html', {'all_scholar': dict})


# 删除学者用户
def del_scholar(request, id):
    ScholarTab.objects.filter(user_id=id).delete()
    return redirect('/scholar')


# 查看学生用户
def student(request):
    all_student = student_tab.objects.all()
    dict = {'admin_id': admin_id, 'all_student': all_student}
    return render(request, 'Dashio/student.html', {'all_student_dict': dict})


# 删除学生用户
def del_student(request,id):
    student_tab.objects.filter(user_id=id).delete()
    return redirect('/student')


# 查看用户身份申请
def authen_user(request):
    all_authen = authen_tab.objects.all()
    dict = {'admin_id': admin_id, 'all_authen': all_authen}
    return render(request, 'Dashio/authen_user.html', {'all_authen_dict': dict})


# 删除身份申请
def del_authen(request, authen_id):
    # user_id = request.GET.get('id')
    authen_tab.objects.filter(authen_id=authen_id).delete()
    user_authen_tab.objects.filter(authen_id=authen_id).delete()
    return redirect('/authen_user')


# 通过用户的身份申请
def pass_authen(request, authen_id):  # 通过后向学者表/用户表中添加对应表项
    authen_info = authen_tab.objects.get(authen_id=authen_id)
    user = user_authen_tab.objects.get(authen_id=authen_id)
    user_info = user_tab.objects.get(user_id=user.user_id)
    if authen_info.identity == 1:  # 学者
        ScholarTab.objects.create(user_id=user_info.user_id, school="default", name=user_info.user_name, email=authen_info.email, p_title="default")
        user_tab.objects.filter(user_id=user_info.user_id).update(authority=1)
    elif authen_info.identity == 2:  # 学生
        student_tab.objects.create(user_id=user_info.user_id,school="default", name=user_info.user_name,email=authen_info.email)
        user_tab.objects.filter(user_id=user_info.user_id).update(authority=2)
    return redirect('/del_user/'+authen_id)


# 查看所有用户信息
def check_all_user(request):
    if request.method == "GET":  # 如果提交方式为GET即显示login.html
        all_user = user_tab.objects.filter()
        dict = {'all_users': all_user, 'admin_id': admin_id}
        return render(request, 'Dashio/check_all_user.html', {'user_dict': dict})
    else:  # 如果提交方式为POST
        return


# 删除用户信息
def delete_user(request, id):
    user_tab.objects.filter(user_id=id).delete()
    return redirect('/checkuser')


# 新爬取成果管理员确认
def add_get_achievement(request):
    # 将待确认成果展示
    item = new_achievement_tab.objects.all()
    dict = {'item': item, 'admin_id': admin_id}
    # print(item)
    return render(request, 'Dashio/add_get_achievement.html', {'dict': dict})


# 新爬取成果通过
def pass_new_achievement(request, id):
    # 将对应关系加入待认领表中
    ach = new_achievement_tab.objects.get(a_id=id)

    with open(relation_all_file, 'r', encoding='utf-8') as relation_csv:
        reader = csv.DictReader(relation_csv, ['au_id', 'ach_id'])
        data = defaultdict(list)
        for line in reader:
            if int(line['ach_id']) == ach.get_id:
                data[ach.get_id].append(line['au_id'])

    for i in data[ach.get_id]:
        new_rel = new_relation_tab.objects.create(auth_id=i,ach_id=ach.get_id)
    return redirect('/del_new_achievement'+'/'+id)


def del_new_achievement(request, id):
    new_achievement_tab.objects.filter(a_id=id).delete()
    return redirect('/add_get_achievement')


def user_id_get(request):
    #user_table.objects.filter(wechatid=request.GET[''])
	print(request.GET['wxNickName'])
	retData = {}
	retData['id'] = ''
	return HttpResponse(json.dumps(retData), content_type = "application/json")

def wx_register(request):
	print(request.GET['wechatid'])
	print(request.GET['school'])
	autho = 0
	print(request.GET['authority'])
	if (request.GET['authority'] == "学生用户"):
		autho = 1
	if (request.GET['authority'] == "学者用户"):
		autho = 2
	print(autho)
	if len(user_tab.objects.filter(wechatid=request.GET['wechatid'])) == 0:
		user_tab(user_name = request.GET['name'], wechatid = request.GET['wechatid'], authority = autho).save()
	if (autho == 1 or autho == 2):
		authen_tab(email = request.GET['mail'], name = request.GET['name'], sno = request.GET['schoolid'], identity = autho).save()
		retData = {}
		retData['b'] = 'b'
		t1 = user_tab.objects.get(wechatid = request.GET['wechatid'])
		t2 = authen_tab.objects.get(name = request.GET['name'])
		print(t1.user_id)
		user_authen_tab(user_id = t1.user_id, authen_id = t2.authen_id).save()
		return HttpResponse(json.dumps(retData), content_type = "application/json")
	retData = {}
	retData['a'] = 'a'
	return HttpResponse(json.dumps(retData), content_type = "application/json")


def hasconnect_A(paper_id, wxid):
	t1 = user_tab.objects.get(wechatid = wxid)
	if len(collect_achievement_tab.objects.filter(user_id = t1.user_id, a_id = paper_id)) == 0:
		return 1
	return 0


def searchPaper(request):
	text = request.GET['text']
	number = 1
	retData = []
	print(text)
	achieves = AchievementTab.objects.all()
	for i in achieves:
		if text in i.name:
			a = {}
			a["id"] = number
			a["paper_id"] = i.a_id
			a["useDate"] = i.name
			a["cx"] = i.author_name
			a["time"] = i.year
			a["isShow"] = hasconnect_A(i.a_id, request.GET['WXID'])
			a["feiyong"] = i.citation
			number = number + 1
			retData.append(a)
	return HttpResponse(json.dumps(retData), content_type = "application/json")





def collectPaper(request):
	retData = {}
	paperId = request.GET['paperId']
	isCollect = request.GET['isCollect']
	WXID = request.GET['WXID']
	print(paperId)
	print(isCollect)
	print(WXID)
	t1 = user_tab.objects.get(wechatid = WXID)
	if (isCollect == '1'):
		print("hahaha")
		collect_achievement_tab(user_id = t1.user_id, a_id = paperId).save()
	else:
		print("xixixi")
		collect_achievement_tab.objects.filter(user_id = t1.user_id, a_id = paperId).delete()
	return HttpResponse(json.dumps(retData), content_type = "application/json")	
