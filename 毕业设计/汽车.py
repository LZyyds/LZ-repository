# -*- coding = utf-8 -*-
# @Time :  2024/3/31 11:07
# @Author : 梁正
# @File : 汽车.py
# @Software : PyCharm

from public_fucs import *

# 声明一个变量来记录重试的记录次数
retry_num = 0
# 爬取失败的列表集合
failed_links = []
# 文章类型
article_type = '汽车'


def main():
    url_dict = {
        'https://www.sohu.com/xchannel/TURBd01EQTNNekV3': [article_type, '新车快报'],
        'https://www.sohu.com/xchannel/TURBd01EQTNNekV4': [article_type, '买车必看'],
        'https://www.sohu.com/xchannel/TURBd01EQTNNekV5': [article_type, '新能源'],
        'https://www.sohu.com/xchannel/TURBd01EQTNNekV6': [article_type, '车市行情'],

    }
    spider_main(url_dict)


main()
