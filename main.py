import os
import os.path
from random import randint
from urllib.parse import urljoin

import urllib3
import requests
from dotenv import load_dotenv

from pprint import pprint

VK_API_VERSION = '5.130'
VK_API_URL = 'https://api.vk.com/'


def get_vk_group_upload_server_album_user(group_id, access_token, api_version):
    url = urljoin(VK_API_URL, 'method/photos.getWallUploadServer')

    params = {'group_id': group_id, 'access_token': access_token, 'v': api_version}

    response = requests.get(url, params=params)
    response.raise_for_status()

    response_data = response.json()['response']

    return response_data['upload_url'], response_data['album_id'], response_data['user_id']


def upload_img_to_vk(upload_url, img_filename='image.png'):
    with open(img_filename, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()

        response_data = response.json()
        return response_data['server'], response_data['photo'], response_data['hash']


def save_vk_wall_img(group_id, photo, server_id, photo_hash, access_token, api_version):
    url = urljoin(VK_API_URL, 'method/photos.saveWallPhoto')
    params = {
        'group_id': group_id,
        'photo': photo,
        'server': server_id,
        'hash': photo_hash,
        'access_token': access_token,
        'v': api_version,
    }

    response = requests.post(url, params=params)
    response.raise_for_status

    response_data = response.json()['response'][0]

    return response_data['id'], response_data['owner_id']


def post_img_to_vk_wall(
    group_id,
    img_media_id,
    img_owner_id,
    comics_comment,
    access_token,
    api_version,
):
    url = urljoin(VK_API_URL, 'method/wall.post')
    params = {
        'owner_id': f'-{group_id}',
        'from_group': 1,
        'attachments': f'photo{img_owner_id}_{img_media_id}',
        'message': comics_comment,
        'access_token': access_token,
        'v': api_version,
    }

    response = requests.post(url, params=params)
    response.raise_for_status()


def post_xkcd_comics_to_vk_wall(comics_id, vk_group_id, vk_access_token, vk_api_version):
    comics_filename, comics_comment = download_xkcd_comics(comics_id)

    server_url, _album, _user = get_vk_group_upload_server_album_user(
        vk_group_id,
        vk_access_token,
        vk_api_version)

    server_id, photo, hash = upload_img_to_vk(server_url, comics_filename)

    img_media_id, img_owner_id = save_vk_wall_img(
        vk_group_id, photo,
        server_id, hash,
        vk_access_token,
        vk_api_version,
    )

    post_img_to_vk_wall(
        vk_group_id,
        img_media_id,
        img_owner_id,
        comics_comment,
        vk_access_token,
        VK_API_VERSION,
    )

    os.remove(comics_filename)


def get_last_xkcd_comics_id():
    url = 'http://xkcd.com/info.0.json'

    response = requests.get(url)
    response.raise_for_status()

    return response.json()['num']


def download_xkcd_comics(comics_id):
    url = f'http://xkcd.com/{comics_id}/info.0.json'

    response = requests.get(url)
    response.raise_for_status()

    img_url = response.json()['img']
    filename = f'xkcd_{comics_id}.png'
    download_img(img_url, filename)

    return filename, response.json()['alt']


def download_img(url, filename, images_dir='.'):
    full_path = os.path.join(images_dir, filename)

    response = requests.get(url, verify=False)
    response.raise_for_status()

    with open(full_path, 'wb') as file:
        file.write(response.content)


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    load_dotenv('.env')
    vk_app_client_id = os.getenv('VK_APP_CLIENT_ID')
    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')

    last_comics_id = get_last_xkcd_comics_id()
    comics_id = randint(1, last_comics_id)

    post_xkcd_comics_to_vk_wall(comics_id, vk_group_id, vk_access_token, VK_API_VERSION)


if __name__ == '__main__':
    main()
