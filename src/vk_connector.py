import io
import random
from typing import Union

import requests

VK_API_BASE = 'https://api.vk.com/method'
VK_API_VERSION = '5.199'


class VkConnectorException(ValueError):
    pass


class VkConnector:
    NAME = 'vk'

    def __init__(self, config):
        try:
            vk_cfg = config['vk']
            self._token = vk_cfg['token']
            self._peer_id = int(vk_cfg['peer_id'])
        except KeyError:
            raise VkConnectorException('vk.token и vk.peer_id обязательные параметры конфига')
        except (TypeError, ValueError):
            raise VkConnectorException('ошибка заполнения vk.peer_id')

    def send_message(self, msg: str):
        self._call('messages.send', {
            'peer_id': self._peer_id,
            'message': msg,
            'random_id': random.randint(0, 2 ** 31),
        })

    def send_pic(self, img_byte_arr: Union[bytes, io.BytesIO]):
        upload_url = self._get_messages_upload_server()
        photo_data = self._upload_photo(upload_url, img_byte_arr)
        attachment = self._save_messages_photo(photo_data)
        self._call('messages.send', {
            'peer_id': self._peer_id,
            'attachment': attachment,
            'random_id': random.randint(0, 2 ** 31),
        })

    # ------------------------------------------------------------------

    def _get_messages_upload_server(self) -> str:
        data = self._call('photos.getMessagesUploadServer', {'peer_id': self._peer_id})
        return data['upload_url']

    def _upload_photo(self, upload_url: str, img_byte_arr: Union[bytes, io.BytesIO]) -> dict:
        if isinstance(img_byte_arr, (bytes, bytearray)):
            img_byte_arr = io.BytesIO(img_byte_arr)
        img_byte_arr.seek(0)

        field_name = 'file1' if 'v2/bulk_upload' in upload_url else 'photo'
        photo_data = self._post_photo(upload_url, img_byte_arr, field_name)

        if not self._is_valid_upload_response(photo_data):
            img_byte_arr.seek(0)
            alt_field = 'photo' if field_name == 'file1' else 'file1'
            alt_data = self._post_photo(upload_url, img_byte_arr, alt_field)
            if self._is_valid_upload_response(alt_data):
                photo_data = alt_data

        if not self._is_valid_upload_response(photo_data):
            raise VkConnectorException(f'Ошибка загрузки фото VK: {photo_data}')
        return photo_data

    def _post_photo(self, upload_url: str, img_byte_arr: io.BytesIO, field_name: str) -> dict:
        resp = requests.post(
            upload_url,
            files={field_name: ('photo.png', img_byte_arr, 'image/png')},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _is_valid_upload_response(photo_data: dict) -> bool:
        if not isinstance(photo_data, dict) or photo_data.get('error_code'):
            return False
        photo = photo_data.get('photo')
        if isinstance(photo, str) and photo and photo != '[]':
            return True
        file1 = photo_data.get('files', {}).get('file1', {})
        return bool(file1.get('sha') and file1.get('secret'))

    @staticmethod
    def _parse_save_photo_params(photo_data: dict) -> dict:
        if isinstance(photo_data.get('photo'), str) and photo_data['photo'] and photo_data['photo'] != '[]':
            return {
                'photo': photo_data['photo'],
                'server': photo_data['server'],
                'hash': photo_data['hash'],
            }
        file1 = photo_data['files']['file1']
        return {
            'photo': f"{file1['sha']}_{file1['secret']}",
            'server': photo_data['server'],
            'hash': photo_data['hash'],
        }

    def _save_messages_photo(self, photo_data: dict) -> str:
        data = self._call('photos.saveMessagesPhoto', self._parse_save_photo_params(photo_data))
        photo = data[0]
        return f"photo{photo['owner_id']}_{photo['id']}"

    def _call(self, method: str, params: dict) -> dict:
        payload = {
            'access_token': self._token,
            'v': VK_API_VERSION,
            **params,
        }
        resp = requests.post(f'{VK_API_BASE}/{method}', data=payload, timeout=10)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            raise VkConnectorException(f'Ошибка HTTP при вызове {method}: {ex}')
        data = resp.json()
        if 'error' in data:
            err = data['error']
            raise VkConnectorException(f"VK API error {err['error_code']}: {err['error_msg']}")
        return data['response']
