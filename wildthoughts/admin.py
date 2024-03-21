from django.contrib import admin
from wildthoughts.models import Animal, Comment, Discussion, Petition, UserList, UserProfile


# Register your models here.
admin.site.register(Animal)
admin.site.register(Comment)
admin.site.register(Discussion)
admin.site.register(Petition)
admin.site.register(UserList)
admin.site.register(UserProfile)
