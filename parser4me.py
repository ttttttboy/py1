# coding:utf-8

import requests
from func import fineName4Win
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def parser_2(page_url, page_html):
    """
    用于分析"教育部-重要文件-<li>"
    :return results[[title, date, link],[   ],[   ]...]
    """
    base_url = page_url
    soup = BeautifulSoup(page_html, "html.parser")
    results = []

    # locate dom_li in html code
    tag_div = soup.find('div', id='wcmpagehtml').find('ul')
    for li in tag_div.children:
        # todo 美化一下，找到去除空行的方法
        # todo link txt date 任一一个为空 抛出异常
        if li != '\n':
            # todo 更好的方法定为 <a>
            tmp = dict(li.contents[1].attrs)["title"]  # 获取li下第一个tag里title的属性值
            title = fineName4Win(tmp)
            link = urljoin(base_url, li.a['href'])  # 用于重定向../../url.com
            date = li.contents[0].string
            results.append([title, date, link])
    return results

def parser_2_1(item, page_html):
    url = item[2]
    title = item[0]
    date = item[1]
    soup = BeautifulSoup(page_html, "html.parser")

    res = ""
    # 判断 网页结构pattern
    div_content_body = soup.find('div', id='content_body')
    div_p = div_content_body.find('div', id='content_body_txt').find_all('p')
    if len(div_p) != 0:
        for child in div_p:
            # print(child.getText())
            res += child.getText()

    return res
