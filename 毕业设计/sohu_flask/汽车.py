# -*- coding = utf-8 -*-
# @Time :  2024/3/31 11:07
# @Author : 梁正
# @File : 汽车.py
# @Software : PyCharm

from crawl_sohu import SohuSpider


def main():
    article_type = '汽车'
    url_dict = {
        'https://www.sohu.com/xchannel/TURBd01EQTNNekV3': [article_type, '新车快报'],
        'https://www.sohu.com/xchannel/TURBd01EQTNNekV4': [article_type, '买车必看'],
        'https://www.sohu.com/xchannel/TURBd01EQTNNekV5': [article_type, '新能源'],
        'https://www.sohu.com/xchannel/TURBd01EQTNNekV6': [article_type, '车市行情'],

    }
    spider = SohuSpider(url_dict)
    spider.spider_main()


if __name__ == '__main__':
    main()
