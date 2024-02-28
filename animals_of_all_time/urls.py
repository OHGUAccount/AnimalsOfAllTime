from django.urls import path
from animals_of_all_time import views

app_name = 'animals-of-all-time'

urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
    path('animals/', views.ListAnimalsView.as_view(), name='animals'),
    path('animals/<slug:animal_name_slug>/', views.AnimalView.as_view(), name='animal'),
    path('profiles/', views.ListProfileView.as_view(), name='profiles'),
]