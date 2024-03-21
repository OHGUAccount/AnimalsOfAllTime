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

from wildthoughts.forms import AnimalForm, CommentForm, DiscussionForm, EditProfileForm, UserListForm, PetitionForm
from wildthoughts.models import Animal, Comment, Discussion, Petition, UserList, UserProfile


"""--------------------------------------------------------HELPER CLASSES -------------------------------------------------------------"""
class Sorter:
    """
    class dedicated to sort a model by specifying a option
    the option is then converted to an appropriate field
    if option is invalid returns model sorted by date
    """
    VALID_MODELS = {Animal, Comment, Discussion, Petition, UserList}
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
    def sort_model(cls, choice: str, model: Model, profile: UserProfile = None) -> tuple[str, list[Model]]:
    
        choice = cls.validate(choice, model)
        field = cls.OPTIONS_ORDER[choice]

        if profile:
            # filter by a profile instance if specified
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
    
    @classmethod
    def sort_discussion_comments(cls, choice, discussion: Discussion) -> tuple[str, list[Model]]:
        choice = cls.validate(choice, Comment)
        field = cls.OPTIONS_ORDER[choice]
        results = Comment.objects.filter(discussion=discussion).order_by(field)

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
    """
    return Animals model sorted by parameter sort_by
    and set up pagination

    Resources used:
     Codemy.com, Pagination: https://youtu.be/N-PB-HMFmdo?si=JFQX6OpyVV6fLJqR
    """
    def get(self, request):
        sort_by = request.GET.get('sort_by')
        sort_by, results = Sorter.sort_model(sort_by, Animal)
        p = Paginator(results, 20)
        page = request.GET.get('page')
        animals = p.get_page(page)
        return render(request, 'wildthoughts/animal/list_animals.html', {'animals':animals, 'sort_by':sort_by})
    

"""------------------------------------------------------------ BASE VIEWS------------------------------------------------------------"""
# Views at the core of our applications, usually shared between multiple pages/templates
class IndexView(View):
    def get(self, request):
        overrated_animals = Animal.objects.order_by('votes')[:5]
        underrated_animals = Animal.objects.order_by('-votes')[:5]
        context_dict = {
            'overrated_animals': overrated_animals,
            'underrated_animals': underrated_animals
        }
        return render(request, 'wildthoughts/base/index.html', context=context_dict)
    

class SearchView(View):
    # Codemy.com, Search: https://youtu.be/AGtae4L5BbI?si=KSDHD2XQh5S6YceP
    def get(self, request):
        searched = request.GET.get('searched')
        category = request.GET.get('category')

        if not searched.strip():
            searched = ''
            results = None
        elif category == 'Animals':
            results = Animal.objects.filter(name__contains=searched)
        elif category == 'Discussions':
            results = Discussion.objects.filter(title__contains=searched)
        elif category == 'Lists':
            results = UserList.objects.filter(title__contains=searched)
        elif category == 'Petitions':
            results = Petition.objects.filter(title__contains=searched)
        elif category == 'Profiles':
            results = UserProfile.objects.filter(user__username__contains=searched)
        context_dict = {
            'searched': searched,
            'category': category,
            'results': results
        }
        
        return render(request, 'wildthoughts/base/search.html', context=context_dict)


class ThemeView(View):
    """
    set the cookie for theme which is then used
    to assign the value for attrbute data-bs-theme in <html>
    https://getbootstrap.com/docs/5.3/customize/color-modes/#adding-theme-colors

    see:
    templatetags/wildthoughts theme() for retrieving theme from cookie, used in base/base.html
    static/js/theme for client side
    """
    def get(self, request):
        theme = request.GET.get('theme')
        if theme in ['dark', 'light']:
            response = HttpResponse("Theme set to: " + theme)
            response.set_cookie('theme', theme)
            return response
        else:
            return HttpResponse(-1)
        

class VoteView(View):
    """
    retrieve the category and id form an ajax request
    and update the vote

    see:
    templatetags/wildthoughts render_vote() for rendering vote in templates
    static/js/vote for client side
    """
    def update_upvote(self, profile, instance):
        if not instance.upvoted_by.filter(id=profile.id).exists():
            instance.upvoted_by.add(profile)
            instance.votes += 1

        if instance.downvoted_by.filter(id=profile.id).exists():
            instance.votes += 1
            instance.downvoted_by.remove(profile)
            
        instance.save()

    def update_downvote(self, profile, instance):
        if instance.upvoted_by.filter(id=profile.id).exists():
            instance.upvoted_by.remove(profile)
            instance.votes -= 1

        if not instance.downvoted_by.filter(id=profile.id).exists():
            instance.votes -= 1
            instance.downvoted_by.add(profile)

        instance.save()

    def update_upvoted(self, profile, instance):
        if instance.upvoted_by.filter(id=profile.id).exists():
            instance.upvoted_by.remove(profile)
            instance.votes -= 1

        instance.save()

    def update_downvoted(self, profile, instance):
        if instance.downvoted_by.filter(id=profile.id).exists():
            instance.downvoted_by.remove(profile)
            instance.votes += 1

        instance.save()

    def update_vote(self, profile, instance, status):            
        if status == 'upvote':
            self.update_upvote(profile, instance)

        elif status == 'downvote':
            self.update_downvote(profile, instance)

        elif status == 'upvoted':
            self.update_upvoted(profile, instance)

        elif status == 'downvoted':
            self.update_downvoted(profile, instance)

    def get(self, request):
        category = request.GET.get('category')
        id = request.GET.get('id')
        status = request.GET.get('status')
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                model = ProfileView.TAB_TO_MODEL[category]
                instance = model.objects.get(id=int(id))
                self.update_vote(profile, instance, status)
                return JsonResponse({'status': 'success', 'count': instance.votes})
            except Exception as e:
                print(e)
                return JsonResponse({'status': 'error'})    
        else:
            login_url = reverse('auth_login')
            return JsonResponse({'status': 'login', 'login_url': login_url})    
        

"""------------------------------------------------------- DISCUSSION VIEWS------------------------------------------------------------"""
class DiscussionView(View):
    def get(self, request, discussion_slug):
        sort_by = request.GET.get('sort_by')
        discussion = Discussion.objects.get(slug=discussion_slug)
        sort_by, comments = Sorter.sort_discussion_comments(sort_by, discussion)
        form = CommentForm()

        context_dict = {
            'discussion': discussion,
            'comments':comments,
            'sort_by': sort_by,
            'form': form
        }

        return render(request, 'wildthoughts/discussion/discussion.html', context=context_dict)
    
    @method_decorator(login_required)
    def post(self, request, discussion_slug):
        form = CommentForm(request.POST)        
        sort_by = request.GET.get('sort_by', 'newest')

        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = UserProfile.objects.get(user=request.user)
            comment.discussion = Discussion.objects.get(slug=discussion_slug)
            comment.save()

        return redirect(reverse('wildthoughts:discussion', kwargs={'discussion_slug': discussion_slug}) + '?sort_by=' + sort_by)


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
        form = DiscussionForm(request.POST, request.FILES)

        if form.is_valid():
            discussion = form.save(commit=False)
            author = UserProfile.objects.get(user=request.user)
            discussion.author = author
            discussion.slug = slugify(discussion.title)
            discussion.save()
            return redirect(reverse('wildthoughts:discussion', kwargs={'discussion_slug': discussion.slug}))
        else:
            print(form.errors)

        return render(request, 'wildthoughts/discussion/add_discussion.html', {'form': form})
    

class ListDiscussionView(View):
    def get(self, request):
        sort_by = request.GET.get('sort_by')
        sort_by, results = Sorter.sort_model(sort_by, Discussion)

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
        sort_by, results = Sorter.sort_model(sort_by, UserList)

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
            return redirect(reverse('wildthoughts:list', kwargs={'user_list_slug': user_list.slug}))
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
    def get(self, request):
        petition_id = request.GET['petition_id']
        if request.user.is_authenticated:
            try:
                petition = Petition.objects.get(id=int(petition_id))
                profile = UserProfile.objects.get(user=request.user)
                if not petition.signed_by.filter(id=profile.id).exists():
                    petition.signatures += 1
                    petition.signed_by.add(profile)
                    petition.save()
                    return JsonResponse({'status': 'success'})
            except Exception as e:
                print(e)
                return JsonResponse({'status': 'error'})
        else:
            login_url = reverse('auth_login')
            return JsonResponse({'status': 'login', 'login_url': login_url})         
    

class ListPetitionView(View):
    def get(self, request):
        sort_by = request.GET.get('sort_by')
        sort_by, results = Sorter.sort_model(sort_by, Petition)

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
        form = PetitionForm(request.POST, request.FILES)
        animals = Animal.objects.all()

        if form.is_valid():
            petition = form.save(commit=False)
            author = UserProfile.objects.get(user=request.user)
            petition.author = author
            petition.save()
            form.save_m2m() 
            return redirect(reverse('wildthoughts:petition', kwargs={'petition_slug': petition.slug}))
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
        sort_by, results = Sorter.sort_model(sort_by, model, profile)
        
        if sort_by in ['most_signed', 'least_signed']:
            sort_by = sort_by.replace('_', ' ')

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
        sort_by = request.GET.get('sort_by')
        sort_by, results = Sorter.sort_profiles(sort_by)
        # set up pagination
        p = Paginator(results, 20)
        page = request.GET.get('page')
        profiles = p.get_page(page)

        return render(request, 'wildthoughts/profile/list_profiles.html', {'profiles':profiles, 'sort_by':sort_by})


class EditProfileView(View):
    @method_decorator(login_required)
    def get(self, request):
        profile = UserProfile.objects.get(user=request.user)
        form = EditProfileForm(instance=profile)
        return render(request, 'wildthoughts/profile/edit_profile.html', {'form': form})
    
    @method_decorator(login_required)
    def post(self, request):
        profile = UserProfile.objects.get(user=request.user)
        form = EditProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            profile = form.save()
            
            updated_username = form.cleaned_data['name']
            return redirect(reverse('wildthoughts:profile', kwargs={'username': profile.user.username}))
        else:
            print(form.errors)

        return render(request, 'wildthoughts/profile/edit_profile.html', {'form': form})



