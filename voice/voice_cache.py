

import json
from ai.cache.cache_helper import CacheHelper
from util.loo import Loo





def clear_cache(is_custom:bool,voice_id:str):
    cache_key = CacheHelper.get_voice_key(is_custom, voice_id)
    CacheHelper.clear(cache_key)
    pass


def getVoiceCache(is_custom, voice_id):
    from voice.models import VoiceTypeModel, VoiceTypeUserCustomModel
    
    cache_key =CacheHelper.get_voice_key(is_custom, voice_id)
    result = CacheHelper.get(cache_key)

    if result is not None:

        return result

    if is_custom:
        v = VoiceTypeUserCustomModel.objects.filter(
            voice_id=voice_id).first()
        result = v.ToJsonObj() if v else None
    else:
        v = VoiceTypeModel.objects.filter(
            voice_id=voice_id).first()
        result = v.ToJsonObj() if v else None

    if result is not None:
        CacheHelper.set(cache_key, result)
    
    return result
