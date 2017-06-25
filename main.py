# coding:utf-8
import os
import time
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import func
from lib.pybloom import BloomFilter

def CreatUrls_lvl1():
    urls_lvl = ['http://www.moe.gov.cn/s78/A05/A05_zcwj/index.html']
    for i in range(1, 17 + 1):
        urls_lvl.append('http://www.moe.gov.cn/s78/A05/A05_zcwj/index_' + str(i) + '.html')
    return urls_lvl

def CreatItems_lvl2(urls_lvl1):
    # structure: [title,date,link]
    #         [...]
    #         [...]

    Items_lvl2 = []  # declare a empty list

    for cur_Url in urls_lvl1:
        base_url = cur_Url  # 用于../../..链接
        # *bug fix* content.decode('utf-8') 转换为与网页一致的utf-8，防止乱码出现
        page_html = requests.get(cur_Url).content.decode('utf-8')
        soup = BeautifulSoup(page_html, "html.parser")

        # locate dom_li in html code
        tag_div = soup.find('div', class_='sj_cen').find('ul')
        for li in tag_div.children:
            # todo 美化一下，找到去除空行的方法
            if li != '\n':
                txt = li.contents[0].string
                link = urljoin(base_url, li.a['href'])  # 用于重定向../../url.com
                date = li.contents[1].string
                Item_lvl2 = [txt, date, link]
                Items_lvl2.append(Item_lvl2)

    return Items_lvl2

def ParseItem(Items_lvl2):
    i = 1
    url_pool = func.file2set(os.getcwd() + '\\log\\url_pool.txt')
    p = open(os.getcwd() + '\\log\\url_pool.txt', 'a')
    for cur_Item in Items_lvl2:
        if cur_Item[2] not in url_pool:
            try:
                buffer = ''
                full_path = os.getcwd() + '\\output\\' + cur_Item[1] + ' ' + func.fineName4Win(cur_Item[0]) + '.txt'
                page_html = requests.get(cur_Item[2], timeout=3).content.decode('utf-8', 'ignore')
                soup = BeautifulSoup(page_html, 'html.parser')

                # 判断 网页结构pattern
                pattern_1 = soup.find(class_='xxgk_main')  # locate content div ( the style 1 )
                pattern_2 = soup.find(id='jyb_common_content')  # locate content div ( the style 2 )
                if pattern_1:
                    buffer = ParseItem_pattern1(cur_Item, soup)
                elif pattern_2:
                    buffer = ParseItem_pattern2(cur_Item, soup)
                else:
                    print("Error %s!\n" % cur_Item[2])

                try:
                    with open(full_path, 'w', encoding='utf-8') as f:   # 以utf8编码新建文件，防止utf8 & GBK转换出问题
                        f.write(buffer)
                   # 记录已爬过
                    # p.write(func.hash4string(cur_Item[2]) + '\n')
                    p.write(cur_Item[2] + '\n')
                except IOError as ioerr:
                    print(ioerr)
                    with open(os.getcwd() + '\\log\\io_err.log', 'a') as log_f:
                        log_f.write(request_err + full_path + '\n')
                    pass

                print('%d # OK %s %s' % (i, cur_Item[1], cur_Item[0]))
                i = i + 1
                time.sleep(0.1)

            except requests.exceptions.RequestException as request_err:
                print(request_err)
                with open(os.getcwd() + '\\log\\con_log.log','a') as log_f:
                    log_f.writelines(request_err)
        else:
            print('%d # Skip %s %s' % (i, cur_Item[1], cur_Item[0]))
            i=i+1
    p.close()


def ParseItem_pattern1(cur_Item, soup):
    buffer = "[标题:]    " + cur_Item[0] + '\n' + "[发布时间:]    " + cur_Item[1] + '\n'
# locate 根div
    dom_xxgk_content_div = soup.find('div', id='xxgk_content_div')  # locate content div ( the style 1 )
# locate 文件号
    if dom_xxgk_content_div:
        doc_num = dom_xxgk_content_div.find(id='xxgk_content_fwzh_top').get_text()
        buffer = buffer + "[文件号:]    " + doc_num + '\n'
        # locate DOM 正文
        buffer = buffer + "[正文:]" + '\n'
        div_final = dom_xxgk_content_div.find_all('p', recursive=False)  # recursive 只搜索子节点而不是子孙
        # 获取最终文字
        if len(div_final) != 0:
            for child in div_final:
                buffer = buffer + child.get_text() + '\n'
    else:
        print("Error in parseItem_pattern 1\n")

    return buffer
def ParseItem_pattern2(cur_Item, soup):
    buffer = "[标题:]    " + cur_Item[0] + '\n' + "[发布时间:]    " + cur_Item[1] + '\n'
    # locate 根div
    div_lvl_1 = soup.find('div', id='content_body')  # locate content div ( the style 1 )
    # locate 文件号
    if div_lvl_1:
        doc_num = re.findall(r"var file_fwzh='(.+?)';", div_lvl_1.get_text())  # 提取 var file_fwzh= '发文号'; 中的文号
        if len(doc_num) == 1:
            buffer = buffer + "[文件号:]    " + doc_num[0] + '\n'
        else:
            buffer = buffer + "[文件号:]    \n"
        # locate DOM 正文
        buffer = buffer + "[正文:]" + '\n'
        div_final = div_lvl_1.find_all('p')
        # 获取最终文字
        if len(div_final) != 0:
            for child in div_final:
                buffer = buffer + child.get_text() + '\n'
    else:
        print("Error in parseItem_pattern 2\n")

    return buffer




def test():
    t = ['http://www.baidd.com', 'http://www.google.com','http://www.adafdf.com']
    for i in t:
        try:
            r= requests.get(i, timeout=2)
        except requests.exceptions.RequestException as err:
            print(err)
    return 0
# t3 = [['ttttt', '2017-04-20 ',
#        'http://www.moe.gov.cn/s78/A05/A05_ztzl/s7507/s7508/s7509/201308/t20130813_155643.html'], \
#       ['财政部 教育部 人民银行 银监会关于进一步落实高等教育学生资助政策的通知', '2017-04-13 ',
#        'http://www.moe.gov.cn/jyb_xxgk/moe_1777/moe_1779/201704/t20170413_302466.html']]
# t4 = [t3[0]]
# ParseItem(t4)
#
# page_list = CreatUrls_lvl1()
# article_list = CreatItems_lvl2(page_list)
# ParseItem(article_list)

