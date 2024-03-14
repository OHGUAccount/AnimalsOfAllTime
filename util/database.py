import json
import os
import random
import shutil

from django.contrib.auth.models import User
from django.core.management import execute_from_command_line
from django.utils.text import slugify

from wildthoughts.models import Animal, Discussion, Petition, UserList, UserProfile


class Database:
    # class dedicated to populate and migrate database
    animal_dict: dict = None
    profile_dict: dict = None
    adjectives = ['scariest', 'gorgeous', 'fastest', 'slowest']
    animals: list[Animal] = None
    users: list[UserProfile] = None

    @classmethod
    def clear(cls) -> None:
        # remove db.sqlite3 and files in migrations
        if os.path.exists("db.sqlite3"):
            os.remove("db.sqlite3")

        init_path = os.path.join("wildthoughts\\migrations", '__init__.py')
        for item in os.listdir("wildthoughts\\migrations"):
            item_path = os.path.join("wildthoughts\\migrations", item)
            if item_path == init_path:
                continue
            elif os.path.isfile(item_path):
                os.remove(item_path)
            else:
                shutil.rmtree(item_path)

        cls.migrate()

    @classmethod
    def load_profile_dict(cls) -> dict:
        if not cls.profile_dict:
            with open("profile.json", "r") as f:
                cls.profile_dict = json.load(f)
        return cls.profile_dict

    @classmethod
    def load_animal_dict(cls) -> dict:
        if not cls.animal_dict:
            with open("animal.json", "r") as f:
                cls.animal_dict = json.load(f)
        return cls.animal_dict

    @classmethod
    def load_author(cls) -> UserProfile:
        author, created = User.objects.get_or_create(
            username='animalcorner',
            email='animalcorner@gmail.com',
            password='WAD2Test2024',
        )
        author, created = UserProfile.objects.get_or_create(user=author)
        return author
    
    @classmethod
    def add_users(cls) -> None:
        profile_dict = cls.load_profile_dict()
        for username, data in profile_dict.items():
            user, created = User.objects.get_or_create(
                username = username,
                email = data['email'],
                password = data['password'],
            )

            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.picture = data['image_path']
            user_profile.save()

    @classmethod
    def add_animals(cls) -> None:
        animal_dict = cls.load_animal_dict()
        author = cls.load_author()
        for name, data in animal_dict.items():
            animal, created = Animal.objects.get_or_create(
                name=name,
                author=author,
                slug=slugify(name)
            )
            animal.description = data['description']
            animal.picture = data['image_path']
            animal.votes = random.randint(1, 100)
            animal.save()

    @classmethod
    def random_animal(cls) -> Animal:
        if cls.animals is None:
            cls.animals = Animal.objects.all()
        return cls.animals.order_by('?').first()

    @classmethod
    def random_user(cls) -> UserProfile:
        if cls.users is None:
            cls.users = UserProfile.objects.all()
        return cls.users.order_by('?').first()

    @classmethod
    def random_zip(cls, size=5) -> tuple[tuple[UserProfile, Animal]]:
        users = [cls.random_user() for i in range(size)]
        animals = [cls.random_animal() for i in range(size)]
        return zip(users, animals)

    @classmethod
    def add_discussions(cls) -> None:
        for user, animal in cls.random_zip():
            discussion, created = Discussion.objects.get_or_create(
                title=f"Why do you like {animal.name} by {user.user.username}?",
                author=user,
                animal=animal,
                slug=slugify(f"Why do you like {animal.name} by {user.user.username}?")
            )

    @classmethod
    def add_user_lists(cls) -> None:
        users = [cls.random_user() for i in range(5)]
        animals = [cls.random_animal() for i in range(5)]
        for user in users:
            adjective = random.choice(cls.adjectives)
            user_list, created = UserList.objects.get_or_create(
                title=f'Top {adjective} animals by {user.user.username}',
                author=user,
                slug=slugify(f'Top {adjective} animals by {user.user.username}')
            )
            for animal in animals:
              user_list.animals.add(animal)

            user_list.save()

    @classmethod
    def add_petitions(cls) -> None:
        for user, animal in cls.random_zip():
            petition, created = Petition.objects.get_or_create(
                title=f'Petition for {animal.name} by {user.user.username}',
                author=user,
                picture=animal.picture,
                description="This animal is at the risk of extinction!",
                slug=slugify(f'Petition for {animal.name} by {user.user.username}')
            )
            petition.goal = 100
            petition.signatures = random.randint(0, 100)
            petition.animals.add(animal)
            petition.save()

    @classmethod
    def populate(cls) -> None:
        cls.add_animals()
        cls.add_users()
        cls.add_discussions()
        cls.add_user_lists()
        cls.add_petitions()
        
    @classmethod
    def migrate(cls) -> None:
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])