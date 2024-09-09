

import requests
import os
SD_API_SITE = os.environ.get("SD_WEB_UI_API_SITE", None)
SD_WEB_UI_LOG_DIR = os.environ.get("SD_WEB_UI_LOG_DIR", None)

if SD_API_SITE is None:
    raise Exception("SD_WEB_UI_API_SITE is None")


def getRequestGetMethod(request_path: str):
    resp = requests.get(f"{SD_API_SITE}{request_path}")
    return resp.json()


def getCurrentSdModel():
    return getRequestGetMethod("/sdapi/v1/options/")['sd_model_checkpoint']


def getQueenSize():
    return getRequestGetMethod("/queue/status")['queue_size']


def switch_sd_model(model_title: str):
    data = {
        "sd_model_checkpoint": model_title
    }
    requests.post(f"{SD_API_SITE}/sdapi/v1/options", json=data)


def getAllSdModels():
    all = getRequestGetMethod("/sdapi/v1/sd-models/")
    result = {}
    for item in all:
        result[item['hash']] = item['title']
    return result


def createRequestJson(o):
    from ai.models.ai_image_record import ImageCreateRecord
    r: ImageCreateRecord = o
    create_count = r.params["count"]
    prompt_text = r.prompt_text
    negative_prompt = r.negative_prompt if r.negative_prompt else ""

    _w, _h = r.get_base_size_from_params()
    return {
        "enable_hr": False,
        "denoising_strength": 0,
        "firstphase_width": 0,
        "firstphase_height": 0,
        "hr_scale": 2,
        "hr_upscaler": "",
        "hr_second_pass_steps": 0,
        "hr_resize_x": 0,
        "hr_resize_y": 0,
        "hr_sampler_name": "",
        "hr_prompt": "",
        "hr_negative_prompt": "",
        "prompt": prompt_text,
        "styles": [

        ],
        "seed": -1,
        "subseed": -1,
        "subseed_strength": 0,
        "seed_resize_from_h": -1,
        "seed_resize_from_w": -1,
        "sampler_name": "Euler",
        "batch_size": 1,
        "n_iter": create_count,
        "steps": 50,
        "cfg_scale": 7,
        "width": _w,
        "height": _h,
        "restore_faces": True,
        "tiling": False,
        "do_not_save_samples": False,
        "do_not_save_grid": False,
        "negative_prompt": negative_prompt,
        "eta": 0,
        "s_min_uncond": 0,
        "s_churn": 0,
        "s_tmax": 0,
        "s_tmin": 0,
        "s_noise": 1,
        "override_settings": {},
        "override_settings_restore_afterwards": True,
        "script_args": [],
        "sampler_index": "Euler a",
        "script_name": "",
        "send_images": True,
        "save_images": False,
        "alwayson_scripts": {}
    }


def run_once():
    import logging
    import requests
    import json
    logger = logging.getLogger()
    from ai.api import sd_web_ui
    from ai.models.ai_image_record import ImageCreateRecord
    r = sd_web_ui.getWaitTask()

    if not r:
        logger.info("no task")
        return

    queueSize = getQueenSize()

    if queueSize > 0:
        logger.info(f"当前有队列在排队queueSize:{queueSize}")
        return

    logger.info(f"开始处理任务:{r.id}")

    current_model_title = getCurrentSdModel()

    if "style" not in r.params:
        logger.error(f"{r.id}:参数style不存在")
        return

    target_sd_model_hash = r.params["style"]

    all_sd_models = getAllSdModels()

    if target_sd_model_hash not in all_sd_models:
        logger.error(f"模型{target_sd_model_hash}不存在")
        r.create_status = ImageCreateRecord.STATUS_NOT_SD_MODEL
        r.save()
        return

    target_sd_model_title = all_sd_models[target_sd_model_hash]

    logger.info(f"目标模型:{target_sd_model_title},当前模型:{current_model_title}")

    if target_sd_model_title != current_model_title:
        logger.info(f"切换模型:{target_sd_model_title}")
        switch_sd_model(target_sd_model_title)
        logger.info(f"切换模型:{target_sd_model_title}完成")
    else:
        logger.info(f"模型已经是:{target_sd_model_title}")

    currentModel = getCurrentSdModel()
    logger.info(f"当前模型:{currentModel}")

    obj = createRequestJson(r)

    r.request_text = json.dumps(obj)

    url = SD_API_SITE + "/sdapi/v1/txt2img"
    logger.info(f"{r.id}开始请求:{url},数据:{obj}")
    resp = requests.post(url,
                         data=r.request_text,)
    # print(resp.json())

    if resp.status_code != 200:
        logger.error(f"{r.id}:请求失败:{resp.status_code}")
        return

    r.response_text = f"status_code:200,图片在文本中，不便于展示"

    images_base64_strs = resp.json()['images']
    img_size = len(images_base64_strs)
    logger.info(f"{r.id}:请求完成,图片数量:{img_size}")

    # import AIImageStorage
    # from ai.oss.oss_storage import AIImageStorage

    # bucket = AIImageStorage.createBucket()

    # AIImageStorage.upload2oss(bucket,".png",)
    from django.core.files.storage import default_storage
    import io
    image_paths = []
    import base64
    from main import settings
    host = f"http://{ settings.BUCKET_NAME}.{settings.END_POINT}"
    for image_str in images_base64_strs:
        file_content = base64.b64decode(image_str)
        save_path = default_storage.save("any.png", io.BytesIO(file_content))
        image_paths.append(f"{host}/{save_path}")

    r.images = json.dumps(image_paths)
    r.big_images = json.dumps(image_paths)
    r.create_status = ImageCreateRecord.STATUS_SUCCESS
    r.save()
    logger.info(image_paths)
    pass


def init_log_config():
    import logging

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s][%(levelname)s]%(message)s", "%Y-%m-%d %I:%M:%S")

    if SD_WEB_UI_LOG_DIR:
        log_dir = SD_WEB_UI_LOG_DIR
        fe = logging.FileHandler(log_dir + "/sd_web_ui.error.log")
        fe.setLevel(logging.ERROR)
        fe.setFormatter(formatter)
        logger.addHandler(fe)

        fh = logging.FileHandler(log_dir + "/sd_web_ui.log")
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    fs = logging.StreamHandler()
    fs.setLevel(logging.INFO)
    fs.setFormatter(formatter)
    logger.addHandler(fs)


if __name__ == '__main__':
    import os
    import django

    init_log_config()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
    django.setup()
    # 添加 INSTALLED_APPS
    from django.conf import settings
    settings.INSTALLED_APPS += ('ai',)

    import time

    while True:
        try:
            run_once()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(e)
        time.sleep(1)

    # run_once()
    pass
