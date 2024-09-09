import datetime
import math
import random
import uuid


class NumberUtil:
    
    
    def random_int(a, b):
        return math.floor(a + (b-a+1)*random.random())
    
    def find_nearest_multiple(a, b):
        r1 = a/b
        r2 = int(r1)
        r3 = r2*b
        r4 = r3
        r5 = int(r4)
        # print(r1,r2,r3,r4,r5)
        return r5

    def createUUID(suffix=""):
        return uuid.uuid5(uuid.NAMESPACE_DNS, f"{suffix}-"+str(
            datetime.datetime.now().timestamp()))
