

from datetime import timezone
import threading


def download_background(task_id: int):
    p = threading.Thread(target=do_multi_process_task, args=[task_id])
    # p = multiprocessing.Process(target=do_multi_process_task, args=[taskIdString])
    p.start()


def download_image(taskIdString: str):
    from util.loo import Loo
    import io
    import datetime
    from main import settings
    from ai.models.download_task import DownloadTask
    from ai.models.ai_image_record import ImageCreateRecord
    from django.core.cache import cache

    HOST = "https://go.ai.tianshuo.vip"

    task_id = int(taskIdString)
    t: DownloadTask = DownloadTask.objects.get(id=task_id)

    r: ImageCreateRecord = t.image_create_record

    t.download_status = DownloadTask.STATUS_DOWNLOADING

    t.start_time = datetime.datetime.now()

    t.save()
    import requests
    import os
    # 这里采用127.0.0.1:8000作为本地，线上会变成443
    if settings.is_online():
        proxy_host = "http://10.0.0.21:808"
        pass
    else:
        proxy_host = "http://192.168.110.89:808"
        
        pass

    try:

        resp = requests.get(t.from_url, proxies={
            "http": f"{proxy_host}",
            "https": f"{proxy_host}"
        }, stream=True)
        total_length = resp.headers.get('content-length')
        if total_length is None:  # no content length header
            image_data = resp.content
        else:
            total_length = int(total_length)
            buffer = io.BytesIO()
            count = 0
            chunk_size = 1024
            for data in resp.iter_content(chunk_size=chunk_size):
                count += len(data)
                buffer.write(data)
                if count % (chunk_size*100*3) == 0:
                    progress = int(count/total_length*100)+1
                    Loo.info(f"下载进度{progress}")
                    cache.set(t.get_redis_key(), progress, timeout=60*60*24*7)
                    pass

            progress = 100
            cache.set(t.get_redis_key(), progress, timeout=60*60*24*7)

            image_data = buffer.getvalue()
            pass

        t.finish_time = datetime.datetime.now()
        t.save()
    except Exception as e:
        # t.download_status = DownloadTask.STATUS_FAILED
        # t.save()
        Loo.error(f"下载失败{taskIdString}-{t.from_url}-{e}")
        post_failed__url = f"{HOST}/ai/download/failed?taskId={taskIdString}"
        resp = requests.post(post_failed__url)
        return
        pass

    Loo.info(f"下载成功,开始处理图片{taskIdString}<>{t.from_url}")

    from ai.api import download_task

    download_task.on_download_finish_v2(task=t, record=r, fileContent=image_data)
    
    
    Loo.info(f"保存本地成功{taskIdString}<>{t.from_url}")

    # post_url = HOST + f"/ai/download/finish?taskId={taskIdString}"

    # resp = requests.post(post_url, files={"file": ("1.png", image_data)})

    # if resp.status_code == 200 and resp.json()['code'] == 0:

    #     # print(f"上传成功{taskIdString}-{t.from_url}")
    #     Loo.info(f"上传成功{taskIdString}-{t.from_url}")
    # else:
    #     # print(f"上传失败{taskIdString}-{t.from_url}-{resp.text}")
    #     Loo.error(f"上传失败{taskIdString}-{t.from_url}-{resp.text}")

    pass


def do_multi_process_task(task_id_string: str):
    import os
    import django
    if 'DJANGO_SETTINGS_MODULE' not in os.environ.keys():
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
        django.setup()
        # 添加 INSTALLED_APPS
        from django.conf import settings
        settings.INSTALLED_APPS += ('ai',)

    from ai.multi_progress.download_image_progress import download_image

    download_image(task_id_string)

    pass
