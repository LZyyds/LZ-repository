# -*- coding = utf-8 -*-
# @Time :  2024/3/31 11:02
# @Author : 梁正
# @File : 科技.py
# @Software : PyCharm

from crawl_sohu import SohuSpider


def main():
    # 文章类型
    article_type = '科技'
    url_dict = {
        'https://www.sohu.com/xchannel/tag?key=%E7%A7%91%E6%8A%80-%E9%80%9A%E8%AE%AF': [article_type, '通讯'],
        'https://www.sohu.com/xchannel/tag?key=%E7%A7%91%E6%8A%80-%E6%95%B0%E7%A0%81': [article_type, '数码'],
        'https://www.sohu.com/xchannel/tag?key=%E7%A7%91%E6%8A%80-%E6%99%BA%E8%83%BD%E7%A1%AC%E4%BB%B6': [article_type,
                                                                                                          '智能硬件'],
    }
    spider = SohuSpider(url_dict)
    spider.spider_main()


if __name__ == '__main__':
    main()
