# -*- coding = utf-8 -*-
# @Time :  2024/3/31 10:58
# @Author : 梁正
# @File : 财经.py
# @Software : PyCharm

from crawl_sohu import SohuSpider


def main():
    article_type = '财经'
    url_dict = {
        'https://www.sohu.com/xchannel/tag?key=%E8%B4%A2%E7%BB%8F-%E7%BB%8F%E6%B5%8E%E8%A7%A3%E7%A0%81': [article_type,
                                                                                                          '经济解码'],
        'https://www.sohu.com/xchannel/tag?key=%E8%B4%A2%E7%BB%8F-%E8%82%A1%E7%A5%A8': [article_type, '股票'],
        'https://www.sohu.com/xchannel/tag?key=%E8%B4%A2%E7%BB%8F-%E5%9F%BA%E9%87%91': [article_type, '基金'],
        'https://www.sohu.com/xchannel/tag?key=%E8%B4%A2%E7%BB%8F-IPO': [article_type, 'IPO'],
    }
    spider = SohuSpider(url_dict)
    spider.spider_main()


if __name__ == '__main__':
    main()
