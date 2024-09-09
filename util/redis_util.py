

from django_redis import get_redis_connection
from django.core.cache import cache

def lock(key, timeout=60*60*24*7):
    """
    :param key:
    :param timeout: 超时时间，单位秒
    :return:
    """

    redis_conn = get_redis_connection("default")
    # cache = RedisCache("default")

    with cache.lock("my_lock_name", timeout=10):
        # 在 10 秒内此部分代码只会被一个进程执行
        # ...
        pass



def check_connection():
    # redis_conn = get_redis_connection("default")
    
    cache.set("test", "test")
    print(cache.get("test"))
    pass
