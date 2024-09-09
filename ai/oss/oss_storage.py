
import hashlib
from typing import IO, Any, Optional
import uuid
import oss2
from django.core.files.storage import Storage, default_storage
from main import settings
import os
import datetime
from oss2 import Bucket


class AIImageStorage(Storage):

    def createBucket():
        return oss2.Bucket(oss2.Auth(
            settings.ACCESS_KEY_ID, settings.ACCESS_KEY_SECRET), settings.END_POINT, settings.BUCKET_NAME)

    def get_content_type(filename_extension):
        if filename_extension.lower() == ".bmp":
            return "image/bmp"
        if filename_extension.lower() == ".gif":
            return "image/gif"
        if filename_extension.lower() == ".jpeg":
            return "image/jpeg"
        if filename_extension.lower() == ".jpg":
            return "image/jpg"
        if filename_extension.lower() == ".png":
            return "image/jpg"
        if filename_extension.lower() == ".html":
            return "text/html"
        if filename_extension.lower() == ".txt":
            return "text/plain"
        if filename_extension.lower() == ".vsd":
            return "application/vnd.visio"
        if filename_extension.lower() in {".pptx", ".ppt"}:
            return "application/vnd.ms-powerpoint"
        if filename_extension.lower() in {".docx", ".doc"}:
            return "application/msword"
        if filename_extension.lower() == ".xml":
            return "text/xml"
        return "application/octet-stream"

    def upload2oss(bucket: Bucket, name, content):
        ext = name.split('.')[-1]
        content_type = AIImageStorage.get_content_type(f".{ext}")
        current_month = datetime.datetime.now().strftime('%Y%m')
        file_content_md5 = hashlib.md5(content.read()).hexdigest()

        new_name = f"{current_month}/{file_content_md5}.{ext}"

        headers = {}
        # headers['Content-Type'] = 'application/octet-stream'
        # headers['Content-Type'] = content_type
        # headers['Content-Disposition'] = f'attachment; filename={new_name}'
        headers['Content-Disposition'] = f'inline'
        content.seek(0)
        # local_file=f"{file_content_md5}.{ext}"
        # with open(local_file,"wb") as f:
        #     f.write(content.read())

        content.open()
        content_str = b''.join(chunk for chunk in content.chunks())
        # bucket.put_object_from_file(new_name, local_file, headers=headers)  # add headers
        bucket.put_object(
            new_name, content_str, headers=headers)  # add headers
        content.close()

        return new_name.replace('\\', '/')

    def save_image(file_content):
        current_month = datetime.datetime.now().strftime('%Y%m')
        file_md5 = hashlib.md5(file_content).hexdigest()
        file_path = f"{current_month}/{file_md5}.png"
        result = default_storage.save(file_path, file_content)
        return result
        pass

    def __init__(self, option=None):

        if not option:
            option = {}
        self.option = option
        self.local_storage = default_storage
        self.bucket = AIImageStorage.createBucket()

    def _open(self, name, mode='rb'):
        # 实现打开文件的逻辑
        #

        return self.bucket.get_object(self._normalize_name(name)).read()

    # def _save(self, name, content):
    #     # 实现保存文件的逻辑
    #     _, ext = os.path.splitext(self._normalize_name(name))
    #     name = str(uuid.uuid4()) + ext
    #     self.bucket.put_object(name, content)
    #     return name

    def save(self, name: str | None, content: IO[Any], max_length: int | None = ...) -> str:
        return super().save(name, content, max_length)

    def _save(self, name, content):
        return AIImageStorage.upload2oss(self.bucket, name, content)

    def delete(self, name):
        # 实现删除文件的逻辑
        self.bucket.delete_object(self._normalize_name(name))

    def exists(self, name):
        # 实现检查文件是否存在的逻辑
        # return self.bucket.object_exists(self._normalize_name(name))
        return False

    def size(self, name):
        # 实现获取文件大小的逻辑
        return self.bucket.get_object_meta(self._normalize_name(name)).headers['Content-Length']

    def url(self, name):
        # 实现获取文件 URL 的逻辑
        url = f"{settings.OSS_CNAME_HOST}/"
        return f"{url}{self._normalize_name(name)}"

    def _normalize_name(self, name):
        return os.path.normpath(self._clean_name(name))

    def _clean_name(self, name):
        return name

    def get_available_name(self, name: str, max_length: int | None = ...) -> str:
        return name
