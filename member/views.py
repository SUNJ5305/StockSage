import time

from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render

from member.models import Member
from decorator.decorator import loginchk, loginadmin


# Create your views here.


def signup(request) :
    if request.method != "POST":
        return render(request, "member/signup.html")
    else :
        id1 = request.POST["id"]
        if Member.objects.filter(id=id1).exists():
            context = {"msg" : "존재하는 아이디 입니다.", "url" : "/member/signup/"}
            return render(request, "alert.html", context)
        else :
            member = Member(id=request.POST['id'],
                            pass1=request.POST['pass1'],
                            name=request.POST['name'],
                            gender=request.POST['gender'],
                            tel=request.POST['tel'],
                            email=request.POST['email'])
            member.save()
            context = {"msg" : "회원가입을 환영합니다.", "url" : "/member/login/"}
            return render(request, "alert.html", context)

def login(request):
    if request.method != "POST":
        return render(request, "member/login.html")
    else :
        id1 = request.POST["id"]
        pass1 = request.POST["pass1"]
        try :
            member = Member.objects.get(id=id1)
        except :
            context = {"msg" : "아이디를 확인하세요", "url" : "/member/login/"}
            return render(request, "alert.html", context)
        else :
            if pass1 == member.pass1:
                request.session['id'] = id1
                context = {"msg" : "환영합니다.", "url" : "/stock/index/"}
                return render(request, "alert.html", context)

            else :
                context = {"msg" : "비밀번호를 확인하세요.", "url":"/member/login/"}
                return render(request, "alert.html", context)

@loginchk
def logout(request) :
    auth.logout(request)
    context = {"msg" : "로그아웃 되었습니다.", "url" : "/member/login"}
    return render(request, "alert.html", context)

@loginchk
def info(request):
    id1 = request.session["id"]
    member = Member.objects.get(id=id1)
    return render(request, "member/info.html", {"member": member})

@loginchk
def update(request):
    id1 = request.session["id"]
    member = Member.objects.get(id=id1)
    if request.method != "POST":
        return render(request, "member/update.html", {"member": member})
    else:
        if member.pass1 == request.POST['password']:
            member.name = request.POST["name"]
            member.gender = request.POST["gender"]
            member.tel = request.POST["tel"]
            member.email = request.POST["email"]
            member.save()
            context = {"msg" : "정보가 수정되었습니다.", "url" : "/member/info/"}
            return render(request, "alert.html", context)
        else:
            context = {"msg" : "비밀번호를 확인해주세요.", "url" : "/member/update/"}
            return render(request, "alert.html", context)

@loginchk
def chgpass(request):
    id1 = request.session["id"]
    member = Member.objects.get(id=id1)
    if request.method != "POST":
        return render(request, "member/chgpass.html")
    else:
        if member.pass1 == request.POST['current_password']:
            if request.POST['new_password'] == request.POST['confirm_password']:
                member.pass1 = request.POST["new_password"]
                member.save()
                context = {"msg" : "비밀번호가 변경되었습니다.", "url" : "/member/login/"}
                return render(request, "alert.html", context)
            else:
                context = {"msg" : "새 비밀번호가 서로 일치하지 않습니다.", "url" : "/member/chgpass/"}
                return render(request, "alert.html", context)
        else:
            context = {"msg" : "비밀번호를 확인해주세요.", "url" : "/member/chgpass/"}
            return render(request, "alert.html", context)

@loginchk
def delete(request):
    id1 = request.session["id"]
    member = Member.objects.get(id=id1) #select 문장 실행
    if request.method != 'POST':
        return render(request, 'member/delete.html', {"member" : member})
    else:
        if request.POST["password"] == member.pass1:
            member.delete()
            auth.logout(request)
            context = {"msg":"회원이 탈퇴되었습니다.", "url":"/member/login/"}
            return render(request, "alert.html", context)
        else:
            context = {"msg":"비밀번호가 틀립니다.", "url":"/member/delete/"}
            return render(request, "alert.html", context)

@loginadmin
def admin(request):
    if request.method != "POST":
        mlist = Member.objects.all()
        return render(request, "member/admin.html", {"mlist": mlist})