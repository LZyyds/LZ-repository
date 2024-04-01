# -*- coding = utf-8 -*-
# @Time :  2024/3/31 10:49
# @Author : 梁正
# @File : 娱乐.py
# @Software : PyCharm

from public_fucs import *

# 声明一个变量来记录重试的记录次数
retry_num = 0
# 爬取失败的列表集合
failed_links = []
# 文章类型
article_type = '娱乐'


def main():
    url_dict = {
        'https://www.sohu.com/xchannel/tag?key=%E5%A8%B1%E4%B9%90-%E6%98%8E%E6%98%9F': [article_type, '明星'],
        'https://www.sohu.com/xchannel/tag?key=%E5%A8%B1%E4%B9%90-%E5%85%AB%E5%8D%A6': [article_type, '八卦'],
        'https://www.sohu.com/xchannel/tag?key=%E5%A8%B1%E4%B9%90-%E5%BD%B1%E8%A7%86%E9%9F%B3%E4%B9%90': [article_type,
                                                                                                          '影视音乐'],
        'https://www.sohu.com/xchannel/tag?key=%E5%A8%B1%E4%B9%90-%E7%BD%91%E7%BB%9C%E7%BA%A2%E4%BA%BA': [article_type,
                                                                                                          '网络红人'],

    }
    spider_main(url_dict)


main()
