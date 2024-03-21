from django import forms
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from wildthoughts.models import Animal, Discussion, Comment, Petition, UserList, UserProfile


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
        

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label='')


class DiscussionForm(forms.ModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'animal', 'description', 'picture']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'animal': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'})
        }

    # form validation here
    def clean_title(self):
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
        self.fields['picture'].help_text = "Upload a picture for your discussion:"


class PetitionForm(forms.ModelForm):
    class Meta:
        model = Petition
        fields = ['title', 'decision_maker', 'goal', 'animals', 'description', 'picture']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'decision_maker': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'goal': forms.NumberInput(attrs={'class': 'form-control', 'min': 10}),
            'animals': forms.SelectMultiple(attrs={'class': 'form-control'})
        }
            # form validation here
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if Petition.objects.filter(title=title).exists():
            raise forms.ValidationError("A petition with this title already exists.")
        
        slug = slugify(title)
        if Petition.objects.filter(slug=slug).exists():
            raise forms.ValidationError("A petition with this title already exists.")
        
        return title
    
    # Add help text for name and description fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].help_text = "Please enter the petition title you would like to create:"
        self.fields['decision_maker'].help_text = "Please enter the name of a person or organisation able to help you implement the change you seek"
        self.fields['goal'].help_text = "Please enter the number of signatures to aim for"
        self.fields['animals'].help_text = "Please enters animals involved:"
        self.fields['description'].help_text = "Please give a brief description on the Petition:"
        self.fields['picture'].help_text = "Upload a picture for your petition:"


class UserListForm(forms.ModelForm):
    class Meta:
        model = UserList
        fields = ['title', 'animals', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'animals': forms.SelectMultiple(attrs={'class': 'form-control'})
        }

    # form validation here
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if UserList.objects.filter(title=title).exists():
            raise forms.ValidationError("A list with this title already exists.")
        
        slug = slugify(title)
        if UserList.objects.filter(slug=slug).exists():
            raise forms.ValidationError("A list with this title already exists.")
        
        return title
    
    # Add help text for name and description fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].help_text = "Please enter the list title you would like to create:"
        self.fields['animals'].help_text = "Please enters animals:"
        self.fields['description'].help_text = "Please give a brief description on the List:"


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['picture', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    # Add help text for name and description fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['picture'].help_text = "Please enter new profile picture:"
        self.fields['description'].help_text = "Please enter new bio:"