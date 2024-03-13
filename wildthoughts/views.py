from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Model
from django.http import HttpResponse, JsonResponse

from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views import View

from registration.backends.simple.views import RegistrationView

from wildthoughts.forms import AnimalForm, UserListForm, DiscussionForm, PetitionForm
from wildthoughts.models import Animal, Comment, Discussion, Petition, UserList, UserProfile


"""--------------------------------------------------------HELPER CLASSES -------------------------------------------------------------"""
class Sorter:
    """
    class dedicated to sort a model by specifying a option
    the option is then converted to an appropriate field
    if option is invalid returns model sorted by date
    """
    VALID_MODELS = {Animal, Comment, Discussion, Petition, UserList, UserProfile}
    OPTIONS_ORDER = {
        'title':'title', 
        'name': 'name', 
        'overrated': '-votes',
        'underrated': 'votes',
        'newest': '-date',
        'oldest': 'date',
        'most_signed': '-signatures',
        'least_signed': 'signatures',
    } 

    @classmethod
    def validate(cls, choice: str, model: Model) -> str:
        if model not in cls.VALID_MODELS:
            raise TypeError(f'Model must be {cls.VALID_MODELS}')
        elif model is Animal and choice == 'title':
            choice = 'name'
        elif model is Comment and choice in ['title', 'name']:
            choice = 'newest'
        elif choice not in cls.OPTIONS_ORDER:
            choice = 'newest'
        return choice

    @classmethod
    def sort(cls, choice: str, model: Model, profile: UserProfile = None) -> tuple[str, list[Model]]:
        choice = cls.validate(choice, model)
        field = cls.OPTIONS_ORDER[choice]

        if profile:
            results = model.objects.filter(author=profile).order_by(field)
        else:
            results = model.objects.order_by(field)

        return choice, results    
    
    @classmethod
    def sort_profiles(cls, choice: str) -> tuple[str, list[Model]]:
        if choice not in ['name', 'oldest', 'newest']:
            choice = 'newest'
        
        if choice == 'name':
            results = UserProfile.objects.order_by('user__username')
        elif choice == 'newest':
            results = UserProfile.objects.order_by('-date')
        elif choice == 'oldest':
            results = UserProfile.objects.order_by('date')

        return choice, results

    @classmethod
    def sort_user_list_animals(cls, choice: str, user_list: UserList) -> tuple[str, list[Model]]:
        choice = cls.validate(choice, Animal)
        field = Sorter.OPTIONS_ORDER[choice]
        results = user_list.animals.order_by(field)
        return choice, results
    
    @classmethod
    def sort_animal_discussions(cls, choice, animal: Animal) -> tuple[str, list[Model]]:
        choice = cls.validate(choice, Discussion)
        field = cls.OPTIONS_ORDER[choice]
        results = Discussion.objects.filter(animal=animal).order_by(field)

        return choice, results    


"""------------------------------------------------------- ANIMAL VIEWS ------------------------------------------------------------"""
class AnimalView(View):
    def get(self, request, animal_name_slug):
        animal = Animal.objects.get(slug=animal_name_slug)
        sort_by = request.GET.get('sort_by')
        sort_by, discussions = Sorter.sort_animal_discussions(sort_by, animal)
        return render(request, 'wildthoughts/animal/animal.html', context={'animal': animal, 'discussions':discussions, 'sort_by': sort_by})


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
        overrated_animals = Animal.objects.order_by('-votes')[:5]
        underrated_animals = Animal.objects.order_by('votes')[:5]
        context_dict = {
            'overrated_animals': overrated_animals,
            'underrated_animals': underrated_animals
        }
        return render(request, 'wildthoughts/base/index.html', context=context_dict)
    

class SearchView(View):
    def post(self, request):
        searched = request.POST['searched']
        category = request.POST['category']

        if not searched.strip():
            searched = ''
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
            

"""------------------------------------------------------- DISCUSSION VIEWS------------------------------------------------------------"""
class DiscussionView(View):
    def get(self, request, discussion_name_slug):
        discussion = Discussion.objects.get(slug=discussion_name_slug)
        comments = Comment.objects.filter(discussion=discussion)
        return render(request, 'wildthoughts/discussion/discussion.html', context={'discussion': discussion, 'comments':comments })


class AddDiscussionView(View):
    @method_decorator(login_required)
    def get(self, request):
        animal_slug = request.GET.get('selected')
        animal_id = None
        if animal_slug:
            try:
                animal_id = Animal.objects.get(slug=animal_slug).id
            except:
                pass

        form = DiscussionForm()
        return render(request, 'wildthoughts/discussion/add_discussion.html', {'form': form, 'animal_id': animal_id})
        
    @method_decorator(login_required)
    def post(self, request):
        form = DiscussionForm(request.POST)

        if form.is_valid():
            discussion = form.save(commit=False)
            author = UserProfile.objects.get(user=request.user)
            discussion.author = author
            discussion.slug = slugify(discussion.title)
            discussion.save()
            return redirect(reverse('wildthoughts:animal', kwargs={'animal_name_slug': discussion.animal.slug}))
        else:
            print(form.errors)

        return render(request, 'wildthoughts/discussion/add_discussion.html', {'form': form})
    

class ListDiscussionView(View):
    def get(self, request):
        sort_by = request.GET.get('sort_by')
        sort_by, results = Sorter.sort(sort_by, Discussion)

        # set up pagination
        p = Paginator(results, 20)
        page = request.GET.get('page')
        discussions = p.get_page(page)
        
        return render(request, 'wildthoughts/discussion/list_discussions.html', context={'discussions': discussions, 'sort_by': sort_by})
    

"""-------------------------------------------------------- LIST VIEWS -------------------------------------------------------------"""
class UserListView(View):
    def get(self, request, user_list_slug):
        user_list = UserList.objects.get(slug=user_list_slug)
        sort_by = request.GET.get('sort_by')
        sort_by, results = Sorter.sort_user_list_animals(sort_by, user_list)
        # set up pagination
        p = Paginator(results, 20)
        page = request.GET.get('page')
        animals = p.get_page(page)
        return render(request, 'wildthoughts/user_list/user_list.html', {'user_list':user_list, 'animals':animals, 'sort_by':sort_by})
    

class ListUserListView(View):
    def get(self, request):
        sort_by = request.GET.get('sort_by')
        sort_by, results = Sorter.sort(sort_by, UserList)

        # set up pagination
        p = Paginator(results, 20)
        page = request.GET.get('page')
        user_lists = p.get_page(page)
        
        return render(request, 'wildthoughts/user_list/list_user_lists.html', context={'user_lists': user_lists, 'sort_by': sort_by})
    

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
    
"""--------------------------------------------------------- PETITION VIEWS------------------------------------------------------------"""
class PetitionView(View):
    def get(self, request, petition_slug):
        petition = Petition.objects.get(slug=petition_slug)

        # set the width of progress bar in petition page
        if petition.goal == 0:
            progress_width = 0
        else:
            progress_width = int(petition.signatures / petition.goal * 100)

        # check if user has signed petition
        has_signed = False
        if request.user.is_authenticated:
            profile = UserProfile.objects.get(user=request.user)
            if petition.signed_by.filter(id=profile.id).exists():
                has_signed = True

        context_dict = {
            'petition': petition,
            'progress_width': progress_width,
            'has_signed': has_signed
        }

        return render(request, 'wildthoughts/petition/petition.html', context=context_dict)
    

class SignPetitionView(View):
    @method_decorator(login_required)
    def get(self, request):
        petition_id = request.GET['petition_id']
        try:
            petition = Petition.objects.get(id=int(petition_id))
            profile = UserProfile.objects.get(user=request.user)
            if not petition.signed_by.filter(id=profile.id).exists():
                petition.signatures += 1
                petition.signed_by.add(profile)
                petition.save()
        except:
            return JsonResponse({'status': 'error'})
        
        return JsonResponse({'status': 'success'})
    

class ListPetitionView(View):
    def get(self, request):
        sort_by = request.GET.get('sort_by')
        sort_by, results = Sorter.sort(sort_by, Petition)

        if sort_by in ['most_signed', 'least_signed']:
            sort_by = sort_by.replace('_', ' ')

        # set up pagination
        p = Paginator(results, 20)
        page = request.GET.get('page')
        petitions = p.get_page(page)
        
        return render(request, 'wildthoughts/petition/list_petitions.html', context={'petitions': petitions, 'sort_by': sort_by})
    

class AddPetitionForm(View):
    @method_decorator(login_required)
    def get(self, request):
        form = PetitionForm()
        animals = Animal.objects.all()
        return render(request, 'wildthoughts/petition/add_petition.html', {'animals': animals, 'form': form})
    
    @method_decorator(login_required)
    def post(self, request):
        form = PetitionForm(request.POST)
        animals = Animal.objects.all()

        if form.is_valid():
            petition = form.save(commit=False)
            author = UserProfile.objects.get(user=request.user)
            petition.author = author
            petition.save()
            form.save_m2m() 
            return redirect(reverse('wildthoughts:petitions'))
        else:
            print(form.errors)

        return render(request, 'wildthoughts/petition/add_petition.html', {'animals': animals, 'form': form})
    

"""---------------------------------------------------------- PROFILE VIEWS ------------------------------------------------------"""
class ProfileView(View):
    TAB_TO_MODEL = {
        'animals': Animal,
        'discussions': Discussion,
        'comments': Comment,
        'lists': UserList,
        'petitions': Petition,
    }

    def get(self, request, username):
        profile = UserProfile.objects.get(user=User.objects.get(username=username))
        loguser = None
        if (request.user.is_authenticated):
            loguser = request.user

        tab = request.GET.get('tab')
        sort_by = request.GET.get('sort_by')
        if tab not in ProfileView.TAB_TO_MODEL:
            tab = 'animals'
        
        model = ProfileView.TAB_TO_MODEL[tab]
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

class UpdateProfileView(View):
    def get(self,request, username):
        p = Paginator(UserProfile.objects.all(), 20)
        page = request.GET.get('page')
        profiles = p.get_page(page)

        return render(request, 'wildthoughts/profile/update_profile.html', {'profiles':profiles})


"""-------------------------------------------------------- LIST VIEWS -------------------------------------------------------------"""
# (Renamed to not be confused with python list)
class UserListView(View):
    def get(self, request):
        sort_by = request.GET.get('sort_by')
        sort_by, results = Sorter.sort_profiles(sort_by)

        # set up pagination
        p = Paginator(results, 20)
        page = request.GET.get('page')
        profiles = p.get_page(page)
        context_dict = {
            'profiles': profiles,
            'sort_by': sort_by,
        }
        return render(request, 'wildthoughts/profile/list_profiles.html', context=context_dict)
