from django.contrib.auth.models import User
from django.db import models
from django.forms import ValidationError
from django.template.defaultfilters import slugify
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.user.username
    

class Animal(models.Model):
    """
    Django automatically creates a “reverse” relation on the related model and gives it a name.
    When two relationships like author and upvoted_by point to the same model related_name
    must be added to avoid naming conflicts.
    """
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='authored_animals')
    name = models.CharField(max_length= 128, unique=True)
    description = models.TextField(blank=True)
    picture = models.ImageField(upload_to='animal_images', blank=True)
    votes = models.IntegerField(default=0)
    upvoted_by = models.ManyToManyField(UserProfile, related_name='upvoted_animals')
    downvoted_by = models.ManyToManyField(UserProfile, related_name='downvoted_animals')
    date = models.DateField(auto_now_add=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Animal, self).save(*args, **kwargs)


class Discussion(models.Model):
    title = models.CharField(max_length=128)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='authored_discussions')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)
    picture = models.ImageField(upload_to='discussion_images', blank=True)
    votes = models.IntegerField(default=0)
    upvoted_by = models.ManyToManyField(UserProfile, related_name='upvoted_discussions')
    downvoted_by = models.ManyToManyField(UserProfile, related_name='downvoted_discussions')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Discussion, self).save(*args, **kwargs)


class Comment(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='authored_comments')
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateField(auto_now_add=True)
    votes = models.IntegerField(default=0)
    upvoted_by = models.ManyToManyField(UserProfile, related_name='upvoted_comments')
    downvoted_by = models.ManyToManyField(UserProfile, related_name='downvoted_comments')

    def __str__(self):
        return self.content
    

class Petition(models.Model):
    title = models.CharField(max_length=128)
    date = models.DateField(auto_now_add=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='authored_petitions')
    animals = models.ManyToManyField(Animal, blank=True)
    picture = models.ImageField(upload_to='petition_images', blank=True)
    description = models.TextField(blank=True)
    decision_maker = models.CharField(max_length=128, blank=True)
    goal = models.IntegerField(default=10)
    signatures = models.IntegerField(default=0)
    signed_by = models.ManyToManyField(UserProfile, related_name='signed_petitions')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.signatures < 0:
            raise ValidationError("Signatures cannot be negative")
        if self.goal < 0:
            raise ValidationError("Goal cannot be negative")
        if self.signatures > self.goal:
            raise ValidationError("Signatures cannot be greater than goal")
        self.slug = slugify(self.title)
        super(Petition, self).save(*args, **kwargs)
        
        
class UserList(models.Model):
    title = models.CharField(max_length=128)
    date = models.DateField(auto_now_add=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='authored_user_lists')
    animals = models.ManyToManyField(Animal)
    description = models.TextField(blank=True)
    votes = models.IntegerField(default=0)
    upvoted_by = models.ManyToManyField(UserProfile, related_name='upvoted_user_lists')
    downvoted_by = models.ManyToManyField(UserProfile, related_name='downvoted_user_lists')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(UserList, self).save(*args, **kwargs)