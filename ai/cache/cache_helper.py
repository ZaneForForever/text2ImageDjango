

from django.core.cache import cache


class CacheHelper:
    platform_config_params = "platform_config_params"
    key_tab_icons = "key_tab_icons"

    voice_token = "voice_token"

    
    
    def get_voice_key(is_custom, voice_id)->str:
        return f"{CacheHelper.voice_token}_{is_custom}_{voice_id}"
    
    
    def test():
        pass

    def get(key):

        return cache.get(key)

    def clear(key):
        cache.delete(key)
        pass

    def set(key, value):
        cache.set(key, value)
        pass
    
    def setForExpire(key, value, time_out):
        cache.set(key, value, time_out)

    def setForExpire(key, value, time_out):
        cache.set(key, value, time_out)
        pass
