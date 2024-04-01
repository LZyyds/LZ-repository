# -*- coding = utf-8 -*-
# @Time :  2024/3/30 21:06
# @Author : 梁正
# @File : public_funs.py
# @Software : PyCharm

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
from retrying import retry
from tqdm import tqdm
import pandas as pd
import requests
import pymysql
import json
import time
import os


# 声明一个变量来记录重试的次数
retry_num = 0
failed_links = []


def create_headers_and_driver():
    """
    创建浏览器请求头和chrome driver
    :return: 请求头、浏览器驱动
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/122.0.0.0 Safari/537.36'
    }

    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={headers['User-Agent']}")
    driver = webdriver.Chrome(options=chrome_options)

    return headers, driver


def get_list_data(url, inner_lable, driver):
    """
    获取目标站点列表页动态数据
    :param url: 不同栏目站点信息
    :param inner_lable: 二级标签
    :param driver: 浏览器驱动
    :return: 链接列表、主图列表、阅读量列表
    """
    # 访问目标url
    driver.get(url)
    # 等待网页页面加载
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.TPLImageTextFeedItem')))

    # 模拟滚动操作
    actions = ActionChains(driver)
    actions.move_to_element(driver.find_element(By.TAG_NAME, 'body')).perform()
    time.sleep(0.5)
    while True:
        previous_position = driver.execute_script("return window.pageYOffset;")
        actions.send_keys(Keys.END).perform()
        time.sleep(1)
        current_position = driver.execute_script("return window.pageYOffset;")
        # 添加适当的等待时间，让页面有时间进行滚动
        time.sleep(1.7)
        # 拖到页面底部则跳出循环
        if current_position == previous_position:
            break

    # 使用BeautifulSoup解析网页源代码
    dom = BeautifulSoup(driver.page_source, 'lxml')

    link_list = []
    main_pic_list = []
    read_num_list = []
    for item in dom.select('.TPLImageTextFeedItem'):
        # 如果域名中没有'sohu'说明是广告链接，跳过
        if 'sohu' not in item.select_one('a')['href'].split('?scm')[0]:
            continue
        link_list.append(item.select_one('a')['href'].split('?scm')[0])
        main_pic_list.append(
            item.select_one('a > .item-img-content > img')['src'] if item.select_one('a > .item-img-content > img')['src']
            else 'https://tse4-mm.cn.bing.net/th/id/OIP-C.FzAP0Vt-mAdHvqJyM01TPgAAAA?w=172&h=180&c=7&r=0&o=5&pid=1.7')
        read_num_list.append(
            item.select_one('div > div > span:nth-last-child(1)').text.replace('阅读', '') if item.select_one(
                'div > div > span:nth-last-child(1)') is not None and '阅读' in item.select_one(
                'div > div > span:nth-last-child(1)').text else '0')

    read_num_list = [int(i.replace('万', '').replace('+', '').replace('.', '').strip() + '000')
                     if '万' in i else int(i) for i in read_num_list]

    print(f"【{inner_lable}】 一共有 {len(link_list)} 条文章链接")
    # print(link_list)
    # print(main_pic_list)
    # print(read_num_list)

    return link_list, main_pic_list, read_num_list


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def _get_web_data(link, headers):
    """
    获取解析详情页文章数据
    :param link: 单个文章详情页链接
    :param headers: 请求头
    :return: 正文、标题、媒体、发布时间、发布省份
    """
    # 根据链接爬取正文信息
    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    response.close()

    # 正文信息
    article_div = soup.select_one(".article," ".article-text")
    if article_div is not None:
        paragraph_list = [p.text.strip() for p in article_div.find_all("p") if
                          "original-title" not in p.get('data-role', [])]
    else:
        paragraph_list = []

    # 正文处理空行格式
    text = "\n".join(paragraph_list)
    text = '\t' + text.replace("\n\n", "\n").replace("\n\n\n", "\n").replace("\n", "\n\t").replace("\n\t\n\t",
                                                                                                   "\n").strip()
    text = text.split('\n\t推荐阅读')[0].split('\n\t责任编辑')[0].replace('返回搜狐，查看更多', '')
    # text = re.sub(r'原标题.*?\n\t', '', text, count=1)

    # 标题
    title_element = soup.select_one(".text-title > h1," "body > div.content.area > div.article-box.l > h3")
    if title_element is not None:
        title = title_element.text.strip()
        if '原创' in title:
            title = '(原创)' + title.replace('原创', '').strip()
    else:
        title = ''

    # 媒体
    media_element = soup.select_one(
        "#user-info > h4 > a," "#article-container > div.left.main > div:nth-child(1) > div > div.text-title > "
        "div > span:nth-child(2),"
        "body > div.content.area > div.aside.r > div.aside-item.right-author-box.mt10 > "
        "div.right-author-info.clearfix > div > a.name.l")
    if media_element is not None:
        media = media_element.text.replace('来源:', '').strip()
    else:
        media = ''

    # 发布时间
    time_element = soup.select_one("#news-time," ".article-box.l > p.article-info.clearfix > span")
    if time_element is not None:
        article_time = time_element.text.replace('编辑于', '').strip()
    else:
        article_time = ''

    # 发布省份
    area_element = soup.select_one(".text-title > div > div > span:nth-child(2)")
    if area_element is not None:
        area = area_element.text.strip()
    else:
        area = ''

    return text, title, media, article_time, area


def get_web_data(link, headers):
    """
    调用_get_web_data函数，加入访问重试机制
    """
    global retry_num  # 声明引用全局变量
    global failed_links
    try:
        text, title, media, article_time, area = _get_web_data(link, headers)
        return text, title, media, article_time, area
    except Exception as e:
        if retry_num < 3:
            retry_num += 1
            print(f"链接:{link} 异常，错误信息，正在重试···")
            return get_web_data(link, headers)  # 递归调用自身进行重试
        else:
            print(f"链接:{link} 异常，重试次数用尽。错误信息:{str(e)}。")
            failed_links.append(link)
            retry_num = 0  # 重试次数清零
            return '', '', '', '', ''


def process_datetime_column(data, column_name):
    """
    处理时间格式
    :param data: 数据表
    :param column_name: 字段名
    :return:
    """
    data[column_name] = data[column_name].str.slice(0, 16)
    data[column_name] = pd.to_datetime(data[column_name], format='%Y-%m-%d %H:%M')
    data[column_name] = data[column_name].dt.strftime('%Y-%m-%d %H:%M:%S')
    data[column_name] = data[column_name].replace('', pd.NaT)
    data[column_name] = data[column_name].fillna('2024-01-01 00:00:00')


def mult_process_and_save(headers, all_link_list, all_main_pic_list, all_read_num_list, outer_lable_list,
                          inner_lable_list):
    """
    多线程处理函数、并保存数据至excel
    :param headers: 请求头
    :param all_link_list: 所有文章链接列表
    :return: 总数据表
    """
    # all_data = pd.DataFrame(columns=['类别', '栏目', '标题', '链接', '媒体', '正文', '发布时间', '发布省份'])
    with ThreadPoolExecutor() as executor:
        pbar = tqdm(total=len(all_link_list), desc=f"{outer_lable_list[0]} 爬取进度")

        def get_web_data_with_progress(link, headers):
            result = get_web_data(link, headers)
            # 更新进度条
            pbar.update(1)
            return result

        results = list(executor.map(get_web_data_with_progress, all_link_list, [headers] * len(all_link_list)))

        data = pd.DataFrame(results, columns=['正文', '标题', '媒体', '发布时间', '发布省份'])
        all_data = pd.DataFrame({
            '类别': outer_lable_list,
            '栏目': inner_lable_list,
            '链接': all_link_list,
            '主图链接': all_main_pic_list,
            '阅读数量': all_read_num_list,
            '标题': data['标题'],
            '正文': data['正文'],
            '媒体': data['媒体'],
            '发布省份': data['发布省份'],
            '发布时间': data['发布时间']
        })

    process_datetime_column(all_data, '发布时间')
    # print(all_data.tail(5))
    print(f'{outer_lable_list[0]}文章数据中有%d条重复数据' % all_data.duplicated().sum())

    file_path = rf'D:\桌面\毕业设计\spider_data\{outer_lable_list[0]}.xlsx'
    if os.path.exists(file_path):
        # 读取已存在的Excel文件
        existing_data = pd.read_excel(file_path)
        # 将新数据追加到已有数据后面
        excel_all_data = pd.concat([existing_data, all_data], ignore_index=True)
        print(f'文章数据中有%d条重复数据' % all_data.duplicated().sum())
        # 删除重复数据
        excel_all_data.drop_duplicates(inplace=True)
        # 将合并后的数据写入Excel文件
        excel_all_data.to_excel(file_path, index=False)
    else:
        # 如果文件不存在，直接创建新文件并保存数据
        all_data.to_excel(file_path, index=False)

    return all_data


def save_to_mysql(all_data, table_name, database_name):
    """
    保存数据到MySQL数据库
    :param all_data: 总数据表
    :param table_name: 表名
    :param database_name: 数据库名
    """
    # 创建数据库连接
    conn = pymysql.connect(host='localhost', user='root', password='123456', database=database_name, charset='utf8mb4')
    cursor = conn.cursor()

    # 构建CREATE TABLE语句
    create_table_sql = f"""
   CREATE TABLE IF NOT EXISTS {table_name} (
      id INT AUTO_INCREMENT PRIMARY KEY,
      `类别` VARCHAR(255),
      `栏目` VARCHAR(255),
      `链接` VARCHAR(255) NOT NULL,
      UNIQUE (`链接`),
      `主图链接` VARCHAR(500),
      `阅读数量` INT,
      `标题` TEXT,
      `正文` TEXT,
      `媒体` VARCHAR(255),
      `发布省份` VARCHAR(255),
      `发布时间` DATETIME
   ) DEFAULT CHARACTER SET utf8mb4;
   """

    # 执行CREATE TABLE语句
    cursor.execute(create_table_sql)

    # 将 DataFrame 转换为列表
    data_list = all_data.values.tolist()
    # 插入数据语句
    insert_statement = f"INSERT INTO {table_name} (`类别`,`栏目`,`链接`,`主图链接`,`阅读数量`,`标题`,`正文`,`媒体`,`发布省份`,`发布时间`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    # 批量插入数据，遇到异常则跳过当前行
    for data in data_list:
        try:
            cursor.execute(insert_statement, data)
            conn.commit()
        except Exception as e:
            print(f"插入数据{data[2]}时发生异常：{e}.跳过当前行继续插入下一行数据。")
            conn.rollback()
    # 关闭游标和连接
    cursor.close()
    conn.close()


def spider_main(url_dict):
    """
    爬虫主函数
    :param url_dict: 待爬取的信息字典
    """
    # 获取请求头、创建 webdriver 对象并启动 Chrome
    headers, driver = create_headers_and_driver()
    start_time = datetime.now()
    # 创建一个字典来存储数据
    data_dict = {}

    # 循环获取不同栏目的目录页信息
    for url, label in url_dict.items():
        link_list, main_pic_list, read_num_list = get_list_data(url, label[1], driver)
        for i in range(len(link_list)):
            link = link_list[i]
            if link not in data_dict:
                data_dict[link] = {
                    "main_pic": main_pic_list[i],
                    "read_num": read_num_list[i],
                    "outer_label": label[0],
                    "inner_label": label[1]
                }

    end_time = datetime.now()
    cost_time = end_time - start_time
    outer_label = str(url_dict).split("',")[0].split("['")[-1]
    print(f'selenium爬取【{outer_label}】目录页一共花了{cost_time.total_seconds()}秒')
    # 退出chromedriver
    driver.quit()

    # 判断是否存在crawled_links.json，没有则创建并写入空列表
    if not os.path.exists('crawled_links.json'):
        with open('crawled_links.json', 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    # 读取crawled_links.json文件内容
    with open('crawled_links.json', 'r', encoding='utf-8') as f:
        crawled_links = json.load(f)

    # 通过历史记录对比，拿到本次爬取新文章链接列表
    new_links = [link for link in data_dict.keys() if link not in crawled_links]
    print(f" 本次爬取 {len(data_dict)} 条文章链接中，有 {len(new_links)} 条新链接···")

    # 追加新的链接到JSON文件中
    if new_links:
        with open('crawled_links.json', 'w', encoding='utf-8') as f:
            crawled_links.extend(new_links)
            json.dump(crawled_links, f, ensure_ascii=False, indent=4)

        new_main_pic_list = [data_dict[link]['main_pic'] for link in new_links]
        new_read_num_list = [data_dict[link]['read_num'] for link in new_links]
        outer_lable_list = [data_dict[link]['outer_label'] for link in new_links]
        inner_lable_list = [data_dict[link]['inner_label'] for link in new_links]

        # 多线程爬取全部详情页内容
        all_data = mult_process_and_save(headers, new_links, new_main_pic_list, new_read_num_list, outer_lable_list,
                                         inner_lable_list)
        # 数据库名和表名
        database_name = "sohu"
        # table_name = "test"
        table_name = outer_label

        # 保存到MySQL的函数
        save_to_mysql(all_data, table_name, database_name)
        print("爬取失败的文章链接列表: ", failed_links)
    else:
        print(f"本次爬取【{outer_label}】目录页无新数据产生···")
