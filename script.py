import os
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'wad2_project.settings')

import django
django.setup()

from util.animal_downloader import AnimalDownloader
from util.database import Database
from util.file_manager import FileManager
from util.profile_downloader import ProfileDownloader


class Script:
    # class dedicated to read cli args and run methods
    @classmethod
    def read_args(cls) -> tuple[str, int]:
        actions = {
            'download': 'Download animals and profiles',
            'cleardatabase': 'Clear the database and the files in migrations',
            'clear': 'Clear the database, the files in migrations and media',
            'populate': 'Populate the database',
            'migrate': 'Migrate the database',
            'database': 'Populate and migrate the database',
            'all': 'Perform all actions'
        }
        count = 50

        if len(sys.argv) <= 1 or sys.argv[1] not in actions:
            print(f'Usage: action={list(actions.keys())} count\n')
            for action, description in actions.items():
                print(f"{action}: {description}")
            print('\ncount: optional argument. Number of animals and profiles to download. Defaults to 50')
            sys.exit(1)

        if len(sys.argv) > 2:
            if sys.argv[2].isdigit():
                count = int(sys.argv[2])
                if count <= 50:
                    print('count must be an integer greater than 50')
                    sys.exit(1)

        return sys.argv[1], count

    @classmethod
    def execute(cls, action: str, count: int) -> None:
        if action == 'download':
            ProfileDownloader.download(count)
            AnimalDownloader.download(count)

        elif action == 'cleardatabase':
            FileManager.clear(Database)
            Database.migrate()

        elif action == 'clear':
            FileManager.clear_all() 
            Database.migrate()

        elif action == 'migrate':
            Database.migrate()

        elif action == 'populate':
            Database.populate()

        elif action == 'database':
            Database.migrate()
            Database.populate()
        
        elif action == 'all':
            FileManager.clear_all()

            animal_dict = AnimalDownloader.download(count)
            profile_dict = ProfileDownloader.download(count)

            Database.animal_dict = animal_dict
            Database.profile_dict = profile_dict
            Database.migrate()
            Database.populate()

    @classmethod
    def run(cls) -> None:
        action, count = cls.read_args()
        try:
            FileManager.validate_working_directory()
            cls.execute(action, count)
        except:
            traceback.print_exc()
            with open('traceback.txt', 'w') as f:
                traceback.print_exc(None, f, True)
                print("\nTraceback saved. Please upload it to Teams if you can't solve the issue.")


if __name__ == '__main__':
    Script.run()