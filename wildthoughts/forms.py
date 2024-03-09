from django import forms
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from wildthoughts.models import UserProfile, Animal, Discussion, Comment, UserList
from select2 import forms as select2forms


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['name', 'description', 'picture']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'})
        }

    # form validation here
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Animal.objects.filter(name=name).exists():
            raise forms.ValidationError("An animal with this name already exists.")
        
        slug = slugify(name)
        if Animal.objects.filter(slug=slug).exists():
            raise forms.ValidationError("An animal with this name already exists.")
        
        return name
    
    # Add help text for name and description fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].help_text = "Please enter the Animal page name:"
        self.fields['description'].help_text = "Please give a brief description on the Animal:"
        self.fields['picture'].help_text = "Upload a picture of your added animal:"
        

class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'animal', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'animal': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'})
        }

    # form validation here
    def clean_name(self):
        title = self.cleaned_data.get('title')
        if Discussion.objects.filter(title=title).exists():
            raise forms.ValidationError("A discussion with this title already exists.")
        
        slug = slugify(title)
        if Discussion.objects.filter(slug=slug).exists():
            raise forms.ValidationError("A discussion with this title already exists.")
        
        return title
    
    # Add help text for name and description fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].help_text = "Please enter the Discussion title you would like to create:"
        self.fields['animal'].help_text = "Please select Animal:"
        self.fields['description'].help_text = "Please give a brief description on the Discussion:"


class UserListForm(forms.ModelForm):
    class Meta:
        model = UserList
        fields = ['title', 'animals', 'description']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'animals': select2forms.SelectMultiple(attrs={'data-placeholder': 'Please select Animals',
                                                          'style': '"width: 100%"'})
        }