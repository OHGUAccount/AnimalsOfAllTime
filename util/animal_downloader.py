import concurrent.futures
import json
import os
import requests

from bs4 import BeautifulSoup


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
    FILES = ["animal.json"]
    FOLDERS = ["media\\animal_images"]

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
        if len(urls) == 0:
            raise Exception('Download failed. Are you connected to the internet?')
        end = min(len(urls), count)
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
        
        print(f"{len(output_dict)} animals downloaded!")
        return output_dict
