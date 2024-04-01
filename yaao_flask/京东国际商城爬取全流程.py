# -*- coding = utf-8 -*-
# @Time :  2023/12/18 10:31
# @Author : 梁正
# @File : 京东国际商城爬取全流程.py
# @Software : PyCharm
from markdown.extensions import attr_list
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import tkinter as tk
import pandas as pd
import random
import time
import re


def show_true_popup(message):
    """ 操作提示弹窗 """
    root = tk.Tk()
    root.title("True Message")

    # 设置窗口大小和位置
    window_width = 400
    window_height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = screen_width - window_width - 800  # 将窗口定位到右下角，留一定的边距
    y = screen_height - window_height - 600
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    # 将窗口设置为最顶层
    root.attributes('-topmost', True)
    label = tk.Label(root, text=message, padx=20, pady=20, font=("Arial", 16))
    label.pack()

    def close_popup():
        root.destroy()

    # 设置定时器，在3秒后调用关闭弹窗函数
    root.after(3000, close_popup)
    root.mainloop()


def jd_create_driver(user_data_dir):
    """ 创建chrome driver """
    options = webdriver.ChromeOptions()
    # 添加保持登录的数据路径：安装目录一般在C:\Users\****\AppData\Local\Google\Chrome\User Data
    # options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # options.add_argument(rf"user-data-dir={user_data_dir}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument("--disable-blink-features")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/120.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    # 模拟真实浏览器，防止被检测
    with open(r'stealth.min.js') as f:
        js = f.read()
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        "source": js
    })
    # driver.get(url=url)
    # 等待参数
    wait = WebDriverWait(driver, 5)
    return driver, wait


def jd_login(driver, wait, keyword):
    """ 登录操作 """
    driver.get('https://www.jd.hk/')
    time.sleep(1)
    # 登录按钮
    login_btn = driver.find_elements(By.CSS_SELECTOR, '#new-ttbar-login > a.link-logout')
    # 如果是未登录状态,须先人工扫码登录
    if len(login_btn) == 0:
        show_true_popup("信息过期，请人工扫码登录！")
        driver.find_element(By.CSS_SELECTOR, '#new-ttbar-login > a').click()
        time.sleep(1)
        # 转到新窗口
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        # 二维码按钮
        login_QR_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.login-form-body > div.login-tab.login-tab-l > a')))
        login_QR_btn.click()
        time.sleep(1)
        # 等待用户扫码操作（最多30秒）
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#key')))
    # 关键词输入
    keyword_input = driver.find_element(By.CSS_SELECTOR, '#key')
    keyword_input.clear()
    # 输入
    keyword_input.send_keys(keyword)
    # 模拟按下回车键
    keyword_input.send_keys(Keys.RETURN)
    time.sleep(3)

    # 模拟点击按销量排行
    sales_btn = driver.find_element(By.CSS_SELECTOR, '.filter_filter__WyDpV > div.topFilter_f-line__C2RLR.topFilter_top__Ly58e > div.topFilter_f-sort__iJE5o > button:nth-child(2)')
    sales_btn.click()
    time.sleep(1)


def jd_get_dir_info(driver, save_path_dir, store_num, keyword):
    """ 获取该关键词搜索页信息 """
    links = []
    titles = []
    main_pic_links = []
    stores = []
    evaluate_nums = []
    types = []

    # 模拟滚动操作
    actions = ActionChains(driver)
    actions.move_to_element(driver.find_element(By.TAG_NAME, 'body')).perform()
    time.sleep(1)
    while True:
        previous_position = driver.execute_script("return window.pageYOffset;")
        actions.send_keys(Keys.END).perform()
        time.sleep(1)
        current_position = driver.execute_script("return window.pageYOffset;")
        # 添加适当的等待时间，让页面有时间进行滚动
        time.sleep(1)
        # 拖到页面底部则跳出循环
        if current_position == previous_position:
            break

    # 商品标题和链接
    for l in driver.find_elements(By.CSS_SELECTOR,
                                  '#root > div:nth-child(6) > div.search_g-main1__ZCpBn > div > div > div.productList_goods-list__wMdJe.productList_item-style-v4__iIyve > ul > li:nth-child(n) > div:nth-child(2) > div > div.productList_p-name__eCbI6 > a'):
        links.append(l.get_attribute('href'))
        titles.append(l.text.strip().replace('京东国际', ''))

    # 主图链接
    for m in driver.find_elements(By.CSS_SELECTOR,
                                  '#root > div:nth-child(6) > div.search_g-main1__ZCpBn > div > div > div.productList_goods-list__wMdJe.productList_item-style-v4__iIyve > ul > li:nth-child(n) > div:nth-child(2) > div > div.productList_p-img__FGbqQ > a > div > img'):
        main_pic_link = m.get_attribute('src')
        main_pic_links.append(main_pic_link)

    # 店铺名称
    for s in driver.find_elements(By.CSS_SELECTOR,
                                  '#root > div:nth-child(6) > div.search_g-main1__ZCpBn > div > div > div.productList_goods-list__wMdJe.productList_item-style-v4__iIyve > ul > li:nth-child(n) > div:nth-child(2) > div > div.productList_p-shop-name__-JOwm > p > a:nth-child(1)'):
        stores.append(s.text.strip())

    # 评论数
    for e in driver.find_elements(By.CSS_SELECTOR,
                                  '#root > div:nth-child(6) > div.search_g-main1__ZCpBn > div > div > div.productList_goods-list__wMdJe.productList_item-style-v4__iIyve > ul > li:nth-child(n) > div:nth-child(2) > div > div.productList_p-buy__DEak9 > div > a > span > b'):
        evaluate_nums.append(e.text.strip())

    # 类型(自营或非自营)
    for t in driver.find_elements(By.CSS_SELECTOR,
                                  '#root > div:nth-child(6) > div.search_g-main1__ZCpBn > div > div > div.productList_goods-list__wMdJe.productList_item-style-v4__iIyve > ul > li:nth-child(n) > div:nth-child(2) > div > div.productList_p-icons__gFUWq'):
        content = t.text.strip()
        if '自营' in content:
            types.append('自营')
        else:
            types.append('非自营')

    # 将结果添加到 DataFrame 中
    all_data = pd.DataFrame({
        '关键词': keyword,
        '类型': types,
        '商品链接': links,
        '标题': titles,
        '店铺': stores,
        '评价数': evaluate_nums,
        '商品主图链接': main_pic_links,
        # '商品主图': main_pics,
    })
    # 根据字段类型匹配非自营的所有行
    filtered_data = all_data[all_data['类型'] == '非自营']
    # filtered_data = filtered_data[~filtered_data['店铺'].isin(['SmartMoney海外官方旗舰店', 'SpringRain海外官方旗舰店'])]
    forward_data = filtered_data.head(store_num)
    # 排名前store_num名的商品（store_num为排前几数）确保至少要有store_num个不同的店铺
    i = store_num
    if len(filtered_data) <= store_num:
        return filtered_data
    while len(forward_data['店铺'].drop_duplicates()) < store_num:
        i += 1
        forward_data = filtered_data.head(i)
    # 符合条件的店铺爬取齐全商品
    stores_list = forward_data['店铺'].drop_duplicates().tolist()
    filtered_data = filtered_data[filtered_data['店铺'].isin(stores_list)]
    # 按照店铺名称进行分组
    grouped_data = filtered_data.groupby('店铺').apply(lambda x: x.values.tolist())
    # 重新排列行顺序
    dir_data = pd.DataFrame([item for sublist in grouped_data.values for item in sublist],
                            columns=filtered_data.columns)

    # print(unique_data)
    # 将结果保存到 Excel 文件中
    dir_data.to_excel(rf'{save_path_dir}\jd-{keyword}-dir.xlsx', index=False)

    return dir_data


def jd_get_detail_info(url, title, driver, all_url):
    """ 获取单个详情页信息 """
    # global all_url
    if str(url) in all_url:
        return [], [], [], [], [], [], all_url
    driver.get(url=url)
    time.sleep(random.uniform(1.5, 2.5))
    if len(str(driver.current_url)) > 50:
        show_true_popup("请人工处理")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#key')))
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#key')))
    except TimeoutException:
        show_true_popup("请人工登录")
        # 二维码按钮
        # login_QR_btn = WebDriverWait(driver, 3).until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, '.login-form-body > div.login-tab.login-tab-l > a')))
        # login_QR_btn.click()
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#key')))

    sku_id_list = []
    sku_name_list = []
    QR_pic_link_list = []
    product_link_list = []
    main_pic_list = []

    # # 判断是否有发货区域信息
    # judge = driver.find_elements(By.CSS_SELECTOR, '.summary-service > .hl_red')
    # i = 0
    # while not judge:
    #     i += 1
    #     if i == 8:
    #         return [], [], [], [], [], [], all_url
    #     driver.refresh()
    #     time.sleep(2)
    #     if len(str(driver.current_url)) > 50:
    #         show_true_popup("请人工处理")
    #         WebDriverWait(driver, 30).until(
    #             EC.presence_of_element_located(
    #                 (By.CSS_SELECTOR, '#key')))
    #     judge = driver.find_elements(By.CSS_SELECTOR, '.summary-service > .hl_red')
    # # if judge and '京东国际' not in judge[0].text:
    # #     return sku_name_list, sku_id_list, product_link_list, QR_pic_link_list, main_pic_list, []
    # # 发货地
    # place = driver.find_element(By.CSS_SELECTOR, '.summary-service')
    # place = re.sub(r'由.*?从', '', place.text.strip().split('发货,')[0])
    # place = place.replace('由', '')

    place = 'None'
    # SKU编号列表和属性名称
    for s in driver.find_elements(By.CSS_SELECTOR, '#choose-attr-1 > div.dd > div.item'):
        sku_id_list.append(s.get_attribute('data-sku'))
        sku_name_list.append(s.text.strip())
    # 如果没有SKU编号列表，构造处理
    if not sku_id_list:
        sku_id_list.append(str(url).split('hk/')[-1].replace('.html', ''))
        sku_name_list.append(title)
        main_pic_list.append(driver.find_element(By.CSS_SELECTOR, '#spec-img').get_attribute('src'))
    # 主图链接
    for p in driver.find_elements(By.CSS_SELECTOR, '#choose-attr-1 > div.dd > div.item > a > img'):
        main_pic_list.append(
            p.get_attribute('src').replace('s40x40_jfs', 's100x100_jfs') if 's40x40_jfs' in p.get_attribute(
                'src') else p.get_attribute('src'))
    # 构造二维码链接和商品链接
    for sku in sku_id_list:
        QR_pic_link_list.append(
            f'https://qrimg.jd.com/https%3A%2F%2Fitem.m.jd.com%2Fproduct%2F{sku}.html%3Fpc_source%3Dpc_productDetail_{sku}-118-1-4-2.png')
        product_link_list.append(f'https://npcitem.jd.hk/{sku}.html')
        # all_url.append(f'https://npcitem.jd.hk/{sku}.html')

    all_url += product_link_list

    print(place)
    print(sku_name_list)
    print(sku_id_list)
    print(QR_pic_link_list)
    print(product_link_list)
    print(main_pic_list)
    print(len(sku_name_list), len(sku_id_list), len(product_link_list), len(QR_pic_link_list), len(main_pic_list), len(all_url))
    print(all_url)

    return sku_name_list, sku_id_list, product_link_list, QR_pic_link_list, main_pic_list, place, all_url


def jd_get_all_data(dir_data, driver, all_url, keyword):
    """ 获取包括多个详情页内的所有信息 """
    url_list = dir_data['商品链接']
    title_list = dir_data['标题']
    store_list = dir_data['店铺']
    evaluate_num_list = dir_data['评价数']
    all_data = pd.DataFrame(
        columns=['二维码链接', '主图链接', '关键词', '商品链接', '标题', '店铺', '发货地', '评论数', 'SKU', '属性'])
    for url, title, store, evaluate_num in zip(url_list, title_list, store_list, evaluate_num_list):
        sku_name_list, sku_id_list, product_link_list, QR_pic_link_list, main_pic_list, place, all_url = jd_get_detail_info(url, title, driver, all_url)
        half_data = pd.DataFrame({
            '二维码链接': QR_pic_link_list,  #[0]] + ['\\'] * (len(sku_id_list) - 1) if QR_pic_link_list else QR_pic_link_list,
            '主图链接': main_pic_list,
            '关键词': keyword,
            '商品链接': product_link_list,
            '标题': [f'{title}'] * len(sku_id_list) if sku_id_list else sku_id_list,
            '店铺': [f'{store}'] * len(sku_id_list) if sku_id_list else sku_id_list,
            '发货地': [f'{place}'] * len(sku_id_list),
            '评论数': [f'{evaluate_num}'] * len(sku_id_list) if sku_id_list else sku_id_list,
            'SKU': sku_id_list,
            '属性': sku_name_list,

        })
        all_data = pd.concat([all_data, half_data], ignore_index=True)
    print(f"详情页数据已爬完")

    print(all_data.tail(5))
    # 查看重复值
    print(f'数据中有%d条重复数据' % all_data.duplicated().sum())
    # 删除重复数据
    all_data.drop_duplicates(inplace=True)

    return all_data


def set_shop_index(df):
    shop_index = {}  # 用于存储每个店铺对应的索引
    index = 1
    index_list = []
    for i in range(len(df)):
        # shop_name = df.loc[i, '店铺']  # 假设你的列名为'店铺'
        shop_name = df['店铺'].tolist()[i]
        if shop_name not in shop_index:
            shop_index[shop_name] = index
            index += 1
        # df.loc[i, '索引'] = shop_index[shop_name]  # 添加一个名为'索引'的新列，存储索引值
        index_list.append(shop_index[shop_name])

    df.insert(2, '索引', index_list)  # 将新的'索引'列移动到第一列

    return df


def jd_filter_data(white_list, black_list, all_data):
    if len(black_list) == 1 and black_list[0] == '':
        black_list = []
    else:
        black_list = black_list.split(' ')
    if len(white_list) == 1 and white_list[0] == '':
        white_list = []
    else:
        white_list = white_list.split(' ')
    if not white_list and not black_list:  # 当白名单和黑名单均为空时
        filter_data = all_data.copy()
    else:
        filter_data = all_data.copy()  # 创建过滤后的数据副本
        if white_list:  # 如果白名单不为空
            white_list = [re.escape(item) for item in white_list]
            white_filter = filter_data['属性'].str.contains('|'.join(white_list), case=False, na=False)
            filter_data = filter_data[white_filter]
        if black_list:  # 如果黑名单不为空
            black_list = [re.escape(item) for item in black_list]
            black_filter = filter_data['属性'].str.contains('|'.join(black_list), case=False, na=False)
            filter_data = filter_data[~black_filter]
    # 将筛选后的数据保存到 Excel 文件中
    filter_data.drop_duplicates(subset="SKU", keep="first", inplace=True)
    filter_data1 = set_shop_index(filter_data)
    filter_data1['索引'] = filter_data1['索引'].apply(lambda x: int(x))

    return filter_data1


def jd_filter_save_data(white_list, black_list, save_path_dir, keyword, all_data):
    """ 根据黑白名单中的关键词匹配筛选并保存数据 """

    if not white_list and not black_list:  # 当白名单和黑名单均为空时
        filter_data = all_data.copy()

    else:
        filter_data = all_data.copy()  # 创建过滤后的数据副本
        if white_list:  # 如果白名单不为空
            white_list = [re.escape(item) for item in white_list]
            white_filter = filter_data['属性'].str.contains('|'.join(white_list), case=False, na=False)
            filter_data = filter_data[white_filter]
        if black_list:  # 如果黑名单不为空
            black_list = [re.escape(item) for item in black_list]
            black_filter = filter_data['属性'].str.contains('|'.join(black_list), case=False, na=False)
            filter_data = filter_data[~black_filter]
    # 将筛选后的数据保存到 Excel 文件中
    filter_data.drop_duplicates(subset="SKU", keep="first", inplace=True)
    filter_data1 = set_shop_index(filter_data)
    filter_data1['索引'] = filter_data1['索引'].apply(lambda x: int(x))
    # filter_data.drop_duplicates(inplace=True)
    filter_data1.to_excel(rf'{save_path_dir}\jd-{keyword}.xlsx', index=False)
    return filter_data1


def jd_show_on_html(save_path_dir, keyword, filter_data):
    """ 将数据展示在html网页上 """

    def main_pic_to_html(image_url):
        return f'<img src="{image_url}" height=150 width=150 alt="">'

    def qr_link_to_html(image_url):
        return f'<img src="{image_url}" height=120 width=120 alt="">'

    def link_html(link_url):
        return f'<a href="{link_url}">{link_url}</a>'

    # 创建一个新的 DataFrame，同时插入空白列
    modified_data = filter_data.copy()
    modified_data['价格1'] = ''
    modified_data['价格2'] = ''
    modified_data['价格3'] = ''
    modified_data['价格4'] = ''
    modified_data['价格5'] = ''
    modified_data['价格6'] = ''

    # 将 DataFrame 导出为 HTML 文件，并在指定字段上应用自定义函数
    modified_data['二维码链接'] = modified_data['二维码链接'].apply(qr_link_to_html)
    modified_data['主图链接'] = modified_data['主图链接'].apply(main_pic_to_html)
    modified_data['商品链接'] = modified_data['商品链接'].apply(link_html)

    # 重新设置索引
    # modified_data.reset_index(drop=True, inplace=True)
    # 将 DataFrame 转换为 HTML 字符串
    html_content = modified_data.to_html(index=False, escape=False)

    # 在导出 HTML 文件之前，将包含 DataFrame 内容的字符串进行处理
    html_header = r"""
    <!DOCTYPE html>
    <html>
    <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>填价格</title>
        <script src="C:/Users/EDY/PycharmProjects/pythonProject/work/yaao_flask/bignumber.min.js"></script>
        <style>
            #exportContainer {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                padding: 10px;
                background-color: #f1f1f1;
                border: 1px solid #ddd;
                z-index: 1000;
            }
            #exportButton, #clearButton{
                font-size: 18px;
                padding: 10px 20px;
                margin-right: 10px;
            }
            .logo{
                margin-left: 10px;
                margin-top: 8px;
                margin-right: 370px;
            }
            #filenameInput {
                font-size: 16px;
                padding: 8px;
                width: 400px;
                margin-right: 10px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 70px; /* 调整这个值来控制表格整体往下移动的距离 */
            }
            th, td {
                padding: 8px;
                text-align: left;
                max-width: 150px;  /* 设置每个td的最大宽度 */
                max-height: 100px;  /* 设置每个td的最大高度 */
                overflow: hidden;   /* 超出部分隐藏 */
                text-overflow: ellipsis;  /* 超出部分显示省略号 */
            }
            thead {
                position: sticky;
                top: 70px;
                background-color: #cccccc;
            }
            .fill-input {
                margin-bottom: 25px; /* 控制输入框上下距离 */
                font-size: 18px; /* 控制输入文本字体大小 */
                color: red; /* 控制输入字体颜色 */
                width: 100%;
            }
        </style>
    </head>
    <body>
        <div id="exportContainer">
            <a href="https://www.jd.hk" class="logo" >
              <img class="logo" src="https://eimg.smzdm.com/201911/21/5dd6a6c24f05c1763.png" height=30 width=150 alt=""></a>
            <input type="text" id="filenameInput" placeholder="文件名 (不填则取当前时刻命名)">
            <button id="exportButton">导出为csv</button>
            <button id="clearButton">一键清空价格</button>

        </div>
    <table border="1" class="dataframe">
        """

    html_tail = r"""
    </table>
    </body>
    <script>
    // 在页面加载完成时执行的函数
    window.addEventListener('load', function() {
      // 获取所有带有类名"fill-input"的<input>元素
      var inputElements = document.querySelectorAll('.fill-input');

      // 为每个<input>元素设置不同的id
      inputElements.forEach(function(inputElement, index) {
        inputElement.id = 'input-' + (index + 1);
      });

      // 从本地存储中获取之前保存的值，并将其赋值给<input>的value属性
      inputElements.forEach(function(inputElement) {
        var savedValue = localStorage.getItem(inputElement.id + '-value');
        if (savedValue) {
          inputElement.value = savedValue;
        }

        // 监听<input>的输入事件，当输入改变时保存新的值到本地存储
        inputElement.addEventListener('input', function(event) {
          var newValue = event.target.value;
          localStorage.setItem(event.target.id + '-value', newValue);
        });
      });

      // 添加事件监听器以导出数据
      var exportButton = document.getElementById('exportButton');
      exportButton.addEventListener('click', function() {
        exportToExcel();
      });
    });
      // 添加清空按钮的点击事件处理程序
      var clearButton = document.getElementById('clearButton');
      clearButton.addEventListener('click', function() {
        clearInputs();
    });

    // 清空输入框和本地存储的值
    function clearInputs() {
      var inputElements = document.querySelectorAll('.fill-input');
      inputElements.forEach(function(inputElement) {
        inputElement.value = '';
        localStorage.removeItem(inputElement.id + '-value');
      });
    }
    // 导出数据到Excel
    function exportToExcel() {
      var headers = ['', '索引', '关键词', '商品链接', '标题', '店铺', '发货地', '评论数', 'SKU', '属性', '价格1', '价格2', '价格3', '价格4', '价格5', '价格6', '周成交单量', '月成交单量']; // 替换成你的实际字段名
      var csvContent = "data:text/csv;charset=utf-8";

      var data = [];
      var price_data = [];
        // 获取<input>元素的值
      var inputElements = document.querySelectorAll('.fill-input');
      inputElements.forEach(function(inputElement) {
        price_data.push(inputElement.value);
      });
      // 获取商品行<tr>元素
      var productRows = document.body.querySelector('tbody').querySelectorAll('tr');
      productRows.forEach(function(row) {
        var rowData = [];
        // 获取<tr>中的第1到第6个<td>的值
        var tableData = row.querySelectorAll('td');
        for (var i = 2; i <= 10; i++) {
          var cellValue = tableData[i].innerText;
          // 如果 cellValue 是数值型且是大数字
          if (!isNaN(cellValue) && parseInt(cellValue) > Number.MAX_SAFE_INTEGER) {
            var bigNum = new BigNumber(cellValue);
            rowData.push(bigNum.toString());
          } else {
            rowData.push(cellValue);
          }
        }
        // 将价格字段添加到rowData中
        var rowIndex = Array.from(productRows).indexOf(row);
        rowData.push(price_data.slice(rowIndex * 6, rowIndex * 6 + 6));
        // 将rowData添加到data列表
        data.push(rowData.join(','));
      });
      // 添加表头
      csvContent += headers.join(',') + '\n';
      // 添加数据
      csvContent += data.join('\n'); // 每行的数据换行
      var filenameInput = document.getElementById('filenameInput');
      // 获取当前时间
      var currentTime = new Date().toLocaleString();
      var keyword = document.querySelector('tr td:nth-child(4)').innerText;
      // 使用用户输入的文件名，如果输入框为空则使用当前时间作为默认名称
      var filename = filenameInput.value.trim() || keyword + currentTime;
      
      // 创建一个链接并点击进行下载
      var encodedUri = encodeURI(csvContent);
      var link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", filename + ".csv");
      document.body.appendChild(link);
      // 模拟点击下载链接
      link.click();
      document.body.removeChild(link); // 下载完成后移除链接
    }
    </script>
    </html>
        """
    # 添加html头部代码
    html_content = html_content.replace('<table border="1" class="dataframe">', html_header)

    # 在 HTML 的表格行中插入 input 元素，并为 input 元素添加 class属性
    html_content = html_content.replace(
        '<td></td>',
        '<td><input class="fill-input" type="text"></td>'
    )
    # 添加html尾部代码
    html_content = html_content.replace('</table>', html_tail)
    # 将处理后的 HTML 字符串保存为 HTML 文件
    with open(rf'{save_path_dir}\jd-{keyword}.html', 'w', encoding='utf-8') as file:
        file.write(html_content)
    return html_content


if __name__ == '__main__':
    all_url = []
    # 爬取关键词（自行更改）
    keyword = 'a2 成人奶粉全脂'
    # 需要销量前几个店铺(修改数字)
    store_num = 7
    # 筛选关键词-黑名单和白名单，列表可为空、（自行更改）
    black_list = []
    white_list = []
    # 保存路径--文件夹（自行更改）
    save_path_dir = rf'C:\Users\EDY\Desktop\data\JD'
    # 添加保持登录的数据路径：安装目录一般在C:\Users\****\AppData\Local\Google\Chrome\User Data
    user_data_dir = r"C:\Users\EDY\AppData\Local\Google\Chrome\User Data"

    # 创建浏览器驱动和等待参数
    driver, wait = jd_create_driver(user_data_dir)
    # 登录操作（登录信息失效则须人工介入扫码）
    jd_login(driver, wait, keyword)
    # 先获取搜索页信息
    dir_data = jd_get_dir_info(driver, save_path_dir, store_num, keyword)
    # # 获取包括详情页内的所有信息
    all_data = jd_get_all_data(dir_data, driver, all_url, keyword)
    # 关闭浏览器
    driver.close()
    # 筛选并保存数据
    filter_data = jd_filter_save_data(white_list, black_list, save_path_dir, keyword, all_data)
    # 生成html文件
    html_content = jd_show_on_html(save_path_dir, keyword, filter_data)
