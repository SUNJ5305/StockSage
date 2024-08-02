from django.shortcuts import render

# 로그인이 된 사용자만 접근할 수 있도록 한다.
def loginchk(func):
    def check(request):  #def function(request, id)
        print("deco")
        try:
            login = request.session["id"]
        except:
            context = {"msg": "로그인 하세요", "url": "/member/login/"}
            return render(request, "alert.html", context)
        return func(request)
    return check

# 관리자만 접근할 수 있도록 한다.
def loginadmin(func):
    def check(request, *args, **kwargs):
        try:
            login = request.session["id"]
        except: # 로그아웃 상태
            context = {"msg":"로그인하세요", "url":"/"}
            return render(request, "alert.html", context)
        else:
            if login != 'admin' :
                context = {"msg":"관리자전용 페이지입니다.","url":"/"}
                return render(request, "alert.html", context)
        return func(request, *args, **kwargs)
    return check