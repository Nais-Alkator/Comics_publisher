import requests
import random
import os
from os import makedirs
from dotenv import load_dotenv

load_dotenv()


ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")


def get_wall_upload_server():
    url = "https://api.vk.com/method/photos.getWallUploadServer?group_id={0}&access_token={1}&v=5.101".format(
        GROUP_ID, ACCESS_TOKEN)
    response = requests.get(url)
    response = response.json()
    return response


def upload_photo(random_image):
    with open(random_image, 'rb') as file:
        upload_server = get_wall_upload_server()
        upload_url = upload_server["response"]["upload_url"]
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
        response = response.json()
        return response


def save_wall_photo(upload_photo):
    photo = str(upload_photo["photo"])
    server = str(upload_photo["server"])
    hash_info = str(upload_photo["hash"])
    url = "https://api.vk.com/method/photos.saveWallPhoto?group_id={0}&photo={1}&server={2}&hash={3}&access_token={4}&v=5.101".format(
        GROUP_ID, photo, server, hash_info, ACCESS_TOKEN)
    response = requests.post(url)
    response = response.json()
    return response


def post_photo(saved_photo, random_image):
    media_id = saved_photo["response"][0]["id"]
    owner_id = saved_photo["response"][0]["owner_id"]
    message = random_image[1]
    url = "https://api.vk.com/method/wall.post?owner_id=-{0}&access_token={1}&v=5.101&attachments=photo{2}_{3}&from_group=0&message={4}".format(
        GROUP_ID, ACCESS_TOKEN, owner_id, media_id, message)
    response = requests.post(url)
    posted_photo = response.json()
    return posted_photo


def get_number_of_last_comic():
    url = "http://xkcd.com/353/info.0.json"
    response = requests.get(url)
    response = response.json()
    number_of_last_comic = response["num"]
    return number_of_last_comic


def save_random_image():
    makedirs("images", exist_ok=True)
    last_comic = get_number_of_last_comic()
    random_comic = random.randint(1, last_comic)
    url = "http://xkcd.com/{}/info.0.json".format(random_comic)
    response = requests.get(url)
    response = response.json()
    image_url = response["img"]
    image_title = response["title"]
    comments = response["alt"]
    file_name = ("images/" + image_title + ".png")
    response = requests.get(image_url, verify=False)
    response.raise_for_status()
    with open(file_name, 'wb') as file:
        file.write(response.content)
    return [file_name, comments]


if __name__ == "__main__":
    random_image = save_random_image()
    uploaded_photo = upload_photo(random_image[0])
    saved_photo = save_wall_photo(uploaded_photo)
    posted_photo = post_photo(saved_photo, random_image)
    os.remove(random_image[0])
