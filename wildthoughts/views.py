from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
#from wildthoughts.forms import UserForm, UserProfileForm

from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views import View
from wildthoughts.forms import AnimalForm

from wildthoughts.models import Animal, Discussion, UserList, UserProfile


class IndexView(View):
    def get(self, request):
        overrated_animals = Animal.objects.order_by('-upvotes')[:5]
        underrated_animals = Animal.objects.order_by('-downvotes')[:5]
        context_dict = {
            'overrated_animals': overrated_animals,
            'underrated_animals': underrated_animals
        }
        return render(request, 'wildthoughts/base/index.html', context=context_dict)
    

class AnimalView(View):
    def get(self, request, animal_name_slug):
        animal = Animal.objects.get(slug=animal_name_slug)
        return render(request, 'wildthoughts/animal/animal.html', context={'animal': animal})
    

class ListAnimalsView(View):
    def get(self, request):
        # set up pagination
        p = Paginator(Animal.objects.all(), 20)
        page = request.GET.get('page')
        animals = p.get_page(page)
        return render(request, 'wildthoughts/animal/list_animals.html', {'animals':animals})
    

class ListProfileView(View):
    def get(self, request):
        # set up pagination
        p = Paginator(UserProfile.objects.all(), 20)
        page = request.GET.get('page')
        profiles = p.get_page(page)
        return render(request, 'wildthoughts/profile/list_profiles.html', {'profiles':profiles})
    

class SearchView(View):
    def post(self, request):
        searched = request.POST['searched']
        category = request.POST['category']
        results = []
        if category == 'Animals':
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


@login_required
def addAnimalView(request):
    form = AnimalForm()
    
    if request.method=='POST':
        form = AnimalForm(request.POST)
    
        if form.is_valid():
            form.save(commit=True)
            return redirect('/wildthoughts/')
        else:
            print(form.errors)
    
    return render(request, 'wildthoughts/add_animal.html', {'form': form})
    