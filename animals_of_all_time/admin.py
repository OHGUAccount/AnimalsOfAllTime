from django.contrib import admin
from animals_of_all_time.models import UserProfile, Animal


# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Animal)