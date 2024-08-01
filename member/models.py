from django.db import models
# Create your models here.

class Member(models.Model) :
    id = models.CharField(max_length=20, primary_key=True)
    pass1 = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    gender = models.IntegerField(default=0)
    tel = models.CharField(max_length=20)
    email = models.CharField(max_length=100)


class PageAccessLog(models.Model):
    access_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    page_url = models.CharField(max_length=255)
    user_id = models.CharField(max_length=20, null=True, blank=True)  # 사용자 ID 필드

    def __str__(self):
        return f"User {self.user_id} accessed {self.page_url} at {self.access_time}"