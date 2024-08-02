from django.contrib import auth
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from decorator.decorator import loginchk, loginadmin
from member.models import Member, PageAccessLog

from django.http import JsonResponse
from django.views.decorators.http import require_GET

def signup(request):
    if request.method != "POST":
        return render(request, "member/signup.html")
    else:
        id1 = request.POST["id"]
        if Member.objects.filter(id=id1).exists():
            context = {"msg": "존재하는 아이디 입니다.", "url": "/member/signup/"}
            return render(request, "alert.html", context)
        else:
            member = Member(id=request.POST['id'],
                            pass1=request.POST['pass1'],
                            name=request.POST['name'],
                            gender=request.POST['gender'],
                            tel=request.POST['tel'],
                            email=request.POST['email'])
            member.save()
            context = {"msg": "회원가입을 환영합니다.", "url": "/member/login/"}
            return render(request, "alert.html", context)


def login(request):
    if request.method != "POST":
        return render(request, "member/login.html")
    else:
        id1 = request.POST["id"]
        pass1 = request.POST["pass1"]
        try:
            member = Member.objects.get(id=id1)
        except Member.DoesNotExist:
            context = {"msg": "아이디를 확인하세요", "url": "/member/login/"}
            return render(request, "alert.html", context)
        else:
            if member.pass1 == pass1:
                if member.is_active:  # 비활성화 상태 확인
                    request.session['id'] = id1
                    context = {"msg": id1 + "님 환영합니다.", "url": "/stock/index/"}
                    return render(request, "alert.html", context)
                else:
                    context = {"msg": "계정이 비활성화되었습니다.", "url": "/member/login/"}
                    return render(request, "alert.html", context)
            else:
                context = {"msg": "비밀번호를 확인하세요.", "url": "/member/login/"}
                return render(request, "alert.html", context)


def searchid(request):
    if request.method != "POST":
        return render(request, "member/searchid.html")
    else:
        email = request.POST.get("email")
        name = request.POST.get("name")

        try:
            member = Member.objects.get(email=email, name=name)
            context = {"msg": f"아이디는 {member.id} 입니다.", "url": "/member/login/"}
            return render(request, "alert.html", context)
        except Member.DoesNotExist:
            context = {"msg": "해당 정보로 아이디를 찾을 수 없습니다.", "url": "/member/searchid/"}
            return render(request, "alert.html", context)


def searchpass(request):
    if request.method == "POST":
        if 'new-pass1' in request.POST and 'new-pass2' in request.POST:
            id1 = request.POST.get("id")
            new_pass1 = request.POST.get("new-pass1")
            new_pass2 = request.POST.get("new-pass2")

            if new_pass1 and new_pass2:
                if new_pass1 == new_pass2:
                    try:
                        member = Member.objects.get(id=id1)
                        member.pass1 = new_pass1
                        member.save()
                        return redirect('/member/login/')  # 비밀번호 재설정 후 로그인 페이지로 리디렉션
                    except Member.DoesNotExist:
                        context = {"msg": "해당 ID로 회원을 찾을 수 없습니다.", "url": "/member/searchpass/"}
                        return render(request, "alert.html", context)
                else:
                    context = {"msg": "비밀번호가 서로 다릅니다.", "url": "/member/searchpass/"}
                    return render(request, "alert.html", context)
            else:
                context = {"msg": "모든 필드를 입력해야 합니다.", "url": "/member/searchpass/"}
                return render(request, "alert.html", context)

        # 비밀번호 재설정 폼을 처리하는 부분
        id1 = request.POST.get("id")
        email = request.POST.get("email")
        if id1 and email:
            try:
                member = Member.objects.get(id=id1, email=email)
                return render(request, "member/searchpass.html", {"id": id1, "step": "reset"})
            except Member.DoesNotExist:
                context = {"msg": "해당 정보로 회원을 찾을 수 없습니다.", "url": "/member/searchpass/"}
                return render(request, "alert.html", context)
        else:
            context = {"msg": "아이디와 이메일을 입력해야 합니다.", "url": "/member/searchpass/"}
            return render(request, "alert.html", context)

    # GET 요청 시 또는 첫 번째 단계의 폼을 렌더링
    return render(request, "member/searchpass.html")

@loginchk
def logout(request):
    auth.logout(request)
    context = {"msg": "로그아웃 되었습니다.", "url": "/member/login"}
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
            context = {"msg": "정보가 수정되었습니다.", "url": "/member/info/"}
            return render(request, "alert.html", context)
        else:
            context = {"msg": "비밀번호를 확인해주세요.", "url": "/member/update/"}
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
                context = {"msg": "비밀번호가 변경되었습니다.", "url": "/member/login/"}
                return render(request, "alert.html", context)
            else:
                context = {"msg": "새 비밀번호가 서로 일치하지 않습니다.", "url": "/member/chgpass/"}
                return render(request, "alert.html", context)
        else:
            context = {"msg": "비밀번호를 확인해주세요.", "url": "/member/chgpass/"}
            return render(request, "alert.html", context)


@loginchk
def delete(request):
    id1 = request.session["id"]
    member = Member.objects.get(id=id1)  # select 문장 실행
    if request.method != 'POST':
        return render(request, 'member/delete.html', {"member": member})
    else:
        if request.POST["password"] == member.pass1:
            member.delete()
            auth.logout(request)
            context = {"msg": "회원이 탈퇴되었습니다.", "url": "/member/login/"}
            return render(request, "alert.html", context)
        else:
            context = {"msg": "비밀번호가 틀립니다.", "url": "/member/delete/"}
            return render(request, "alert.html", context)


@loginadmin
def admin(request):
    # GET 파라미터에서 탭 상태를 가져옴
    current_tab = request.GET.get('tab', 'user-list')  # 기본값은 'user-list'

    # 회원 목록 가져오기
    mlist = Member.objects.all()

    # 로그 기록 가져오기 및 필터링
    logs = PageAccessLog.objects.exclude(page_url__icontains='/admin/').order_by('-access_time')

    # 날짜 범위 필터링
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        logs = logs.filter(access_time__range=[start_date, end_date])

    # 페이지네이션 처리
    paginator = Paginator(logs, 10)  # 페이지당 10개의 로그 항목
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "mlist": mlist,
        "page_obj": page_obj,
        "current_tab": current_tab
    }
    return render(request, "member/admin.html", context)

@require_GET
@loginadmin
def toggle_member_status(request, member_id):
    try:
        member = Member.objects.get(id=member_id)
        member.is_active = not member.is_active
        member.save()
        return JsonResponse({'status': 'success'})
    except Member.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '회원이 존재하지 않습니다.'})