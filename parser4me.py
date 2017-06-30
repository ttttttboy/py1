# coding:utf-8
import re
from io import open
from os import getcwd
from os.path import isfile
# from func import fineName4Win
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode


def CreatStartURLs_2():
    """
    用于分析"教育部-> 重要文件-> 中央文件
    :return: URLs[]
    """
    res = []
    res.append('http://www.moe.edu.cn/jyb_xxgk/moe_1777/moe_1778/index.html')  # 财政部-中央文件
    for i in range(1, 5 + 1):
        res.append('http://www.moe.edu.cn/jyb_xxgk/moe_1777/moe_1778/index_' + str(i) + '.html')
    return res

def CreatStartURLs_3():
    """
    用于分析"教育部-> 重要文件-> 其他部门文件
    :return: URLs[]
    """
    res = []
    res.append('http://www.moe.edu.cn/jyb_xxgk/moe_1777/moe_1779/index.html')  # 财政部-中央文件
    for i in range(1, 12 + 1):
        res.append('http://www.moe.edu.cn/jyb_xxgk/moe_1777/moe_1779/index_' + str(i) + '.html')
    return res

def CreatStartURLs_4():
    """
    用于分析"教育部-> 重要文件-> 教育部文件
    :return: URLs[]
    """
    res = []
    base_url = "http://www.moe.gov.cn/was5/web/search"
    for i in range(1, 90+1):
        payload = {'page':i, # total items 8928. -> total pages 8928/100 = 90
                   'channelid': 277865, 'perpage':100, 'outlinepage':10, 'searchscope':'',
                   'timescope':'', 'timescopecolumn':'', 'orderby':'-SCRQ', 'towcmurl':'', 'andsen':'',
                   'total':'','orsen':'', 'exclude':''}
        res.append(base_url + '?' + urlencode(payload))
    return res

def parser_2(page_url, page_html):
    """
    用于分析"教育部-> 重要文件-> 中央文件-> DOM <li>"
    :return results[[title, date, link],[ li ],[ li ]...]
    """
    base_url = page_url
    soup = BeautifulSoup(page_html, "html.parser")
    results = []

    # locate dom_li in html code
    tag_div = soup.find('div', id='wcmpagehtml').find_all('ul')
    for ul in tag_div:
        if not ul.find('script'): # 排除<ul> <script/> </ul>
            for li in ul.children:
                # todo 美化一下，找到去除空行的方法
                # todo link txt date 任一一个为空 抛出异常
                if li != '\n':
                    # todo 更好的方法locate<a>
                    attrs_dict = li.contents[1].attrs
                    tmp = attrs_dict.get("title")     # 获取li下第一个tag里title的属性值 as dict(li.contents[1].attrs)["title"]
                    if tmp == None:
                        tmp = li.contents[1].get_text()
                    title = fineName4Win(tmp)
                    link = urljoin(base_url, li.a['href'])  # 用于重定向../../url.com
                    date = li.contents[0].get_text()
                    results.append([title, date, link])
    return results

def parser_2_1(item, page_html):
    url = item[2]
    title = item[0]
    date = item[1]
    soup = BeautifulSoup(page_html, "html.parser")
    res = ""

    # res += "#1[Title]\n" + item[0] + '\n'
    # res += "#2[Date]\n" + item[1] + '\n'
    # res += "#3[Content]\n"

    div_content_body = soup.find('div', id='content_body')
    if div_content_body != None:
        doc_num = re.findall(r"var file_fwzh='(.+?)';", div_content_body.get_text())  # 提取 var file_fwzh= '发文号'; 中的文号
        div_p = div_content_body.find('div', id='content_body_txt').find_all('p')
    res += "源文件地址：" + item[2] + '\n'
    res += "标题： " + item[0] + '\n'
    if len(doc_num) > 0:
        res += "发文字号： " + doc_num[0] + '\n'
    res += "发布时间：" + item[1] + '\n'
    res += "正文： \n"
    if len(div_p) != 0:
        for child in div_p:
            # print(child.getText())
            res += child.getText() + '\n'

    return res

def parser_3(page_url, page_html):
    """
    用于分析"教育部-> 重要文件-> 其他部门文件-> DOM<li>"
    :return results[[title, date, link],[   ],[   ]...]
    """
    return parser_2(page_url, page_html)

def parser_3_1(item, page_html):
    url = item[2]
    title = item[0]
    date = item[1]
    soup = BeautifulSoup(page_html, "html.parser")
    res = ""
    doc_num = [" "]
    div_content_body = []
    div_p = []
    # res += "#1[Title]\n" + item[0] + '\n'
    # res += "#2[Date]\n" + item[1] + '\n'
    # res += "#3[Content]\n"

    div_content_body = soup.find('div', id='jyb_common_content')
    if div_content_body != None:
        doc_num = re.findall(r"var file_fwzh='(.+?)';", div_content_body.get_text())  # 提取 var file_fwzh= '发文号'; 中的文号
        div_p = div_content_body.find('div', id='content_body').find_all('p')
        if div_p == None:
            div_p = div_content_body.find('div', id='content_body_txt').find_all('p')

    res += "源文件地址：" + item[2] + '\n'
    res += "标题： " + item[0] + '\n'
    if len(doc_num) > 0:
        res += "发文字号： " + doc_num[0] + '\n'
    res += "发布时间：" + item[1] + '\n'
    res += "正文： \n"
    if len(div_p) != 0:
        for child in div_p:
            # print(child.getText())
            res += child.getText() + '\n'

    return res

def parser_4(page_url, page_html):
    """
    用于分析"教育部-> 重要文件-> 财政部-> DOM<li>"
    :return results[[title, date, link],[   ],[   ]...]
    """
    return parser_2(page_url, page_html)

def parser_4_1(item, page_html):
    url = item[2]
    title = item[0]
    date = item[1]
    soup = BeautifulSoup(page_html, "html.parser")
    res = ""
    doc_num = [" "]
    div_content_body = []
    div_p = []
    # res += "#1[Title]\n" + item[0] + '\n'
    # res += "#2[Date]\n" + item[1] + '\n'
    # res += "#3[Content]\n"


    # locate 根div
    dom_xxgk_content_div = soup.find('div', id='xxgk_content_div')
    # get 发文字号
    if dom_xxgk_content_div != None:
        fwzh_top = dom_xxgk_content_div.find(id='xxgk_content_fwzh_top')
        if fwzh_top != None:
            doc_num = [dom_xxgk_content_div.find(id='xxgk_content_fwzh_top').get_text()]
        div_p = dom_xxgk_content_div.find_all('p', recursive=False)  # recursive 只搜索子节点而不是子孙

    # if div_content_body != None:
    #     doc_num = re.findall(r"var file_fwzh='(.+?)';", div_content_body.get_text())  # 提取 var file_fwzh= '发文号'; 中的文号
    #     div_p = div_content_body.find('div', id='content_body').find_all('p')
    #     if div_p == None:
    #         div_p = div_content_body.find('div', id='content_body_txt').find_all('p')

    res += "源文件地址：" + item[2] + '\n'
    res += "标题： " + item[0] + '\n'
    if len(doc_num) > 0:
        res += "发文字号： " + doc_num[0] + '\n'
    res += "发布时间：" + item[1] + '\n'
    res += "正文： \n"
    if len(div_p) != 0:
        for child in div_p:
            # print(child.getText())
            res += child.getText() + '\n'

    return res



def fineName4Win(old_name):
    import re
    new_name = 'Error'
    rstr = r"[\/\\\:\*\?\"\<\>\|\s]"  # '/\:*?"<>|space'
    if old_name is not None:
        new_name = re.sub(rstr, "", old_name)
    return new_name

