from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from wildthoughts.models import Animal, Discussion, Petition, UserList, UserProfile

# Create your tests here.
# Models
class AnimalMethodTests(TestCase):
    def setUp(self):
        user = User.objects.create(username='testuser')
        profile = UserProfile.objects.create(user=user)
        self.animal, created = Animal.objects.get_or_create(
            name='Lion',
            author=profile,
            description="The king of the jungle!",
        )

    def test_slug(self):
        self.assertEqual(self.animal.slug, slugify("Lion"))


class UserListMethodTests(TestCase):
    def setUp(self):
        user = User.objects.create(username='testuser')
        self.profile = UserProfile.objects.create(user=user)
        self.user_list = UserList.objects.create(
                title='My favorite animals',
                author=self.profile,
                )

    def test_slug(self):
        self.assertEqual(self.user_list.slug, slugify("My favorite animals"))
            

class DiscussionMethodTests(TestCase):
    def setUp(self):
        user = User.objects.create(username='testuser')
        profile = UserProfile.objects.create(user=user)
        animal, created = Animal.objects.get_or_create(
            name='Lion',
            author=profile,
        )
        self.discussion, created = Discussion.objects.get_or_create(
            title='Discussion about Lions',
            author=profile,
            animal=animal,
        )

    def test_slug(self):
        self.assertEqual(self.discussion.slug, slugify("Discussion about Lions"))


class PetitionMethodTests(TestCase):
    def setUp(self):
        user = User.objects.create(username='testuser')
        profile = UserProfile.objects.create(user=user)
        self.petition, created = Petition.objects.get_or_create(
            title=f'Petition for Animal',
            author=profile,
            description="This animal is at the risk of extinction!",
        )
    
    def test_signatures_less_than_goal(self):
        self.petition.goal = 100
        self.petition.signatures = 101
        with self.assertRaises(ValidationError):
            self.petition.save()

    def test_signatures_are_positive(self):
        self.petition.signatures = -100
        with self.assertRaises(ValidationError):
            self.petition.save()

    def test_goals_are_positive(self):
        self.petition.goal = -100
        with self.assertRaises(ValidationError):
            self.petition.save()

    def test_slug(self):
        self.assertEqual(self.petition.slug, slugify("Petition for Animal"))
                         

# Views
class IndexViewTests(TestCase):
    def test_view_with_no_animals(self):
        response = self.client.get(reverse('wildthoughts:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no animals yet...')
        self.assertQuerysetEqual(response.context['animals'], [])


class AnimalViewTests(TestCase):
    def setUp(self):
        user = User.objects.create(username='testuser')
        profile = UserProfile.objects.create(user=user)
        self.animal, created = Animal.objects.get_or_create(
            name='Lion',
            author=profile,
            description="The king of the jungle!",
        )

    def test_index_view_with_no_discussions(self):
        response = self.client.get(reverse('wildthoughts:animal', kwargs={'animal_name_slug': self.animal.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no discussions yet...')
        self.assertQuerysetEqual(response.context['discussions'], [])


class ListAnimalsViewTests(TestCase):
    def test_view_with_no_animals(self):
        response = self.client.get(reverse('wildthoughts:animals'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no animals yet...')
        self.assertQuerysetEqual(response.context['animals'], [])


class ListDiscussionsViewTests(TestCase):
    def test_view_with_no_discussions(self):
        response = self.client.get(reverse('wildthoughts:discussions'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no discussions yet...')
        self.assertQuerysetEqual(response.context['discussions'], [])


class ListPetitionsViewTests(TestCase):
    def test_view_with_no_petitions(self):
        response = self.client.get(reverse('wildthoughts:petitions'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no petitions yet...')
        self.assertQuerysetEqual(response.context['petitions'], [])


class ProfileViewTests(TestCase):
    def setUp(self):
        user = User.objects.create(username='testuser')
        self.profile = UserProfile.objects.create(user=user)

    def test_view_with_no_animals(self):
        response = self.client.get(reverse('wildthoughts:profile', kwargs={'username': self.profile.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no animals yet...')
        self.assertQuerysetEqual(response.context['animals'], [])


class ListProfileViewTests(TestCase):
    def test_view_with_no_profiles(self):
        response = self.client.get(reverse('wildthoughts:profiles'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no profiles yet...')
        self.assertQuerysetEqual(response.context['profiles'], [])