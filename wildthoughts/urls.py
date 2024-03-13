from django.urls import path
from wildthoughts import views

app_name = 'wildthoughts'

urlpatterns = [
    # animal urls
    path('add_animal/', views.AddAnimalView.as_view(), name='add_animal'),
    path('animals/', views.ListAnimalsView.as_view(), name='animals'),
    path('animals/<slug:animal_name_slug>/', views.AnimalView.as_view(), name='animal'),

    # base urls
    path('index/', views.IndexView.as_view(), name='index'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('theme/', views.ThemeView.as_view(), name='theme'),

    # comments urls

    # discussion urls

    # profile urls
    path('profiles/', views.ListProfileView.as_view(), name='profiles'),
    path('profiles/<slug:username>/', views.ProfileView.as_view(), name='profile'),
    path('profiles/<slug:username>/update', views.UpdateProfileView.as_view(), name='update_profile'),


    # userlist view
    path('lists/', views.UserListView.as_view(), name='lists'),
    path('add_list/', views.AddUserListView.as_view(), name='add_list'),
]