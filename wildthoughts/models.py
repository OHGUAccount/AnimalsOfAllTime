from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    description = models.TextField(blank=True)
    

    def __str__(self):
        return self.user.username
    

class Animal(models.Model):
    """
    Django automatically creates a “reverse” relation on the related model and gives it a name.
    When two relationships like author and upvoted_by point to the same model related_name
    must be added to avoid naming conflicts.
    """
    # ehen two relationships point to the same model like author and  
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='authored_animals')
    name = models.CharField(max_length= 128, unique=True)
    description = models.TextField(blank=True)
    picture = models.ImageField(upload_to='animal_images', blank=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    upvoted_by = models.ManyToManyField(UserProfile, related_name='upvoted_animals')
    downvotes_by = models.ManyToManyField(UserProfile, related_name='downvoted_animals')
    date = models.DateField(auto_now_add=True)
    slug = models.SlugField(unique=True)

    @property
    def total_votes(self):
        return self.upvotes - self.downvotes

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
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    upvoted_by = models.ManyToManyField(UserProfile, related_name='upvoted_discussions')
    downvotes_by = models.ManyToManyField(UserProfile, related_name='downvoted_discussions')
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
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    upvoted_by = models.ManyToManyField(UserProfile, related_name='upvoted_comments')
    downvotes_by = models.ManyToManyField(UserProfile, related_name='downvoted_comments')

    def __str__(self):
        return self.content
    

class UserList(models.Model):
    title = models.CharField(max_length=128)
    date = models.DateField(auto_now_add=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='authored_user_lists')
    animals = models.ManyToManyField(Animal)
    description = models.TextField(blank=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    upvoted_by = models.ManyToManyField(UserProfile, related_name='upvoted_user_lists')
    downvotes_by = models.ManyToManyField(UserProfile, related_name='downvoted_user_lists')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(UserList, self).save(*args, **kwargs)