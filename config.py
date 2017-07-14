# coding:utf-8
import os
import queue
# from collections import deque

URL_TODO_QUEUE = queue.Queue()
BUFFER_TO_SERIAL_QUEUE = queue.Queue()

PATH_OUTPUT_FOLDER = os.path.join(os.getcwd(), "APP_output")         #  ../py/APP_output/
PATH_LOG_FOLDER = os.path.join(os.getcwd(), "APP_log")
path_requestErr_log = os.path.join(os.getcwd(), "APP_output", "request_err.log")
PATH_CHECKED_URLS = os.path.join(os.getcwd(), "APP_log", "checked_url_pool.bfdat")
PATH_SERIALIZATION_QUEUE = os.path.join(os.getcwd(), "APP_log", "serial_QUEUE.dat")

# DEBUG Trigger
DEBUG_TIMER = True
DEBUG_IGNORE_CHECKED_URL = True
DEBUG_IGNORE_SERIAL_QUEUE = False

#Thread
THREAD_NUM = 4  # 4 203s  8 106s 16 118
