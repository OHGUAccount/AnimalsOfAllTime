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
    path('add_discussion/', views.AddDiscussionView.as_view(), name='add_discussion'),
    path('discussions/', views.ListDiscussionView.as_view(), name = "discussions"),
    path('discussion/', views.DiscussionView.as_view(), name = "discussion"),

    # petition urls
    path('petitions/', views.ListPetitionView.as_view(), name='petitions'),
    path('sign_petition/', views.SignPetitionView.as_view(), name='sign_petition'),
    path('petitions/<slug:petition_slug>/', views.PetitionView.as_view(), name='petition'),
    path('add_petition/', views.AddPetitionForm.as_view(), name='add_petition'),

    # profile urls
    path('profiles/', views.ListProfileView.as_view(), name='profiles'),
    path('profiles/<slug:username>/', views.ProfileView.as_view(), name='profile'),

    # userlist view
    path('lists/', views.ListUserListView.as_view(), name='lists'),
    path('lists/<slug:user_list_slug>/', views.UserListView.as_view(), name='list'),
    path('add_list/', views.AddUserListView.as_view(), name='add_list'),
]