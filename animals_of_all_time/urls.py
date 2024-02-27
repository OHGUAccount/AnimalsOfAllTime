from django.urls import path
from animals_of_all_time import views

app_name = 'animals-of-all-time'

urlpatterns = [
path('', views.index, name='index'),
]