# -*- coding: utf-8 -*-
import logging
import multiprocessing

chdir = f"/app"


timeout = 60
backlog = 2048
bind = "0.0.0.0:80"
user = "root"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 1
daemon = False
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"

 

loglevel = "info"

logger = logging.getLogger()
logger.setLevel(logging.INFO)



formatter = logging.Formatter(
    "[%(asctime)s][%(levelname)s]%(message)s", "%Y-%m-%d %I:%M:%S")

# Console Handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

ch.setFormatter(formatter)
logger.addHandler(ch)


# Gunicorn Error File Handler
# fh = logging.FileHandler(log_dir + "/access.log")
# fh.setLevel(logging.INFO)
# fh.setFormatter(formatter)
# logger.addHandler(fh)
