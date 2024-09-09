from datetime import datetime
import json
import time
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from ai.third import baidu_translate, stability_ai, thenextleg_io
from ai.models.api_key import ApiKey
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def Test(request):
    data = {"data": 111}
    message_id = "YdhSSzbuJ4BYvTvHqc0x"
    # result=thenextleg_io.get_message_status(message_id)
    text = "a running dog"
    # text = "Multi dimensional paper kirigami craft, paper illustration, Chinese illustration on white background, Night, starry sky, Milky Way, above super wide agle, Thomas Kinkade, dreamy, 4K, romantic, trending on Artstation colorful vanilla oil, 3d relief"
    result = thenextleg_io.text2image(prompt_text=text)
    print(result)
    # data=stability_ai.query_platform_engines(ApiKey.objects.filter(platform=1).first().key)
    # prompts = [
    #     {
    #         "text": "a running dog"
    #     }
    # ]
    # engine_id = "stable-diffusion-v1-5"
    # out_path = "test"
    # stability_ai.generation_image(ApiKey.objects.filter(
    #     platform=1).first().key, engine_id, prompts,out_path)

    # try:
    #     result = baidu_translate.Translate("hello".replace(",", "\n"))
    # except Exception as e:
    #     return JsonResponse({"code": -1, "msg": str(e)}, safe=False)

    return JsonResponse(data={"code": 0, "data": result}, safe=False)


def Home(request):
    return render(request, 'ai/homev2.html')


@csrf_exempt
def AjaxPostPrompt(request):
    # prompt_text = request.GET.get('prompts',None)
    obj = json.loads(request.body)

    prompt_text = obj['text']
    prompts = [
        {
            "text": prompt_text
        }
    ]
    engine_id = "stable-diffusion-v1-5"

    # out_path = f"{request.user.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    result = stability_ai.text_2_image(user_id=0, api_key=ApiKey.objects.filter(
        platform=1).first().key, engine_id=engine_id, text_prompts=prompts, samples=1)

    # out_path="test.png"
    # time.sleep(2)

    amount = stability_ai.query_balance(
        ApiKey.objects.filter(platform=1).first().key)
    return JsonResponse({"urls": result, "amount": amount}, safe=False)
