# member/middleware.py

from django.utils import timezone
from member.models import PageAccessLog

class PageAccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # 세션에서 사용자 ID 가져오기
        user_id = request.session.get('id', None)

        # 로그를 남길 페이지 URL 필터링
        if not self.should_log(request.path):
            return response

        # 로그 기록
        log = PageAccessLog(
            access_time=timezone.now(),  # 현재 시간 기록
            ip_address=request.META.get('REMOTE_ADDR'),  # 클라이언트 IP 주소 기록
            page_url=request.path,  # 요청된 페이지 URL 기록
            user_id=user_id  # 사용자 ID 기록
        )
        log.save()

        return response

    def should_log(self, path):
        """
        로그를 남길 페이지 URL을 필터링합니다.
        예를 들어, 정적 파일이나 특정 패턴의 URL을 제외합니다.
        """
        # 예: .png, .jpg 같은 이미지 파일 제외
        if path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.css', '.js')):
            return False

        # 예: /static/ 또는 /media/와 같은 경로 제외
        if path.startswith('/static/') or path.startswith('/media/'):
            return False

        # 기타 필요한 필터링 조건을 추가할 수 있습니다.
        return True
