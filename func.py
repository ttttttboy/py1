# coding:utf-8
from hashlib import md5

def hash4string(srcbyte):
    # 将字符串和汉字转化成byte类型
    srcbyte = str.encode('gb2312')
    m = md5()
    m.update(srcbyte)
    return m.hexdigest()

def isByteInHashPool(target, hashPool):
    """
    :type hashPool: set
    :type target: string
    :return bool
    """
    # srcbyte = target.encode('gb2312')
    return target in hashPool


def file2BloomFilter(file):
    """

    :type file: string
    :return: set
    """
    from pybloom import BloomFilter
    bf = BloomFilter(capacity=1000, error_rate=0.001)
    with open(file, 'r') as f:
        for line in f:
            _ = bf.add(line.strip('\n'))
    return bf


def fineName4Win(old_name):
    import re
    new_name = 'Error'
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
    if old_name is not None:
        new_name = re.sub(rstr, " ", old_name)
    return new_name

