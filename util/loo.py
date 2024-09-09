
import datetime
import logging


class Loo:

    def init_in_duo_progress():
        logger =logging.getLogger()
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)s][%(levelname)s]%(message)s", "%Y-%m-%d %I:%M:%S")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        

        pass
    
    def info(obj):
        # t=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.getLogger().info(f"{obj}")
        print(f"{obj}")
        pass

    def err(obj):
        # t=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.getLogger().error(f"{obj}")
        pass
    def error(obj):
        # t=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.getLogger().error(f"{obj}")
        pass
    
    def debug(obj):
        # t=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.getLogger().debug(f"{obj}")
        pass

    def warn(obj):
        # t=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.getLogger().warn(f"{obj}")
        pass
