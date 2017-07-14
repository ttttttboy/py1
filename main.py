# coding:utf-8
import time
import pickle
import requests
import threading
import parser4me
from config import *
from pybloom import ScalableBloomFilter  # in github
from serialization import out2File_txt


def SetUp():
    if not os.path.isdir(PATH_LOG_FOLDER):
        os.mkdir(PATH_LOG_FOLDER)
    if not os.path.isdir(PATH_OUTPUT_FOLDER):
        os.mkdir(PATH_OUTPUT_FOLDER)



def CreatURLQueue():
    """

    :return: None
    """
    urls_lv1 = parser4me.CreatStartURLs_4()

    if os.path.isfile(PATH_SERIALIZATION_QUEUE) and not DEBUG_IGNORE_SERIAL_QUEUE:   # 已存在url pool
        global URL_TODO_QUEUE
        with open(PATH_SERIALIZATION_QUEUE, 'rb') as ser_f:
            serialed_urls = pickle.load(ser_f)
            for item in serialed_urls:
                URL_TODO_QUEUE.put(item)

        print("Load URL_QUEUE = %s" % len(serialed_urls))
    else:                                                                            # 不存在url pool
        i = 0
        i_item = 0
        to_serial_urls = []
        for url_lv1 in urls_lv1:
            urls_lv2 = GetItemListByUrlLv1(url_lv1)
            i += len(urls_lv2)
            print("Got %s urls ( Total %s ) from %s" % (len(urls_lv2), i, url_lv1))

            for u in urls_lv2:
                # todo 分布式改成QUEUE https://stackoverflow.com/questions/16754116/pickle-queue-objects-in-python
                URL_TODO_QUEUE.put(u)
                to_serial_urls.append(u)
        with open(PATH_SERIALIZATION_QUEUE, 'wb') as ser_f:
            pickle.dump(to_serial_urls, ser_f, pickle.HIGHEST_PROTOCOL)
        print("Dummp URL_QUEUE = %s" % len(to_serial_urls))


def GetItemListByUrlLv1(url_lv1):
    """
    :param url_lv1:
    :return: struct is [title,date,link] [] [] []..... for the page url_lv1
    """
    time.sleep(0.3)
    page_html = requests.get(url_lv1).content.decode('utf-8')
    res = parser4me.parser_4(url_lv1, page_html)
    return res


def ParseQueue():
    # Load Checked Urls File
    if os.path.isfile(PATH_CHECKED_URLS) and not DEBUG_IGNORE_CHECKED_URL:
        with open(PATH_CHECKED_URLS, 'rb') as rf:
            checked_url_pool = ScalableBloomFilter.fromfile(rf)
            print("bf: Read pybloom from %s.\n" % PATH_CHECKED_URLS)
    else:
        checked_url_pool = ScalableBloomFilter(initial_capacity=1000, error_rate=0.001,
                                               mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        print("bf: Create pybloom")

    # Get each Item from Queue
    i = 0
    URL_TODO_QUEUE.put(None)
    for item in iter(URL_TODO_QUEUE.get_nowait, None):
        item.append(i)  # add num to item=[title, date, link, num, (content)]
        i += 1
        cur_url = item[2]
        cur_num = item[3]

        if (cur_url in checked_url_pool) == False:  # cur_url never checked
            try:
                time.sleep(0.3)
                page_html_raw = requests.get(cur_url, timeout=3)
            except requests.RequestException as e:
                print("Parser #%s Faile" % cur_num, end='')
                print(e)
                # URL_DEQUE.appendleft(cur_url)  #再循环
                with open(path_requestErr_log, 'a') as f_requestErr:
                    f_requestErr.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) +
                                       "Timeout " + cur_url + '\n')
                # print(" fail!")
            else:
                print("Parser #%s fetched " % cur_num)
                page_html = page_html_raw.content.decode('utf-8', 'ignore')
                buffer = parser4me.parser_4_1(item, page_html)

                # out2File_txt(buffer, item)
                # todo add content to item
                rich_buffer = [buffer, item]
                BUFFER_TO_SERIAL_QUEUE.put(rich_buffer)
                checked_url_pool.add(cur_url)
        else:
            print("Parser #%s skipped " % cur_num)


        with open(PATH_CHECKED_URLS, 'wb') as wf:
            checked_url_pool.tofile(wf)
            # print("bf: Write pybloom to %s " % path_checked_url_file)

    # end sub thread with put sign -1
    global THREAD_NUM
    for i in range(THREAD_NUM):
        BUFFER_TO_SERIAL_QUEUE.put(-1)


def worker_2File(num_thread):
    print("Thread_%s is running..." % num_thread)
    while True:
        rich_buffer = BUFFER_TO_SERIAL_QUEUE.get()
        if rich_buffer == -1:
            break
        else:
            print("Thread_%s to serial  #%s" % (num_thread, rich_buffer[1][3]))
            out2File_txt(rich_buffer[0], rich_buffer[1])

            # print("Thread: Saved to  ")
    print("Thread_%s Ends." % num_thread)


def runThreading(num_Threads):
    threads_list = []
    threads_list.append(threading.Thread(target=ParseQueue))  # 主进程
    threads_list[0].setName("MainThread")

    for i in range(num_Threads):
        t = threading.Thread(target=worker_2File, args=(i,))
        threads_list.append(t)


    for t in threads_list:
        t.start()
    for t in threads_list:
        if t.is_alive():
            t.join()


def main():
    SetUp()
    CreatURLQueue()

    debug_time_0 = time.time() if DEBUG_TIMER else 0
    # ParseQueue()
    runThreading(THREAD_NUM)

    print("DEBUG_Timer End：%s\n" % str(time.time() - debug_time_0)) if DEBUG_TIMER else None
    # demo_doc()
    print('')


if __name__ == "__main__":
    main()


