import os
from random import randint
from urllib.parse import urljoin

import requests
import urllib3
from dotenv import load_dotenv

VK_API_VERSION = '5.130'
VK_API_URL = 'https://api.vk.com/'
TEMP_IMAGES_EXT = '.png'


def check_vk_api_error(response):
    vk_answer = response.json()

    if 'error' in vk_answer:
        raise requests.HTTPError('Error in VK answer, check token, method and other params')

    if vk_answer.get('photo') == '[]':
        raise requests.HTTPError('VK photo not uploaded!')


def get_vk_group_upload_server_album_user(group_id, access_token, api_version):
    url = urljoin(VK_API_URL, 'method/photos.getWallUploadServer')

    params = {'group_id': group_id, 'access_token': access_token, 'v': api_version}

    response = requests.get(url, params=params)
    response.raise_for_status()
    check_vk_api_error(response)

    upload_params = response.json()['response']

    return upload_params['upload_url'], upload_params['album_id'], upload_params['user_id']


def upload_img_to_vk(upload_url, img_filename='image.png'):
    with open(img_filename, 'rb') as file:
        files = {'photo': file}
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
        check_vk_api_error(response)

        uploaded_photo_params = response.json()
        return (
            uploaded_photo_params['server'],
            uploaded_photo_params['photo'],
            uploaded_photo_params['hash'],
        )


def save_vk_wall_img(group_id, server_id, photo, photo_hash, access_token, api_version):
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
    response.raise_for_status()
    check_vk_api_error(response)

    saved_photo_params = response.json()['response'][0]

    return saved_photo_params['id'], saved_photo_params['owner_id']


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
    check_vk_api_error(response)


def post_xkcd_comics_to_vk_wall(comics_id, vk_group_id, vk_access_token, vk_api_version):
    comics_filename, comics_comment = download_xkcd_comics(comics_id)

    server_url, _album, _user = get_vk_group_upload_server_album_user(
        vk_group_id,
        vk_access_token,
        vk_api_version)

    server_id, vk_photo, photo_hash = upload_img_to_vk(server_url, comics_filename)

    img_media_id, img_owner_id = save_vk_wall_img(
        vk_group_id,
        server_id,
        vk_photo,
        photo_hash,
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


def get_last_xkcd_comics_id():
    url = 'http://xkcd.com/info.0.json'

    response = requests.get(url)
    response.raise_for_status()

    return response.json()['num']


def download_xkcd_comics(comics_id):
    url = f'http://xkcd.com/{comics_id}/info.0.json'

    response = requests.get(url)
    response.raise_for_status()

    comics_metadata = response.json()
    img_url = comics_metadata['img']
    filename = f'xkcd_{comics_id}.png'
    download_img(img_url, filename)

    return filename, comics_metadata['alt']


def download_img(url, filename, images_dir='.'):
    full_path = os.path.join(images_dir, filename)

    response = requests.get(url, verify=False)
    response.raise_for_status()

    with open(full_path, 'wb') as file:
        file.write(response.content)


def delete_files_by_ext(file_ext, dir='.'):
    files = os.listdir(dir)
    for file in files:
        if file.endswith(file_ext):
            os.remove(os.path.join(dir, file))


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    load_dotenv('.env')
    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    vk_group_id = os.getenv('VK_GROUP_ID')

    last_comics_id = get_last_xkcd_comics_id()
    comics_id = randint(1, last_comics_id)

    try:
        post_xkcd_comics_to_vk_wall(comics_id, vk_group_id, vk_access_token, VK_API_VERSION)
    except requests.HTTPError as e:
        print('HTTP error: ', e)
    finally:
        try:
            delete_files_by_ext(TEMP_IMAGES_EXT)
        except OSError:
            print('Error deleting temp files')


if __name__ == '__main__':
    main()
