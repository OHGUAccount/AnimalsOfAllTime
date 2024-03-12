import argparse
import concurrent.futures
import json
import os
import random
import requests
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'wad2_project.settings')

import django
django.setup()
from django.contrib.auth.models import User
from django.core.management import execute_from_command_line
from django.utils.text import slugify

from bs4 import BeautifulSoup
from PIL import Image
from wildthoughts.models import Animal, Discussion, Petition, UserList, UserProfile


class ImageProfile:
    # class dedicated to create image profiles with random colours using pillow
    colours = ['blue', 'green', 'red', 'yellow']

    @classmethod
    def create_colour(cls, colour: str, width=300, height=300) -> None:
        image = Image.new('RGB', (width, height), colour)
        image.save(f'media\\profile_images\\{colour}.png')

    @classmethod
    def create_multi_colours(cls, colours: list[str] = None, width=300, height=300):
        if not colours:
            colours = cls.colours
        for colour in colours:
            cls.create_colour(colour, width, height)

    @classmethod
    def exist_colour(cls, colour: str, create=False) -> str:
        exist = os.path.exists(f'media\\profile_images\\{colour}.png')
        if not exist and create:
            cls.create_colour(colour)
            exist = os.path.exists(f'media\\profile_images\\{colour}.png')
            
        if exist:
            return f'profile_images\\{colour}.png'
    
    @classmethod
    def exist_multi_colours(cls, colours: list[str] = None, create=False) -> dict[str, bool]:
        if not colours:
            colours = cls.colours
        output_dict = {}
        for colour in colours:
            output_dict[colour] = cls.exist_colour(colour, create)
        return output_dict
    
    @classmethod
    def random_colour(cls, colours: list[str] = None) -> tuple[str, str]:
        if not colours:
            colours = cls.colours
        colour = random.choice(colours)
        return colour, cls.exist_colour(colour, create=True)


class AnimalDownloader:
    """
    class dedicated to webscrape https://animalcorner.org/animals/
    using BeautifulSoup and dividing the workload between threads
    only download method should be used

    Resources used:
    freeCodeCamp.org: https://youtu.be/XVv6mJpFOb0?si=cY__8rXOFzQ5jdzv
    John Watson Rooney: https://youtu.be/aA6-ezS5dyY?si=SB2rH5OACNMdiSlX
    stackoverflow: https://stackoverflow.com/questions/13137817/how-to-download-image-using-requests
    """
    @classmethod
    def __find_urls(cls) -> list[str]:
        """
        extracts all urls from the page and returns them as a list
        """
        urls = []
        html_file = requests.get('https://animalcorner.org/animals/').text
        soup = BeautifulSoup(html_file, 'lxml')
        a = soup.find_all('a')
        for link in a: 
            href = link.get('href')
            if 'animals' in href:
                urls.append(href)
        return urls
    
    @classmethod
    def __reduce_size(cls, urls: list[str], count: int) -> list[str]:
        """
        reduce the size of the list of url to a specified number
        note that it won't exactly download the specified number of animals 
        since validation is done at execution
        """
        end = min(len(urls), count) - 1
        return urls[:end]

    @classmethod
    def __get_name(cls, soup: BeautifulSoup) -> str:
        return soup.title.string.split('-')[0].strip()

    @classmethod
    def __get_description(cls, soup: BeautifulSoup) -> str:
        div = soup.find('div', class_ = 'entry-content')
        return div.find('p').text

    @classmethod
    def __save_image(cls, soup: BeautifulSoup) -> str:
        div = soup.find('div', class_="featured-image-wrapper")
        img_tag = div.find('img')
        img_url = img_tag.get('data-breeze')
        with requests.get(img_url, stream=True) as response:
            filename = os.path.join('media\\animal_images', os.path.basename(img_url))
            with open(filename, 'wb') as out_file:
                out_file.write(response.content)
            img_path = os.path.join('animal_images', os.path.basename(img_url))
            return img_path

    @classmethod
    def __get_data(cls, url: list[str]) -> tuple[str, str, str]:
        try:
            html_file = requests.get(url).text
            soup = BeautifulSoup(html_file, 'lxml')
            name = cls.__get_name(soup)
            description = cls.__get_description(soup)
            if name and description:
                image_path = cls.__save_image(soup)
                if image_path:
                    return name, description, image_path
        except:
            pass
        
    @classmethod
    def download(cls, count=50) -> dict[str, dict[str, str]]:
        output_dict = {}
        urls = cls.__find_urls()
        urls = cls.__reduce_size(urls, count)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(cls.__get_data, url) for url in urls]

            for future in concurrent.futures.as_completed(futures):
                result = future.result() 
                if result is not None:
                    name, description, image_path = result
                    output_dict[name] = {
                        'description' : description,
                        'image_path' : image_path
                    }

        with open("animal.json", "w") as f:
            json.dump(output_dict, f, indent=2)
        return output_dict


class Database:
    # class dedicated to populate and migrate database
    animal_dict: dict = None
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
        for num in range(100):
            user, created = User.objects.get_or_create(
                username = f'test{num}',
                email = f'test{num}@gmail.com',
                password = 'WAD2Test2024',
            )
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            colour, image_path = ImageProfile.random_colour()
            user_profile.picture = image_path
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
                goal=200,
                signatures=random.randint(0, 100),
                slug=slugify(f'Petition for {animal.name}')
            )
            petition.animals.add(animal)

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


class Script:
    # class dedicated to read cli args and run methods
    @classmethod
    def read_args(cls):
        parser = argparse.ArgumentParser()
        actions = ['download', 'clear', 'populate', 'migrate', 'database', 'all']
        parser.add_argument('action', choices=actions)
        args = parser.parse_args()
        return args.action

    @classmethod
    def execute(cls, action):
        if action == 'download':
            AnimalDownloader.download()

        elif action == 'clear':
            Database.clear()

        elif action == 'populate':
            Database.populate()

        elif action == 'migrate':
            Database.migrate()

        elif action == 'database':
            Database.populate()
            Database.migrate()
        
        elif action == 'all':
            animal_dict = AnimalDownloader.download()
            Database.animal_dict = animal_dict
            Database.populate()
            Database.migrate()

    @classmethod
    def run(cls):
        action = cls.read_args()
        cls.execute(action)


if __name__ == '__main__':
    Script.run()