import os
import shutil 

from util.animal_downloader import AnimalDownloader
from util.database import Database
from util.profile_downloader import ProfileDownloader


class FileManager:
    MODULES = [AnimalDownloader, Database, ProfileDownloader]

    @classmethod
    def validate_working_directory(cls) -> None:
        # create folder if they don't exists
        for module in cls.MODULES:
            for folder in module.FOLDERS:
                os.makedirs(folder, exist_ok=True) 
                # create an __init__.py
                init_path = os.path.join(folder, '__init__.py')
                with open(init_path, 'a') as f: 
                    pass

    @classmethod
    def clear(cls, module) -> None:
        for file in module.FILES:
            if os.path.exists(file):
                os.remove(file)

        # remove all files and folders in a directory
        # except __init__.py
        for folder in module.FOLDERS:
            init_path = os.path.join(folder, '__init__.py')
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                if item_path == init_path:
                    continue
                elif os.path.isfile(item_path):
                    os.remove(item_path)
                else:
                    shutil.rmtree(item_path)

    @classmethod
    def clear_all(cls) -> None:
        for module in cls.MODULES:
            cls.clear(module)
