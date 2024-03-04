from django.urls import path
from wildthoughts import views

app_name = 'wildthoughts'

urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
    path('animals/', views.ListAnimalsView.as_view(), name='animals'),
    path('animals/<slug:animal_name_slug>/', views.AnimalView.as_view(), name='animal'),
    path('profiles/', views.ListProfileView.as_view(), name='profiles'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('add_animal/', views.AddAnimalView.as_view(), name='add_animal'),
    path('lists/', views.UserListView.as_view(), name='lists'),
    path('profiles/<slug:username>/', views.ProfileView.as_view(), name='profile'),
    path('overrated/', views.OverratedView.as_view(), name='overrated'),
    path('underrrated/', views.UnderratedView.as_view(), name='underrated'),
]