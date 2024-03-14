import argparse
import os
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'wad2_project.settings')

import django
django.setup()

from util.animal_downloader import AnimalDownloader
from util.database import Database
from util.profile_downloader import ProfileDownloader


class Script:
    # class dedicated to read cli args and run methods
    @classmethod
    def read_args(cls):
        parser = argparse.ArgumentParser()
        actions = ['download', 'clear', 'cleardatabase', 'populate', 'migrate', 'database', 'all']
        parser.add_argument('action', choices=actions)
        args = parser.parse_args()
        return args.action

    @classmethod
    def execute(cls, action):
        if action == 'download':
            ProfileDownloader.download()
            AnimalDownloader.download()

        elif action == 'cleardatabase':
            Database.clear()

        elif action == 'clear':
            Database.clear()
            ProfileDownloader.clear()
            AnimalDownloader.clear()

        elif action == 'populate':
            Database.populate()

        elif action == 'migrate':
            Database.migrate()

        elif action == 'database':
            Database.populate()
            Database.migrate()
        
        elif action == 'all':
            Database.clear()
            ProfileDownloader.clear()
            AnimalDownloader.clear()

            animal_dict = AnimalDownloader.download()
            profile_dict = ProfileDownloader.download()

            Database.animal_dict = animal_dict
            Database.profile_dict = profile_dict
            Database.populate()
            Database.migrate()

    @classmethod
    def run(cls):
        with open('traceback.log', 'w') as f:
            try:
                action = cls.read_args()
                cls.execute(action)
            except:
                traceback.print_exc()
                with open('traceback.txt', 'w') as f:
                    traceback.print_exc(None, f, True)
                    print("\nTraceback saved. Please upload it to Teams if you can't solve the issue.")


if __name__ == '__main__':
    Script.run()