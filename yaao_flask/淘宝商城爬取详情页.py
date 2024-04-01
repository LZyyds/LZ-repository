from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
import tkinter as tk
import pandas as pd
import pyautogui
import itertools
import random
import base64
import time


def create_driver(user_data_dir):
    """ 创建chrome driver """
    # pyautogui.hotkey('ctrl', 'alt', '0')
    # time.sleep(2)
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # 添加保持登录的数据路径：安装目录一般在C:\Users\****\AppData\Local\Google\Chrome\User Data
    # options.add_argument(rf"user-data-dir={user_data_dir}")
    # options.add_experimental_option("debuggerAddress", "127.0.0.1:9221")
    # options.add_argument("--start-maximized")
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
    # 等待参数
    wait = WebDriverWait(driver, 5)

    return driver, wait


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


def get_tb_info(url, title, driver):
    """ 获取淘宝网页格式的单个详情页数据 """
    driver.get(url=url)
    # time.sleep(50)
    time.sleep(random.uniform(0.3, 0.7))
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#J_tbExtra > dl > dd,' '.BasicContent--sku--6N_nw6c')))
    except:
        show_true_popup("请人工处理")
        WebDriverWait(driver, 70).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#J_tbExtra > dl > dd,' '.BasicContent--sku--6N_nw6c')))
    # print(driver.current_url)
    # 判断该网页是新版还是旧版
    if 'isNew=false' in str(driver.current_url):
        SellCounter, is_tax, sku_types, QR_pic_url, place = old_tb_info(title, driver)
    else:
        SellCounter, is_tax, sku_types, QR_pic_url, place = new_tb_info(title, driver)

    return SellCounter, is_tax, sku_types, QR_pic_url, place


def new_tb_info(title, driver):
    """ 新版淘宝网页格式的单个详情页数据 """
    # 防止验证码干扰，预留人工处理时间
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.BasicContent--sku--6N_nw6c')))
    except:
        show_true_popup("请人工处理")
        login_btn = driver.find_element(By.CSS_SELECTOR,
                                        '.SecurityContent--rightTips--3nPyDzP > div.SecurityContent--loginBtn--28e5PZf')
        login_btn.click()
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.BasicContent--sku--6N_nw6c')))

    property_type = []
    capacity_type = []
    time.sleep(0.5)
    is_bannar = driver.find_elements(By.CSS_SELECTOR, 'body > div.J_MIDDLEWARE_FRAME_WIDGET > iframe,' '#baxia-punish,'
                                     '#bg-img,' '#bx-feedback-btn')
    # if len(is_bannar) > 0:
    #     show_true_popup("请人工处理")
    #     time.sleep(8)
    while driver.find_elements(By.CSS_SELECTOR, 'body > div.J_MIDDLEWARE_FRAME_WIDGET > iframe,' '#baxia-punish,'
                                     '#bg-img,' '#bx-feedback-btn'):
        show_true_popup("请人工处理")
        time.sleep(5)
    # 月销量
    SellCounter = driver.find_element(By.CSS_SELECTOR, '.ItemHeader--root--DXhqHxP > div > span')
    SellCounter = SellCounter.text.strip()
    # 定位要悬停的元素
    param_btn = driver.find_element(By.CSS_SELECTOR, ".Promotion--root--3qHQalP > div.Promotion--trigger--1jNnEEI")
    # 使用ActionChains模拟鼠标悬停操作
    ActionChains(driver).move_to_element(param_btn).perform()
    # 判断并构造是否保税区发货字段
    tb_extra = driver.find_elements(By.CSS_SELECTOR,
                                    '.Promotion--leftPanel--3PvKA-7 > div:nth-child(n) > span.Promotion--caption--1nq0p3r')
    if '保税' in tb_extra[-1].text.strip():
        is_tax = '保税区发货'
    elif '海外直邮' in tb_extra[-1].text.strip():
        is_tax = '海外直邮'
    else:
        is_tax = '一般贸易'

    # 发货地
    place = driver.find_elements(By.CSS_SELECTOR,
                                 '#root > div > div.Item--main--1sEwqeT > div.Item--content--12o-RdR > div.BasicContent--root--1_NvQmc > div > div.BasicContent--itemInfo--2NdSOrj > div.MCDelivery > div.delivery-content > div.delivery-content-inner > div.delivery-from-addr')
    if place:
        place = place[0].text.strip().replace('至', '')

    # 类型（罐型）列表
    for p in driver.find_elements(By.CSS_SELECTOR,
                                  'div.skuWrapper > div > div:nth-child(1) > div:nth-child(1) > div > div:nth-child(n) > div > span'):
        property_type.append(p.text.strip())
    # 容量列表
    for c in driver.find_elements(By.CSS_SELECTOR,
                                  '.BasicContent--sku--6N_nw6c > div > div > div:nth-child(1) > div:nth-child(2) > div > div:nth-child(n) > div > span'):
        capacity_type.append(c.text.strip())

    # 如果这两个列表均不为空，排列组合构造SKU列表；其中一个为空则将另一列表直接赋值给SKU列表
    if property_type and capacity_type:
        sku_types = [f'{x} {y}' for x, y in itertools.product(property_type, capacity_type)]
    else:
        sku_types = property_type or capacity_type
    # print('SKU列表:', sku_types)
    data_property = driver.find_elements(By.CSS_SELECTOR,
                                         '#root > div > div.Item--main--1sEwqeT > div.Item--content--12o-RdR > div.BasicContent--root--1_NvQmc > div > div.BasicContent--itemInfo--2NdSOrj > div.BasicContent--sku--6N_nw6c > div > div > div:nth-child(1) > div:nth-child(1) > span')
    if data_property and '颜色分类' in data_property[0].text:
        sku_types = [f'{title}']
    # 如果没有款式选择区域，则用标题
    if not sku_types:
        sku_types.append(title)

    # print(SellCounter, place, is_tax, sku_types, QR_pic_url, sep='\n')
    # 定位要悬停的元素
    QR_btn = driver.find_element(By.CSS_SELECTOR, "#J_Toolkit > div > div > div.toolkit-item.toolkit-item-qrcode")
    # 使用ActionChains模拟鼠标悬停操作
    ActionChains(driver).move_to_element(QR_btn).perform()
    time.sleep(random.uniform(0.8, 1))
    # 定位到指定元素
    QR_element = driver.find_element(By.CSS_SELECTOR, '.toolkit-item.toolkit-item-qrcode > div > div > canvas')

    # 获取元素的位置和大小
    location = QR_element.location
    size = QR_element.size
    # 截取指定元素区域的截图
    screenshot_base64 = driver.get_screenshot_as_base64()
    time.sleep(0.5)
    img = Image.open(BytesIO(base64.b64decode(screenshot_base64)))
    time.sleep(0.5)
    left = location['x']
    top = location['y']
    right = left + size['width']
    bottom = top + size['height']
    # print(left, top, right, bottom)
    img = img.crop((left, top, right, bottom))

    # 将截图转换为 Base64 编码
    buffered = BytesIO()
    try:
        img.save(buffered, format="PNG")
        screenshot_base64_cropped = base64.b64encode(buffered.getvalue()).decode('utf-8')
        # print('data:image/png;base64,' + str(screenshot_base64_cropped))
        QR_pic_url = 'data:image/png;base64,' + str(screenshot_base64_cropped)
    except:
        QR_pic_url = 'https://tse4-mm.cn.bing.net/th/id/OIP-C.FzAP0Vt-mAdHvqJyM01TPgAAAA?w=172&h=180&c=7&r=0&o=5&pid=1.7'
    return SellCounter, is_tax, sku_types, QR_pic_url, place


def old_tb_info(title, driver):
    """ 旧版淘宝网页格式的单个详情页数据 """
    # 防止验证码干扰，预留人工处理时间
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#J_tbExtra > dl > dd')))
    except TimeoutException:
        show_true_popup("请人工处理")
        if driver.find_element(By.CSS_SELECTOR, '.BasicContent--sku--6N_nw6c'):
            SellCounter, is_tax, sku_types, QR_pic_url, place = new_tb_info(title, driver)
            return SellCounter, is_tax, sku_types, QR_pic_url, place
        else:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#J_tbExtra > dl > dd')))

    property_type = []
    capacity_type = []
    time.sleep(1)
    # 识别是否出现弹窗
    is_bannar = driver.find_elements(By.CSS_SELECTOR, 'body > div.J_MIDDLEWARE_FRAME_WIDGET > iframe,' '#baxia-punish,'
                                     '#bg-img,' '#bx-feedback-btn')
    # if len(is_bannar) > 0:
    #     show_true_popup("请人工处理")
    #     time.sleep(8)
    while driver.find_elements(By.CSS_SELECTOR, 'body > div.J_MIDDLEWARE_FRAME_WIDGET > iframe,' '#baxia-punish,'
                                     '#bg-img,' '#bx-feedback-btn'):
        show_true_popup("请人工处理")
        time.sleep(5)

    # 商品主图
    main_pic = driver.find_element(By.CSS_SELECTOR, '#J_ImgBooth,' '#J_UlThumb > li:nth-child(2) > div > a > img,'
                                                    '#J_UlThumb > li.tb-selected > div > a > img')
    main_pic = main_pic.get_attribute('src')
    # 月销量
    SellCounter = driver.find_element(By.CSS_SELECTOR, '#J_SellCounter')
    SellCounter = SellCounter.text.strip()
    # 判断并构造是否保税区发货字段
    tb_extra = driver.find_element(By.CSS_SELECTOR, '#J_tbExtra > dl > dd')
    if '保税区发货' in tb_extra.text.strip():
        is_tax = '保税区发货'
    elif '海外直邮' in tb_extra.text.strip():
        is_tax = '海外直邮'
    else:
        is_tax = '一般贸易'

    # 发货地
    place = driver.find_elements(By.CSS_SELECTOR, '#J-From')
    if place:
        place = place[0].text.strip().replace('至', '')

    # 类型（罐型）列表
    for p in driver.find_elements(By.CSS_SELECTOR, '#J_isku > div > dl:nth-child(1) > dd > ul > li,'
                                                   '#J_isku > div > dl:nth-child(1) > dd > ul > li:nth-child(n)'):
        property_type.append(p.text.strip())
    # 容量列表
    for c in driver.find_elements(By.CSS_SELECTOR, '#J_isku > div > dl:nth-child(2) > dd > ul > li,'
                                                   '#J_isku > div > dl:nth-child(2) > dd > ul > li:nth-child(n)'):
        capacity_type.append(c.text.strip())

    # 如果这两个列表均不为空，排列组合构造SKU列表；其中一个为空则将另一列表直接赋值给SKU列表
    if property_type and capacity_type:
        sku_types = [f'{x} {y}' for x, y in itertools.product(property_type, capacity_type)]
    else:
        sku_types = property_type or capacity_type
    # print('SKU列表:', sku_types)
    data_property = driver.find_elements(By.CSS_SELECTOR, '#J_isku > div > dl:nth-child(1) > dd > ul')
    if data_property and '颜色分类' in data_property[0].get_attribute('data-property'):
        sku_types = [f'{title}']
    # 如果没有款式选择区域，则用标题
    if not sku_types:
        sku_types.append(title)
    QR_btn = driver.find_element(By.CSS_SELECTOR, '#J_TabBar > li.tb-qrcode-tool')
    driver.execute_script("arguments[0].scrollIntoView();", QR_btn)
    # 定位要悬停的元素QR_btn
    # 使用ActionChains模拟鼠标悬停操作
    ActionChains(driver).move_to_element(QR_btn).perform()
    time.sleep(random.uniform(1, 1.3))
    # 定位到指定元素
    element = driver.find_element(By.CSS_SELECTOR, '.ks-popup > .ks-overlay-content')

    # 获取元素的位置和大小
    location = element.location
    size = element.size
    # 截取指定元素区域的截图
    screenshot_base64 = driver.get_screenshot_as_base64()
    time.sleep(0.5)
    img = Image.open(BytesIO(base64.b64decode(screenshot_base64)))
    left = location['x']
    time.sleep(0.5)
    top = 45  # location['y']
    right = location['x'] + size['width']
    bottom = top + size['height']
    # print(left, top, right, bottom)
    img = img.crop((left, top, right, bottom))

    # 将截图转换为 Base64 编码
    buffered = BytesIO()
    try:
        img.save(buffered, format="PNG")
        screenshot_base64_cropped = base64.b64encode(buffered.getvalue()).decode('utf-8')
        # print('data:image/png;base64,' + str(screenshot_base64_cropped))
        QR_pic_url = 'data:image/png;base64,' + str(screenshot_base64_cropped)
    except:
        QR_pic_url = 'https://tse4-mm.cn.bing.net/th/id/OIP-C.FzAP0Vt-mAdHvqJyM01TPgAAAA?w=172&h=180&c=7&r=0&o=5&pid=1.7'

    return SellCounter, is_tax, sku_types, QR_pic_url, place


def get_tb_data(driver, tb_data):
    """ 循环调用函数获取所有淘宝详情页数据 """
    all_data = pd.DataFrame(
        columns=['二维码链接', '商品链接', '关键词', '类别', '店名', '标题', '商品ID', '月销量', '是否保税区', '发货地',
                 '版本', 'SKU'])
    for type, store, title, url, id, keyword \
            in zip(tb_data['类型'], tb_data['店铺'], tb_data['标题'], tb_data['商品链接'], tb_data['商品ID'],
                   tb_data['关键词']):
        SellCounter, is_tax, sku_types, QR_pic_url, place = get_tb_info(url, title, driver)

        half_data = pd.DataFrame({
            '二维码链接': [f'{QR_pic_url}'] + ['\\'] * (len(sku_types) - 1),
            '商品链接': [f'{url}'] * len(sku_types),
            '关键词': [f'{keyword}'] * len(sku_types),
            '类别': [f'{type}'] * len(sku_types),
            '店名': [f'{store}'] * len(sku_types),
            '标题': [f'{title}'] + ['\\'] * (len(sku_types) - 1),
            '商品ID': [f'{id}'] * len(sku_types),
            '月销量': [f'{SellCounter}'] * len(sku_types),
            '是否保税区': [f'{is_tax}'] * len(sku_types),
            '发货地': [f'{place}'] * len(sku_types),
            '版本': ['None'] * len(sku_types),
            'SKU': sku_types,
        })
        all_data = pd.concat([all_data, half_data], ignore_index=True)

    return all_data


def get_tm_info(url, title, driver):
    """ 获取天猫网页格式的单个详情页数据 """
    driver.get(url=url)
    time.sleep(random.uniform(0.5, 1))
    # 防止干扰，预留人工处理时间
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.BasicContent--sku--6N_nw6c')))
    except TimeoutException:
        show_true_popup("请人工处理")
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.BasicContent--sku--6N_nw6c')))

    property_type = []
    capacity_type = []
    zuhe_type = []
    is_bannar = driver.find_elements(By.CSS_SELECTOR, 'body > div.J_MIDDLEWARE_FRAME_WIDGET > iframe,' '#baxia-punish,'
                                     '#bg-img,' '#bx-feedback-btn')
    # if len(is_bannar) > 0:
    #     show_true_popup("请人工处理")
    #     time.sleep(8)
    while driver.find_elements(By.CSS_SELECTOR, 'body > div.J_MIDDLEWARE_FRAME_WIDGET > iframe,' '#baxia-punish,'
                                     '#bg-img,' '#bx-feedback-btn'):
        show_true_popup("请人工处理")
        time.sleep(5)
    # 转手机二维码
    time.sleep(random.uniform(0.8, 1))
    # 定位要悬停的元素
    element_to_hover_over = driver.find_element(By.CSS_SELECTOR,
                                                "#J_Toolkit > div > div > div.toolkit-item.toolkit-item-qrcode")
    # 使用ActionChains模拟鼠标悬停操作
    ActionChains(driver).move_to_element(element_to_hover_over).perform()
    time.sleep(random.uniform(0.8, 1))
    # 定位到指定元素
    QR_element = driver.find_element(By.CSS_SELECTOR,
                                     '#J_Toolkit > div > div > div.toolkit-item.toolkit-item-qrcode > div > div > canvas')

    # 获取元素的位置和大小
    location = QR_element.location
    size = QR_element.size
    # 截取指定元素区域的截图
    screenshot_base64 = driver.get_screenshot_as_base64()
    time.sleep(0.5)
    img = Image.open(BytesIO(base64.b64decode(screenshot_base64)))
    time.sleep(0.5)
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    img = img.crop((left, top, right, bottom))
    # 将截图转换为 Base64 编码
    buffered = BytesIO()
    try:
        img.save(buffered, format="PNG")
        screenshot_base64_cropped = base64.b64encode(buffered.getvalue()).decode('utf-8')
        # print('data:image/png;base64,' + str(screenshot_base64_cropped))
        QR_link = 'data:image/png;base64,' + str(screenshot_base64_cropped)
    except:
        QR_link = 'https://tse4-mm.cn.bing.net/th/id/OIP-C.FzAP0Vt-mAdHvqJyM01TPgAAAA?w=172&h=180&c=7&r=0&o=5&pid=1.7'
    # 主图链接
    # main_pic = driver.find_element(By.CSS_SELECTOR, '.BasicContent--mainPic--2v9ooiI > div > div > img,'
    #                                                 '.BasicContent--mainPic--2v9ooiI > div > ul > li:nth-child(2) > img')
    # main_pic_link = main_pic.get_attribute('src')
    # 月销量
    SellCounter = driver.find_element(By.CSS_SELECTOR,
                                      '.BasicContent--itemInfo--2NdSOrj > div.ItemHeader--root--DXhqHxP > div > span.ItemHeader--salesDesc--srlk2Hv')
    SellCounter = SellCounter.text.strip()
    # 发货地
    place = driver.find_elements(By.CSS_SELECTOR,
                                 '#root > div > div.Item--main--1sEwqeT > div.Item--content--12o-RdR > div.BasicContent--root--1_NvQmc > div.BasicContent--main--2mfq-dl > div.BasicContent--itemInfo--2NdSOrj > div.MCDelivery > div.delivery-content > div.delivery-content-inner > div.delivery-from-addr')
    if place:
        place = place[0].text.strip().replace('至', '')
    # 商品版本信息
    version = driver.find_elements(By.CSS_SELECTOR,
                                   '.BasicContent--sku--6N_nw6c > div > div > div.skuCate > div > div.skuItem.current > span')
    if version:
        version = version[0].text.strip()
        # 罐型信息
        for p in driver.find_elements(By.CSS_SELECTOR,
                                      '.BasicContent--sku--6N_nw6c > div > div > div:nth-child(2) > div:nth-child(1) > div > div > div > span'):
            property_type.append(p.text.strip())
    else:
        version = 'None'
        for p in driver.find_elements(By.CSS_SELECTOR,
                                      '.BasicContent--sku--6N_nw6c > div > div > div:nth-child(1) > div:nth-child(1) > div > div > div > span'):
            property_type.append(p.text.strip())

    # 税信息
    tb_extra = driver.find_elements(By.CSS_SELECTOR,
                                    '#root > div > div.Item--main--1sEwqeT > div.Item--content--12o-RdR > div.BasicContent--root--1_NvQmc > div.BasicContent--banner--1_UlxqS > img')
    if len(tb_extra) != 0:
        tb_extra = driver.find_element(By.CSS_SELECTOR,
                                       '#root > div > div.Item--main--1sEwqeT > div.Item--content--12o-RdR > div.BasicContent--root--1_NvQmc > div.BasicContent--banner--1_UlxqS > img')
        if '/imgextra/i1' in tb_extra.get_attribute('src'):
            is_tax = '保税区发货'
        else:
            is_tax = '海外直邮'
    else:
        is_tax = '一般贸易'

    # 容量信息
    for c in driver.find_elements(By.CSS_SELECTOR,
                                  '.BasicContent--sku--6N_nw6c > div > div > div:nth-child(2) > div:nth-child(2) > div > div > div > span,'
                                  '#J_isku > div > dl:nth-child(2) > dd > ul > li:nth-child(n),'
                                  '.BasicContent--sku--6N_nw6c > div > div > div:nth-child(1) > div:nth-child(2) > div > div > div > span'):
        capacity_type.append(c.text.strip())
    # 组合信息
    for z in driver.find_elements(By.CSS_SELECTOR,
                                  '.BasicContent--sku--6N_nw6c > div > div > div:nth-child(1) > div > div > div > div > span'):
        zuhe_type.append(z.text.strip())
    # SKU款式信息
    if len(capacity_type) == 0:
        if len(zuhe_type) == 0:
            sku_types = property_type
        else:
            sku_types = zuhe_type
    else:
        sku_types = [f'{x} {y}' for x, y in itertools.product(property_type, capacity_type)]

    if len(sku_types) == 0:
        sku_types.append(title)

    return SellCounter, is_tax, sku_types, QR_link, version, place


def get_tm_data(driver, tm_data):
    """ 循环调用函数获取所有天猫详情页数据 """
    all_data = pd.DataFrame(
        columns=['二维码链接', '商品链接', '关键词', '类别', '店名', '标题', '商品ID', '月销量', '是否保税区', '发货地',
                 '版本', 'SKU'])
    for type, store, title, url, id, keyword in \
            zip(tm_data['类型'], tm_data['店铺'], tm_data['标题'], tm_data['商品链接'], tm_data['商品ID'],
                tm_data['关键词']):
        SellCounter, is_tax, sku_types, QR_link, version, place = get_tm_info(url, title, driver)

        half_data = pd.DataFrame({
            '二维码链接': [f'{QR_link}'] + ['\\'] * (len(sku_types) - 1),
            # '主图链接': [f'{main_pic}'] * len(sku_types),
            '商品链接': [f'{url}'] * len(sku_types),
            '关键词': [f'{keyword}'] * len(sku_types),
            '类别': [f'{type}'] * len(sku_types),
            '店名': [f'{store}'] * len(sku_types),
            '标题': [f'{title}'] + ['\\'] * (len(sku_types) - 1),
            '商品ID': [f'{id}'] * len(sku_types),
            '月销量': [f'{SellCounter}'] * len(sku_types),
            '是否保税区': [f'{is_tax}'] * len(sku_types),
            '发货地': [f'{place}'] * len(sku_types),
            '版本': [f'{version}'] * len(sku_types),  # + ['\\'] * (len(sku_types) - 1),
            'SKU': sku_types,
        })
        all_data = pd.concat([all_data, half_data], ignore_index=True)
    return all_data


def show_detail_html(detail_data, save_path, keyword):
    """ 将数据展示在html网页上 """

    def main_pic_to_html(image_url):
        return f'<img src="{image_url}" height=150 width=150 alt="">'

    def qr_link_to_html(image_url):
        if len(str(image_url)) > 2:
            return f'<img src="{image_url}" height=120 width=120 alt="">'
        else:
            return image_url

    def link_html(link_url):
        if len(str(link_url)) > 2:
            return f'<a href="{link_url}">{link_url}</a>'
        else:
            return link_url

    # 创建一个新的 DataFrame，同时插入空白列
    modified_data = detail_data.copy()

    modified_data['价格'] = ''

    # 将 DataFrame 导出为 HTML 文件，并在指定字段上应用自定义函数
    modified_data['二维码链接'] = modified_data['二维码链接'].apply(qr_link_to_html)
    # modified_data['主图链接'] = modified_data['主图链接'].apply(main_pic_to_html)
    modified_data['商品链接'] = modified_data['商品链接'].apply(link_html)

    # 重新设置索引
    modified_data.reset_index(drop=True, inplace=True)
    # 将 DataFrame 转换为 HTML 字符串
    html_content = modified_data.to_html(index=True, escape=False)

    # 在导出 HTML 文件之前，将包含 DataFrame 内容的字符串进行处理
    html_header = r"""
<!DOCTYPE html>
<html>
<head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>淘宝查价格html</title>
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
        }
        thead {
            position: sticky;
            top: 70px;
            background-color: #cccccc;
        }
        .fill-input2 {
            margin-bottom: 25px; /* 控制输入框上下距离 */
            font-size: 18px; /* 控制输入文本字体大小 */
            color: red; /* 控制输入字体颜色 */
        }
    </style>
</head>
<body>
    <div id="exportContainer">
        <a href="https://www.taobao.com/" class="logo" >
          <img class="logo" src="https://gw.alicdn.com/imgextra/i3/O1CN01uRz3de23mzWofmPYX_!!6000000007299-2-tps-143-59.png" height=40 width=150 alt=""></a>
        <input type="text" id="filenameInput" placeholder="文件名 (不填则取当前时刻命名)">
        <button id="exportButton">导出为csv</button>
        <button id="clearButton">一键清空</button>

    </div>
<table border="1" class="dataframe">
    """

    html_tail = r"""
</table>
</body>
<script>
// 在页面加载完成时执行的函数
window.addEventListener('load', function() {
  // 获取所有带有类名"fill-input2"的<input>元素
  var inputElements = document.querySelectorAll('.fill-input2');

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
  var inputElements = document.querySelectorAll('.fill-input2');
  inputElements.forEach(function(inputElement) {
    inputElement.value = '';
    localStorage.removeItem(inputElement.id + '-value');
  });
}
// 导出数据到Excel
function exportToExcel() {
  var headers = ['', '商品链接', '关键词', '类别', '店名', '标题', '商品ID', '月销量', '是否保税区', '发货地', '版本', 'SKU', '价格']; // 替换成你的实际字段名
  var csvContent = "data:text/csv;charset=utf-8";

  var data = [];
  var price_data = [];
    // 获取<input>元素的值
  var inputElements = document.querySelectorAll('.fill-input2');
  inputElements.forEach(function(inputElement) {
    price_data.push(inputElement.value);
  });
  // 获取商品行<tr>元素
  var productRows = document.body.querySelector('tbody').querySelectorAll('tr');
  productRows.forEach(function(row) {
    var rowData = [];
    // 获取<tr>中的第1到第6个<td>的值
    var tableData = row.querySelectorAll('td');
    for (var i = 1; i <= 11; i++) {
      rowData.push(tableData[i].innerText);
    }
    // 将价格字段添加到rowData中
    var rowIndex = Array.from(productRows).indexOf(row);
    rowData.push(price_data[rowIndex]);
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

  // 使用用户输入的文件名，如果输入框为空则使用当前时间作为默认名称
  var filename = filenameInput.value.trim() || currentTime;

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

    # 在 HTML 的表格行中插入 input 元素，并为 input 元素添加 class属性<td><input class="fill-input1" type="checkbox"></td>
    html_content = html_content.replace(
        '<td></td>',
        '<td><input class="fill-input2" type="text"></td>'
    )
    # 添加html尾部代码
    html_content = html_content.replace('</table>', html_tail)
    # 将处理后的 HTML 字符串保存为 HTML 文件
    with open(rf'{save_path}\详情页\tb-{keyword}-detail.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

    return html_content


def tb_detail_transform_table(html_str):
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_str, 'html.parser')
    # 获取表格元素
    table = soup.select_one('table > tbody')
    # 创建新的 HTML 结构
    new_html = '<div class="grid-container">'
    # 遍历每一行<tr>
    for row in table.find_all('tr'):
        # new_html += '<div class="grid-item">'

        # 获取每个字段的值
        link_src = row.select('td img')[0]['src']  # :nth-child(1)
        # index = row.select('td')[2].text
        keyword = row.select('td')[2].text
        link = row.select('td a')[0]['href']
        type = row.select('td')[3].text
        whole_shop = row.select('td')[4].text
        shop = row.select('td')[4].text[:7] + '...'  # 过长部分隐藏
        whole_title = row.select('td')[5].text
        title = row.select('td')[5].text[:28] + '...'  # 标题过长部分隐藏
        item_id = row.select('td')[6].text
        sell = row.select('td')[7].text
        tax_type = row.select('td')[8].text
        place = row.select('td')[9].text
        version = row.select('td')[10].text
        whole_version = row.select('td')[10].text[:8] + '...'
        attribute = row.select('td')[11].text
        whole_attribute = row.select('td')[11].text[:10] + '...'
        # price = row.select('td input')[0]['class']

        # 构造新 HTML 结构
        new_html += f'''
            <div class="grid-item">
                <div class="info">
                    <div class="item-info">
                        <div class="type">{type}</div>
                        <div class="tax_type" title="{keyword}">{tax_type}</div>                   
                    </div>
                    <div class="item-info">
                        <div class="sell">{sell} 销量</div>
                        <div class="place">{place}</div>
                    </div>
                    <div class="item-info">
                        <div class="item-id">ID:{item_id}</div>
                        <div class="version" title="{whole_version}">{version}</div>
                    </div>
                    <div class="img-container">   
                        <div>                 
                            <a href="{link}">
                                <img src="{link_src}" height=110 width=110 alt="" title="{link}">
                            </a>
                            <div class="attribute" title="{whole_attribute}">{attribute}</div>
                        </div>
                        <div> 
                            <div class="shop" title="{whole_shop}">{shop}</div>
                            <div class="title" title="{whole_title}">{title}</div>
                            <div class="reserved">
                                <input class="fill-input2" type="text">
                                <input class="fill-input1" type="checkbox">
                            </div>
                        </div>
                    </div> 
                </div>
            </div>
        '''
        # new_html += '\n'
    new_html += '</div>'

    return new_html



if __name__ == '__main__':
    # 搜索关键词
    keyword = 'a2奶粉三段'
    # 储存数据文件夹路径
    save_path = r"C:\Users\EDY\Desktop\data\TB"
    # 添加保持登录的数据路径：安装目录一般在C:\Users\****\AppData\Local\Google\Chrome\User Data
    user_data_dir = r"C:\Users\EDY\AppData\Local\Google\Chrome\User Data"
    # 数据范围选择，0只要淘宝系的数据，1只要天猫系的数据，不填或其余元素则不筛选
    data_range = ''

    # 创建浏览器驱动
    driver, wait = create_driver(user_data_dir)
    # 筛选后浏览器导出的数据文件路径
    try:
        filter_data = pd.read_csv(r"C:\Users\EDY\Downloads\2024_1_12 15_00_09.csv")
    except:
        filter_data = pd.read_csv(r"C:\Users\EDY\Downloads\2024_1_12 15_00_09.csv", encoding='gbk')
    # filter_data['是否保留'] = filter_data['是否保留'].apply(lambda x: str(x))
    filter_data = filter_data[filter_data['是否保留']]

    # 筛选只要淘宝的数据
    if data_range == '淘宝':
        tb_data = filter_data.copy()
        tb_data = tb_data[tb_data['类型'] != '天猫']
        detail_data = get_tb_data(driver, tb_data)
    # 筛选只要天猫的数据
    elif data_range == '天猫':
        tm_data = filter_data.copy()
        tm_data = tm_data[tm_data['类型'] == '天猫']
        detail_data = get_tm_data(driver, tm_data)
    # 不筛选，全部都要
    else:
        tb_data = filter_data[filter_data['类型'] != '天猫']
        tm_data = filter_data[filter_data['类型'] == '天猫']
        all_tb_data = get_tb_data(driver, tb_data)
        all_tm_data = get_tm_data(driver, tm_data)
        detail_data = pd.concat([all_tb_data, all_tm_data], ignore_index=True)

    detail_data['月销量'] = detail_data['月销量'].str.replace('月销 ', '').str.replace('已售 ', '')
    detail_data['商品ID'] = detail_data['商品链接'].apply(lambda x: str(x).split('id=')[-1].split('&ns')[0])
    detail_data.to_excel(rf'{save_path}\tb-{keyword}-detail.xlsx', index=False)
    html_content = show_detail_html(detail_data, save_path, keyword)
    driver.quit()
