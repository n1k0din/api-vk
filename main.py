import os.path
from os import getenv

import urllib3
import requests
from dotenv import load_dotenv


def download_img(url, filename, images_dir='.'):
    full_path = os.path.join(images_dir, filename)

    response = requests.get(url, verify=False)
    response.raise_for_status()

    with open(full_path, 'wb') as file:
        file.write(response.content)


def download_xkcd_comics(comics_id):
    url = f'http://xkcd.com/{comics_id}/info.0.json'

    response = requests.get(url)
    response.raise_for_status()

    img_url = response.json()['img']
    print(response.json()['alt'])

    # download_img(img_url, 'image.png')


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    load_dotenv('.env')
    vk_app_client_id = getenv('VK_APP_CLIENT_ID')

    download_xkcd_comics(353)


if __name__ == '__main__':
    main()
