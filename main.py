from pprint import pprint
import requests
import json
import time
from progress.bar import FillingSquaresBar

token_vk = "958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008"
token_ya = "AQAAAAAF5wpHAADLW49NVCGEuEXOjuckYnhI9Bc"
test_vk_id = 552934290


class YaUploader:
    def __init__(self):
        self.token_vk = token_vk
        self.token_ya = token_ya
        self.user_id = input('Укажите ID профиля VK: ')
        self.yandex_folder = input('Укажите название папки на Яндекс.Диске: ')
        self.count_save = int(input('Введите максимальное число сохраняемых фотографий (5 по умолчанию): '))

    def get_new_folder(self):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token_ya}'
        }
        params = {
            'path': self.yandex_folder,
            'overwrite': 'true'
        }
        response = requests.put(url=url, headers=headers, params=params)
        if response.status_code != 201:
            return f'Папка с именем: {self.yandex_folder} уже существует!'
        else:
            return f'Папка: {self.yandex_folder} создана на Yandex disc'

    def get_requests_vk(self):
        url = "https://api.vk.com/method/photos.get?"
        params = {
            'owner_id': self.user_id,
            'album_id': 'profile',
            'extended': '1',
            'photo_sizes': '1',
            'access_token': self.token_vk,
            'v': '5.131'
        }
        response = requests.get(url=url, params=params)
        if response.status_code != 200:
            print('Failed')
        return response.json()

    def upload_file_ya_disk(self, file_name, url_vk):
        file_path = self.yandex_folder + '/' + file_name
        up_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token_ya}'}
        params = {'url': url_vk, 'path': file_path}
        response = requests.post(url=up_url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 202:
            print('Файл загружен на Яндекс Диск')

    def creation_json(self, info):
        with open('info_photo_files.json', 'a') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

    def get_response(self):
        count = 0
        if 'error' in self.get_requests_vk():
            print(f'Ошибка: Аккаунт ID:{self.user_id} недоступен')
        elif self.get_requests_vk()['response'].get('count', False) == 0:
            print(f'На аккаунте ID {self.user_id} нет фотографий!')
        else:
            for i in self.get_requests_vk()['response']['items']:
                if count < self.count_save:
                    info = []
                    temp_dict = {'file_name': f"{str(i['likes']['count']) + '.jpg'}",
                                 'size': f"{i['sizes'][-1]['type']}"}
                    if f"{temp_dict['file_name']}" not in info:
                        info.append(temp_dict)
                        self.upload_file_ya_disk(f"{str(i['likes']['count']) + '.jpg'}", f"{i['sizes'][-1]['url']}")
                    else:
                        alter_dict = {'file_name': f"{str(i['likes']['count']) + str(i['date']) + '.jpg'}",
                                      'size': f"{i['sizes'][-1]['type']}"}
                        info.append(alter_dict)
                        self.upload_file_ya_disk(f"{str(i['likes']['count']) + str(i['date']) + '.jpg'}",
                                                 f"{i['sizes'][-1]['url']}")
                    self.creation_json(info)
                    count += 1

    def start(self):
        if self.count_save is not None:
            bar = FillingSquaresBar('Countdown', max=self.count_save)
            for number in range(self.count_save):
                bar.next()
                time.sleep(1)
            self.get_response()
            bar.finish()
        else:
            self.count_save = 5
            bar = FillingSquaresBar('Countdown', max=self.count_save)
            for number in range(5):
                bar.next()
                time.sleep(1)
            self.get_response()
            bar.finish()


if __name__ == '__main__':
    uploader = YaUploader()
    uploader.start()
