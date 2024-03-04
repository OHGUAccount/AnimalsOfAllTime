from django import forms
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from wildthoughts.models import UserProfile,Animal,Discussion,Comment,UserList

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['name', 'description', 'picture']

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
        self.fields['name'].help_text = "Please enter the Animal page name!"
        self.fields['description'].help_text = "Please give a brief description on the Animal."
        self.fields['picture'].help_text = "Upload a picture of your added animal!"



       