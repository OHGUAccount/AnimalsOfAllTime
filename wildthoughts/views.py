from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views import View

from registration.backends.simple.views import RegistrationView

from wildthoughts.forms import AnimalForm, UserListForm
from wildthoughts.models import Animal, Comment, Discussion, UserList, UserProfile


"""--------------------------------------------------------HELPER CLASSES -------------------------------------------------------------"""
class Sorter:
    @staticmethod
    def sort(choice, model, profile=None):
        options_order = {
            'title':'title', 
            'name': 'name', 
            'overrated': '-upvotes',
            'underrated': '-downvotes',
            'newest': '-date',
            'oldest': 'date',
        } 

        if model is Animal and choice == 'title':
            choice = 'name'
        elif model is Comment and choice in ['title', 'name']:
            choice = 'newest'
        elif choice not in options_order:
            choice = 'newest'
            
        field = options_order[choice]

        if profile:
            results = model.objects.filter(author=profile).order_by(field)
        else:
            results = model.objects.order_by(field)

        return choice, results    
    

"""------------------------------------------------------- ANIMAL VIEWS ------------------------------------------------------------"""
class AnimalView(View):
    def get(self, request, animal_name_slug):
        animal = Animal.objects.get(slug=animal_name_slug)
        discussions = Discussion.objects.filter(animal=animal)
        return render(request, 'wildthoughts/animal/animal.html', context={'animal': animal, 'discussions':discussions})
    

class AddAnimalView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = AnimalForm()
        return render(request, 'wildthoughts/animal/add_animal.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = AnimalForm(request.POST, request.FILES) 

        if form.is_valid():
            animal = form.save(commit=False)
            author = UserProfile.objects.get(user=request.user)
            animal.author = author
            animal.slug = slugify(animal.name)
            animal.save()
            return redirect(reverse('wildthoughts:animal', kwargs={'animal_name_slug': animal.slug}))
        else:
            print(form.errors)

        return render(request, 'wildthoughts/animal/add_animal.html', {'form': form})
    

class ListAnimalsView(View):
    def get(self, request):
        sort_by = request.GET.get('sort_by')
        sort_by, results = Sorter.sort(sort_by, Animal)
        # set up pagination
        p = Paginator(results, 20)
        page = request.GET.get('page')
        animals = p.get_page(page)
        return render(request, 'wildthoughts/animal/list_animals.html', {'animals':animals, 'sort_by':sort_by})
    

"""------------------------------------------------------------ BASE VIEWS------------------------------------------------------------"""
class IndexView(View):
    def get(self, request):
        overrated_animals = Animal.objects.order_by('-downvotes')[:5]
        underrated_animals = Animal.objects.order_by('-upvotes')[:5]
        context_dict = {
            'overrated_animals': overrated_animals,
            'underrated_animals': underrated_animals
        }
        return render(request, 'wildthoughts/base/index.html', context=context_dict)
    

class SearchView(View):
    def post(self, request):
        searched = request.POST['searched']
        category = request.POST['category']

        if not searched:
            results = None
        elif category == 'Animals':
            results = Animal.objects.filter(name__contains=searched)
        elif category == 'Discussions':
            results = Discussion.objects.filter(title__contains=searched)
        elif category == 'Lists':
            results = UserList.objects.filter(title__contains=searched)
        elif category == 'Profiles':
            results = UserProfile.objects.filter(user__username__contains=searched)
        context_dict = {
            'searched': searched,
            'category': category,
            'results': results
        }
        
        return render(request, 'wildthoughts/base/search.html', context=context_dict)


class ThemeView(View):
    def get(self, request):
        theme = request.GET.get('theme')
        if theme in ['dark', 'light']:
            response = HttpResponse("Theme set to: " + theme)
            response.set_cookie('theme', theme)
            return response
        else:
            return HttpResponse(-1)
            

"""-------------------------------------------------------------- PROFILE VIEWS ------------------------------------------------------"""
class ProfileView(View):
    tab_to_model = {
        'animals': Animal,
        'discussions': Discussion,
        'comments': Comment,
        'lists': UserList,
    }

    def get(self, request, username):
        profile = UserProfile.objects.get(user=User.objects.get(username=username))
        loguser = None
        if (request.user.is_authenticated):
            loguser = request.user

        tab = request.GET.get('tab')
        sort_by = request.GET.get('sort_by')
        if tab not in ProfileView.tab_to_model:
            tab = 'animals'
        
        model = ProfileView.tab_to_model[tab]
        sort_by, results = Sorter.sort(sort_by, model, profile)
        
        context_dict = {
        'profile': profile, 
         'loguser':loguser, 
         'sort_by':sort_by, 
         'tab': tab, 
         'results': results
         }
        
        return render(request, 'wildthoughts/profile/profile.html', context=context_dict)    


class NewRegistrationView(RegistrationView):
    # create an instance of UserProfile when the user registers
    def register(self, form):
        new_user = super().register(form)
        UserProfile.objects.get_or_create(user=new_user)
        return new_user
    
    def get_success_url(self, user):
            return reverse('wildthoughts:index')
    

class ListProfileView(View):
    def get(self, request):
        # set up pagination
        p = Paginator(UserProfile.objects.all(), 20)
        page = request.GET.get('page')
        profiles = p.get_page(page)
        return render(request, 'wildthoughts/profile/list_profiles.html', {'profiles':profiles})


"""-------------------------------------------------------- LIST VIEWS -------------------------------------------------------------"""
# (Renamed to not be confused with python list)
class UserListView(View):
    def get(self, request):
        sort_by = request.GET.get('sort_by')
        sort_by, results = Sorter.sort(sort_by, UserList)

        # set up pagination
        p = Paginator(results, 20)
        page = request.GET.get('page')
        user_lists = p.get_page(page)
        
        return render(request, 'wildthoughts/user_list/user_list.html', context={'user_lists': user_lists, 'sort_by': sort_by})
    

class AddUserListView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = UserListForm()
        animals = Animal.objects.all()
        return render(request, 'wildthoughts/user_list/add_user_list.html', {'animals': animals, 'form': form})
    
    @method_decorator(login_required)
    def post(self, request):
        form = UserListForm(request.POST)
        animals = Animal.objects.all()

        if form.is_valid():
            user_list = form.save(commit=False)
            author = UserProfile.objects.get(user=request.user)
            user_list.author = author
            user_list.save()
            form.save_m2m() 
            return redirect(reverse('wildthoughts:lists'))
        else:
            print(form.errors)

        return render(request, 'wildthoughts/user_list/add_user_list.html', {'animals': animals, 'form': form})
    