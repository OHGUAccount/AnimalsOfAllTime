from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views import View

from animals_of_all_time.models import Animal, UserProfile


class IndexView(View):
    def get(self, request):
        overrated_animals = Animal.objects.order_by('-upvotes')[:5]
        underrated_animals = Animal.objects.order_by('-downvotes')[:5]
        context_dict = {
            'overrated_animals': overrated_animals,
            'underrated_animals': underrated_animals
        }
        return render(request, 'animals_of_all_time/index.html', context=context_dict)
    

class AnimalView(View):
    def get(self, request, animal_name_slug):
        animal = Animal.objects.get(slug=animal_name_slug)
        return render(request, 'animals_of_all_time/animal/animal.html', context={'animal': animal})
    

class ListAnimalsView(View):
    def get(self, request):
        # set up pagination
        p = Paginator(Animal.objects.all(), 20)
        page = request.GET.get('page')
        animals = p.get_page(page)
        return render(request, 'animals_of_all_time/animal/list_animals.html', {'animals':animals})
    

class ListProfileView(View):
    def get(self, request):
        # set up pagination
        p = Paginator(UserProfile.objects.all(), 20)
        page = request.GET.get('page')
        profiles = p.get_page(page)
        return render(request, 'animals_of_all_time/profile/list_profiles.html', {'profiles':profiles})
    