import requests
import random
import os
from os import makedirs
from dotenv import load_dotenv
import tempfile


def get_wall_upload_server():
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    params = {"access_token": access_token, "group_id": group_id, "v": "5.101"}
    response = requests.get(url, params=params)
    response = response.json()
    if 'error' in response:
        raise requests.exceptions.HTTPError(response['error'])
    return response


def upload_photo(random_image):
    with open(random_image, 'rb') as file:
        upload_server = get_wall_upload_server()
        upload_url = upload_server["response"]["upload_url"]
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)
        response = response.json()
        return response


def save_wall_photo(upload_photo):
    photo = upload_photo["photo"]
    server = upload_photo["server"]
    hash_info = upload_photo["hash"]
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {"group_id": group_id, "photo": photo, "server": server, "hash": hash_info, "access_token": access_token, "v": "5.101"}
    response = requests.post(url, params=params)
    response = response.json()
    if 'error' in response:
        raise requests.exceptions.HTTPError(response['error'])
    return response


def post_photo(saved_photo, random_image):
    media_id = saved_photo["response"][0]["id"]
    owner_id = saved_photo["response"][0]["owner_id"]
    message = random_image[1]
    url = "https://api.vk.com/method/wall.post?owner_id=-{0}&access_token={1}&v=5.101&attachments=photo{2}_{3}&from_group=0&message={4}".format(
        group_id, access_token, owner_id, media_id, message)
    params = {"owner_id": "-{}".format(group_id), "access_token": access_token, "v": "5.101", "attachments": "photo{0}{1}".format(owner_id, media_id), "from_group": "0", "message": message}
    response = requests.post(url)
    posted_photo = response.json()
    if 'error' in posted_photo:
        raise requests.exceptions.HTTPError(posted_photo['error'])
    return posted_photo


def get_number_of_last_comic():
    url = "http://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    number_of_last_comic = response["num"]
    return number_of_last_comic


def save_random_image():
    try:
        temporary_directory = tempfile.TemporaryDirectory()
        temporary_directory = tempfile.gettempdir()
    except ValueError:
        exit()
    last_comic = get_number_of_last_comic()
    random_comic = random.randint(1, last_comic)
    url = "http://xkcd.com/{}/info.0.json".format(random_comic)
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    image_url = response["img"]
    image_title = response["title"]
    comments = response["alt"]
    image_path = "{0}/{1}.png".format(temporary_directory, image_title)
    response = requests.get(image_url, verify=False)
    response.raise_for_status()
    with open(image_path, 'wb') as file:
        file.write(response.content)
    return [image_path, comments]


if __name__ == "__main__":
    load_dotenv()
    access_token = os.getenv("ACCESS_TOKEN")
    group_id = os.getenv("GROUP_ID")
    try: 
        random_image = save_random_image()
        image_path = random_image[0]
        uploaded_photo = upload_photo(image_path)
        saved_photo = save_wall_photo(uploaded_photo)
        posted_photo = post_photo(saved_photo, random_image)
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))
    except requests.exceptions.ConnectionError as error:
        exit("Can't get data from server:\n{0}".format(error))
