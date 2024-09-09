


from datetime import datetime, timedelta

def display_time_difference(created_time):
    if created_time is None:
        return '未知时间'
    current_time = datetime.now()
    time_difference = current_time - created_time

    if time_difference.days > 7:
        return str(time_difference.days // 7) + '周前'
    elif time_difference.days > 0:
        return str(time_difference.days) + '天前'
    elif time_difference.seconds > 3600:
        return str(time_difference.seconds // 3600) + '小时前'
    elif time_difference.seconds > 60:
        return str(time_difference.seconds // 60) + '分钟前'
    else:
        return '刚刚'
