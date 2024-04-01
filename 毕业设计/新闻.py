# -*- coding = utf-8 -*-
# @Time :  2024/3/31 10:32
# @Author : 梁正
# @File : 新闻.py
# @Software : PyCharm

from public_fucs import *

# 声明一个变量来记录重试的记录次数
retry_num = 0
# 爬取失败的列表集合
failed_links = []
# 文章类型
article_type = '新闻'


def main():
    url_dict = {
        'https://www.sohu.com/xchannel/tag?key=%E6%96%B0%E9%97%BB-%E6%97%B6%E6%94%BF': [article_type, '时政'],
        'https://www.sohu.com/xchannel/tag?key=%E6%96%B0%E9%97%BB-%E5%9B%BD%E9%99%85': [article_type, '国际'],
        'https://www.sohu.com/xchannel/tag?key=%E6%96%B0%E9%97%BB-%E8%B4%A2%E7%BB%8F': [article_type, '财经'],
    }
    spider_main(url_dict)


main()
