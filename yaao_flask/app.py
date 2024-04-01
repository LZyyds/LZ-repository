import pandas as pd
from flask import Flask, render_template, request, send_file, Response, jsonify
from 淘宝商城爬取目录页 import *
from 淘宝商城爬取详情页 import *
from 京东批量关键词 import *
from 商智自动化全流程 import *
from 多个webdriver import *
from jd_app import *
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import numpy as np
import psutil
import requests
import websocket
import json
import os

app = Flask(__name__)
# 设置中文字体为SimHei
font_path = r'./static/SimHei.ttf'  # 根据实际字体文件的路径进行修改
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
app.static_folder = os.path.join(app.root_path, 'static')
app.template_folder = os.path.join(app.root_path, 'templates')
app.debug = True

dir_data = None
# 数据文件夹保存路径
tb_save_path_dir = r"D:\桌面\work\yaao\淘宝"
jd_save_path_dir = rf'D:\桌面\work\yaao\京东'

""" 以下代码用于初次运行，创建需要的文件夹，创建后可注释
    注意，如果以下两行文件夹名称改动后，面的代码也需要跟着改 """
# jd_folders = ['导出价格', '查完销量', '已筛选完', '配置文件']
# tb_folders = ['localStorage', 'black_list', '搜索页', '详情页']
# for jd_folder in jd_folders:
#     jd_folder_path = os.path.join(jd_save_path_dir, jd_folder)
#     if not os.path.exists(jd_folder_path):
#         os.makedirs(jd_folder_path)
#         print(f'文件夹 {jd_folder} 创建成功')
#     else:
#         print(f'文件夹 {jd_folder} 已存在')
# for tb_folder in tb_folders:
#     tb_folder_path = os.path.join(tb_save_path_dir, tb_folder)
#     if not os.path.exists(tb_folder_path):
#         os.makedirs(tb_folder_path)
#         print(f'文件夹 {tb_folder} 创建成功')
#     else:
#         print(f'文件夹 {tb_folder} 已存在')


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/index')
def home():
    #return render_template("index.html")
    return index()


@app.route('/TB_index')
def TB_index():
    """ 淘宝操作页 """
    return render_template("TB_index.html")


@app.route('/JD_index')
def JD_index():
    """ 京东（扫码填价版本）操作页 """
    return render_template("JD_index.html")


@app.route('/JDSZ_index')
def JDSZ_index():
    """ 京东商智操作页 """
    return render_template("JDSZ_index.html")


@app.route('/new_JD_index')
def new_JD_index():
    """ 京东（机器填价版本）操作页 """
    return render_template("new_JD_index.html")


@app.route('/add_SKU', methods=['POST'])
def add_SKU():
    """ 商智单个商铺单独添加SKU的路由 """
    data = request.get_json()
    # 获取前端参数
    account = data.get('account')
    password = data.get('password')
    inputPath = data.get('inputPath')
    driver, wait = create_driver()
    automatic_logon(account, password, driver, wait)
    # 竞品配置自动点击函数
    config_click(driver, wait)
    # 批量添加所有SKU监控
    if '.csv' not in inputPath:
        addPath = rf'{jd_save_path_dir}\导出价格\jd-{inputPath}-price.xlsx'
    else:
        addPath = rf'{inputPath}'
    # 添加操作函数
    msg = add_sku(addPath, driver, wait)
    driver.close()
    return jsonify({'success': True, 'msg': msg})


@app.route('/delete_SKU', methods=['POST'])
def delete_SKU():
    """ 商智单个商铺单独删除SKU的路由 """
    data = request.get_json()
    # 搜索关键词
    account = data.get('account')
    password = data.get('password')
    driver, wait = create_driver()
    automatic_logon(account, password, driver, wait)
    # 竞品配置自动点击
    config_click(driver, wait)
    # 批量删除所有SKU监控
    delete_sku(driver, wait)
    driver.close()
    msg = '删除完毕'
    return jsonify({'success': True, 'msg': msg})


@app.route('/query_sales', methods=['POST'])
def query_sales():
    """ 商智单个商铺单独查询SKU的路由 """
    data = request.get_json()
    # 搜索关键词
    account = data.get('account')
    password = data.get('password')
    inputPath = data.get('inputPath')
    outputPath = data.get('outputPath')
    driver, wait = create_driver()
    automatic_logon(account, password, driver, wait)
    # 竞品配置自动点击
    config_click(driver, wait)
    # 竞品概况自动点击
    view_click(driver, wait)
    # 上周成交单量数据
    last_week_data = get_trade_num("/html/body/div[3]/div/div[2]/div[1]/div[2]/div/p/div/ul/li[4]", '周成交单量', driver, wait)
    # 上月成交单量数据
    last_month_data = get_trade_num("/html/body/div[3]/div/div[2]/div[1]/div[2]/div/p/div/ul/li[5]", '月成交单量', driver, wait)
    # print(last_month_data)
    if '.csv' in inputPath:
        try:
            price_data = pd.read_csv(rf'{inputPath}')
        except:
            price_data = pd.read_csv(rf'{inputPath}', encoding='gbk')
    else:
        price_data = pd.read_excel(rf'{jd_save_path_dir}\导出价格\jd-{inputPath}-price.xlsx')
    # sale_data.to_excel(rf'{jd_save_path_dir}\sale_data.xlsx', index=False)
    # sale_data = pd.read_excel(rf'{jd_save_path_dir}\sale_data.xlsx')
    # 将爬取的周/月成交单量根据SKU添加到总表
    all_data = add_columns_by_sku(price_data, last_week_data, '周成交单量')
    all_data = add_columns_by_sku(all_data, last_month_data, '月成交单量')
    # 将结果保存到 Excel 文件中
    all_data.to_excel(rf'{jd_save_path_dir}\查完销量\{outputPath}.xlsx', index=False)
    driver.close()
    msg = '查询完毕'
    return jsonify({'success': True, 'msg': msg})


@app.route('/all_jdsz', methods=['POST'])
def all_jdsz():
    """ 商智单个商铺全部操作的路由 """
    data = request.get_json()
    # 搜索关键词
    account = data.get('account')
    password = data.get('password')
    inputPath = data.get('inputPath')
    outputPath = data.get('outputPath')
    driver, wait = create_driver()
    # 自动登录京商智账号
    automatic_logon(account, password, driver, wait)
    # 竞品配置自动点击
    config_click(driver, wait)
    # 批量删除所有SKU监控
    delete_sku(driver, wait)
    # 批量添加所有SKU监控
    if '.csv' not in inputPath:
        addPath = rf'{jd_save_path_dir}\导出价格\jd-{inputPath}-price.xlsx'
    else:
        addPath = rf'{inputPath}'
    # 添加SKU函数
    msg = add_sku(addPath, driver, wait)
    # 竞品概况自动点击
    view_click(driver, wait)
    # 上周成交单量数据
    last_week_data = get_trade_num("/html/body/div[3]/div/div[2]/div[1]/div[2]/div/p/div/ul/li[4]", '周成交单量', driver, wait)
    # 上月成交单量数据
    last_month_data = get_trade_num("/html/body/div[3]/div/div[2]/div[1]/div[2]/div/p/div/ul/li[5]", '月成交单量', driver, wait)
    # 需要操作的数据表
    if '.csv' in inputPath:
        try:
            price_data = pd.read_csv(rf'{inputPath}')
        except:
            price_data = pd.read_csv(rf'{inputPath}', encoding='gbk')
    else:
        price_data = pd.read_excel(rf'{jd_save_path_dir}\导出价格\jd-{inputPath}-price.xlsx')
    # 将爬取的周/月成交单量根据SKU添加到总表
    all_data = add_columns_by_sku(price_data, last_week_data, '周成交单量')
    all_data = add_columns_by_sku(all_data, last_month_data, '月成交单量')
    # 将结果保存到 Excel 文件中
    all_data.to_excel(rf'{jd_save_path_dir}\查完销量\{outputPath}.xlsx', index=False)
    driver.close()
    msg = msg + '\n\n全部操作完毕'
    return jsonify({'success': True, 'msg': msg})


@app.route('/all_webdriver', methods=['POST'])
def all_webdriver():
    """ 商智多个商铺循环全部操作的路由（对应商智操作页的右侧部分按钮） """
    data = request.get_json()
    # 获取前端信息
    table_name = data.get('inputPath')
    output_name = data.get('outputPath')
    # 执行函数
    all_webdriver_main(jd_save_path_dir, table_name, output_name)
    msg = '全部操作完毕'
    return jsonify({'success': True, 'msg': msg})


@app.route('/search_button', methods=['POST'])
def search_button():
    """ 商智多个商铺循环全部操作的路由（对应京东操作页的“查销量”按钮） """
    data = request.get_json()
    # 获取前端信息
    table_name = data.get('table_name')
    # 执行函数
    all_webdriver_main(jd_save_path_dir, table_name, table_name)
    return jsonify({'success': True})


@app.route('/app_button', methods=['POST'])
def app_button():
    """ 对应京东操作页的“查价格”按钮 """
    data = request.get_json()
    # 获取前端信息
    table_name = data.get('table_name')
    # 执行函数
    jd_app_main(jd_save_path_dir, table_name)
    return jsonify({'success': True})


@app.route('/jd_export-csv', methods=['POST'])
def jd_export_csv():
    """ 对应京东操作页（扫码查价版本）中的导出excel按钮 """
    data = request.get_json()
    # keyword = data['keyword']
    table_data = data['table_data']
    table_name = data['table_name']
    result_data = pd.DataFrame(table_data, columns=['索引', '关键词', '商品链接', '标题', '店铺', '评论数', 'SKU', '属性', '价格1', '价格2', '价格3', '价格4', '价格5', '价格6'])
    # 将空字符串替换为NaN
    result_data.replace('', pd.NA, inplace=True)
    # 删除所有值都为空的行
    result_data = result_data.dropna(subset=['价格1', '价格2', '价格3', '价格4', '价格5', '价格6'], how='all')
    # 将剩余非空行的空值赋值为'/'
    result_data.fillna('/', inplace=True)
    # 构建新字段
    result_data['周成交单量'] = ''
    result_data['月成交单量'] = ''
    # 重新排列字段顺序
    new_order = ['索引', '关键词', '标题', '属性', '店铺', '商品链接', '评论数', '周成交单量', '月成交单量', '价格1',
                 '价格2', '价格3', '价格4', '价格5', '价格6', 'SKU']
    result_data = result_data.reindex(columns=new_order)
    result_data.to_excel(rf'{jd_save_path_dir}\导出价格\jd-{table_name}-price.xlsx', index=False)

    return jsonify({'success': True})


@app.route('/jd_export_filter', methods=['POST'])
def jd_export_filter():
    """ 对应京东操作页（机器查价版本）中的导出excel按钮 """
    data = request.get_json()
    # keyword = data['keyword']
    table_data = data['table_data']
    table_name = data['table_name']
    result_data = pd.DataFrame(table_data, columns=['索引', '关键词', '商品链接', '标题', '店铺', '评论数', 'SKU', '属性', '是否勾选'])
    # 将空字符串替换为NaN
    result_data.replace('', pd.NA, inplace=True)
    # 筛选勾选的商品
    result_data = result_data[result_data['是否勾选']]
    result_data = result_data[['索引', '关键词', '商品链接', '标题', '店铺', '评论数', 'SKU', '属性']]
    # 将剩余非空行的空值赋值为'/'
    # result_data.fillna('/', inplace=True)
    # result_data = spilt_price(result_data)
    result_data['周成交单量'] = ''
    result_data['月成交单量'] = ''
    result_data['价格1'] = ''
    result_data['价格2'] = ''
    result_data['价格3'] = ''
    result_data['发货地区'] = ''
    new_order = ['索引', '关键词', '标题', '属性', '店铺', '发货地区', '商品链接', '评论数', '周成交单量', '月成交单量', '价格1',
                 '价格2', '价格3', 'SKU']
    # 重新排列字段顺序
    result_data = result_data.reindex(columns=new_order)
    result_data.to_excel(rf'{jd_save_path_dir}\已筛选完\jd-{table_name}.xlsx', index=False)

    return jsonify({'success': True})


@app.route('/jd_uploadFile', methods=['POST'])
def jd_upload_file():
    """ 对应京东操作页（两个版本）中的导入文件按钮 """
    uploaded_file = request.files['file']  # 获取上传的文件
    df = pd.read_excel(uploaded_file)  # 读取Excel文件内容
    df.replace(pd.NA, '', inplace=True)
    # 获取指定的四个字段内容存为四个列表
    field1_list = df['关键词'].tolist()
    field2_list = df['店铺数'].tolist()
    field3_list = df['黑名单'].tolist()
    field4_list = df['白名单'].tolist()
    # 处理整列都为空的异常情况
    try:
        field3_list = ['' if np.isnan(x) else x for x in field3_list]
    except:
        pass
    try:
        field4_list = ['' if np.isnan(x) else x for x in field4_list]
    except:
        pass
    print(field1_list, field2_list, field3_list, field4_list, sep='\n')
    # 返回关键词信息到前端，将配置文件，即表格中内容写到前端页面，相当于代替输入关键词信息
    return jsonify({
        'success': True,
        'field1_list': field1_list, 'field2_list': field2_list,
        'field3_list': field3_list, 'field4_list': field4_list
    })


@app.route('/start_jd', methods=['POST'])
def start_jd():
    """  该路由已弃用
    为京东爬取单个关键词的版本，目前都是批量多个关键词的版本
    对应 single_JD_index.html 和 京东国际商城爬取全流程.py """
    data = request.get_json()
    all_url = []
    # 搜索关键词
    keyword = data.get('keyword')
    # 需要销量前几个店铺(修改数字)
    store_num = int(data.get('store_num'))
    # 筛选关键词-黑名单和白名单，列表可为空、（自行更改）
    inputVal1 = data.get('inputVal1')
    inputVal2 = data.get('inputVal2')

    # 如果用户不输入黑白名单，即为空列表
    if inputVal1 == '':
        black_list = []
    else:
        black_list = inputVal1.split(' ')
    if inputVal2 == '':
        white_list = []
    else:
        white_list = inputVal2.split(' ')
    print(black_list, white_list, sep='\n')
    # 保存路径--文件夹（自行更改）
    # save_path_dir = rf'C:\Users\EDY\Desktop\data\JD'
    # 添加保持登录的数据路径：安装目录一般在C:\Users\****\AppData\Local\Google\Chrome\User Data
    user_data_dir = r"C:\Users\EDY\AppData\Local\Google\Chrome\User Data"

    # 创建浏览器驱动和等待参数
    driver, wait = jd_create_driver(user_data_dir)
    # 登录操作（登录信息失效则须人工介入扫码）
    jd_login(driver, wait, keyword)
    # 先获取搜索页信息
    dir_data = jd_get_dir_info(driver, jd_save_path_dir, store_num, keyword)
    # # 获取包括详情页内的所有信息
    all_data = jd_get_all_data(dir_data, driver, all_url, keyword)
    # 关闭浏览器
    driver.close()
    # 筛选并保存数据
    filter_data = jd_filter_save_data(white_list, black_list, jd_save_path_dir, keyword, all_data)
    # 生成html文件
    html_content = jd_show_on_html(jd_save_path_dir, keyword, filter_data)
    table_content = jd_transform_table(html_content)
    # table_content = re.search(r'<table border="1" class="dataframe">(.*?)</table>', html_content, re.DOTALL)
    if not table_content:
        table_content = '异常，表格为空'
    # msg = rf'文件路径为{save_path_dir}\jd-{keyword}.html'
    return jsonify({'success': True, 'msg': table_content})


@app.route('/start_jd1', methods=['POST'])
def start_jd1():
    """ 对应京东操作页（扫码查价版本）中的启动按钮 """
    data = request.get_json()
    all_url = []
    all_data2 = pd.DataFrame(
        columns=['索引', '二维码链接', '主图链接', '关键词', '商品链接', '标题', '店铺', '发货地', '评论数', 'SKU', '属性'])
    # 搜索关键词列表
    keywords = data.get('keyword').split(',')
    # 需要销量前几个店铺列表
    store_nums = [int(x) for x in data.get('store_num').split(',')]

    # 筛选关键词-黑名单和白名单，列表可为空、（自行更改）
    black_lists = [x.split(' ') for x in data.get('inputVal1').split(',')]
    white_lists = [x.split(' ') for x in data.get('inputVal2').split(',')]
    print(keywords, store_nums, black_lists, white_lists)
    # 获取前端输入的表名
    table_name = data.get('table_name')
    # 添加保持登录的数据路径：安装目录一般在C:\Users\****\AppData\Local\Google\Chrome\User Data
    # 该变量实际后续代码没用到
    user_data_dir = r"C:\Users\EDY\AppData\Local\Google\Chrome\User Data"

    show_true_popup("已点击，请等待···")
    # 创建浏览器驱动和等待参数
    driver, wait = jd_create_driver(user_data_dir)
    # 清除浏览器缓存
    driver.execute_cdp_cmd('Network.clearBrowserCache', {})
    # 清除所有的 Cookie
    driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
    driver.delete_all_cookies()
    # driver.execute_script("window.sessionStorage.clear()")
    # 登录操作（登录信息失效则须人工介入扫码）
    jd_login(driver, wait)
    for keyword, store_num, black_list, white_list in zip(keywords, store_nums, black_lists, white_lists):
        sent_keyword(driver, keyword)
        # 先获取搜索页信息
        dir_data = jd_get_dir_info(driver, jd_save_path_dir, store_num, keyword)
        # # 获取包括详情页内的所有信息
        all_data = jd_get_all_data(dir_data, driver, all_url, keyword)
        # 筛选数据
        filter_data1 = jd_filter_data(white_list, black_list, all_data)
        # 合并不同关键词的数据
        all_data2 = pd.concat([all_data2, filter_data1], ignore_index=True)
        # 清除浏览器缓存
        # driver.execute_script("window.localStorage.clear()")
        # driver.execute_script("window.sessionStorage.clear()")
    # 筛选并保存数据
    all_data2.to_excel(rf'{jd_save_path_dir}\jd-{table_name}.xlsx', index=False)
    # 执行关闭浏览器的 CDP 命令
    driver.execute_cdp_cmd('Browser.close', {})
    # 生成html文件
    html_content = jd_show_on_html(jd_save_path_dir, all_data2, table_name)
    # 转换html代码，即设计商品信息呈现排版
    table_content = jd_transform_table(html_content)
    # table_content = re.search(r'<table border="1" class="dataframe">(.*?)</table>', html_content, re.DOTALL)
    if not table_content:
        table_content = '异常，表格为空'
    # msg = rf'文件路径为{save_path_dir}\jd-{keyword}.html'
    return jsonify({'success': True, 'msg': table_content})


@app.route('/start_jd_auto', methods=['POST'])
def start_jd_auto():
    """ 对应京东操作页（机器查价版本）中的启动按钮 """
    data = request.get_json()
    all_url = []
    all_data2 = pd.DataFrame(
        columns=['索引', '二维码链接', '主图链接', '关键词', '商品链接', '标题', '店铺', '发货地', '评论数', 'SKU', '属性'])
    # 搜索关键词
    keywords = data.get('keyword').split(',')
    # 需要销量前几个店铺(修改数字)
    store_nums = [int(x) for x in data.get('store_num').split(',')]

    # 筛选关键词-黑名单和白名单，列表可为空、（自行更改）
    black_lists = [x.split(' ') for x in data.get('inputVal1').split(',')]
    white_lists = [x.split(' ') for x in data.get('inputVal2').split(',')]
    print(keywords, store_nums, black_lists, white_lists)
    # 获取前端输入的表名
    table_name = data.get('table_name')
    # 添加保持登录的数据路径：安装目录一般在C:\Users\****\AppData\Local\Google\Chrome\User Data
    # 该变量实际后续代码没用到
    user_data_dir = r"C:\Users\EDY\AppData\Local\Google\Chrome\User Data"

    show_true_popup("已点击，请等待···")
    # 创建浏览器驱动和等待参数
    driver, wait = jd_create_driver(user_data_dir)
    # 清除浏览器缓存
    driver.execute_cdp_cmd('Network.clearBrowserCache', {})
    # 清除所有的 Cookie
    driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
    driver.delete_all_cookies()
    # 登录操作（登录信息失效则须人工介入扫码）
    jd_login(driver, wait)
    for keyword, store_num, black_list, white_list in zip(keywords, store_nums, black_lists, white_lists):
        sent_keyword(driver, keyword)
        # 先获取搜索页信息
        dir_data = jd_get_dir_info(driver, jd_save_path_dir, store_num, keyword)
        # # 获取包括详情页内的所有信息
        all_data = jd_get_all_data(dir_data, driver, all_url, keyword)
        # 筛选数据
        filter_data1 = jd_filter_data(white_list, black_list, all_data)
        # 合并不同关键词的数据
        all_data2 = pd.concat([all_data2, filter_data1], ignore_index=True)
        # 清除浏览器缓存
        driver.execute_cdp_cmd('Network.clearBrowserCache', {})
        # driver.execute_script("window.localStorage.clear()")
        # driver.execute_script("window.sessionStorage.clear()")
    all_data2.to_excel(rf'{jd_save_path_dir}\jd-{table_name}.xlsx', index=False)
    # 执行关闭浏览器的 CDP 命令
    driver.execute_cdp_cmd('Browser.close', {})
    # 生成html文件
    html_content = jd_show_on_html(jd_save_path_dir, all_data2, table_name)
    # 转换html代码，即设计商品信息前端呈现排版
    table_content = jd_transform_table2(html_content)
    # table_content = re.search(r'<table border="1" class="dataframe">(.*?)</table>', html_content, re.DOTALL)
    if not table_content:
        table_content = '异常，表格为空'
    # msg = rf'文件路径为{save_path_dir}\jd-{keyword}.html'
    return jsonify({'success': True, 'msg': table_content})


@app.route('/start_tb_dir', methods=['POST'])
def start_tb_dir():
    """ 对应淘宝操作页中的启动爬取目录页按钮 """
    global dir_data
    data = request.get_json()
    # 搜索关键词
    keyword = data.get('keyword')
    show_true_popup("已点击，请等待···")
    # 创建浏览器驱动
    driver, wait = dir_create_driver()
    # 清除浏览器缓存
    driver.execute_cdp_cmd('Network.clearBrowserCache', {})
    driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
    # 清除所有的 Cookie
    # driver.delete_all_cookies()
    time.sleep(1)
    # 登录并自动点击
    login_click(driver, wait, keyword)
    # 获取淘宝搜索页数据
    types, links, titles, stores, nums, pics, msg1 = get_dir_info(driver, wait, keyword)
    # 处理并划分两种类型数据
    dir_data = process_dir_data(keyword, types, links, titles, stores, nums, pics)
    # 统计所有行标题出现的词频并保存excel
    msg2 = count_and_save(dir_data, tb_save_path_dir, keyword)
    msg = msg1 + '\n' + msg2
    # 执行关闭浏览器的 CDP 命令
    driver.execute_cdp_cmd('Browser.close', {})
    return jsonify({'success': True, 'msg': msg})


@app.route('/tb_uploadFile', methods=['POST'])
def tb_upload_file():
    """ 对应淘宝操作页中的 “导入筛选词文件” 按钮 """
    uploaded_file = request.files['file']  # 获取上传的文件
    file_contents = uploaded_file.read().decode('utf-8')  # 读取文件内容
    print(file_contents)
    return jsonify({'success': True, 'msg': file_contents})


def tb_transform_table(html_str, keyword):
    """ 搜索页商品信息html展示转换 """
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_str, 'html.parser')
    # 获取表格元素
    table = soup.select_one('table > tbody')

    # 如果有历史勾选记录文件
    if os.path.exists(rf"{tb_save_path_dir}\localStorage\tb-{keyword}-record.xlsx"):
        record_table = pd.read_excel(rf"{tb_save_path_dir}\localStorage\tb-{keyword}-record.xlsx")
        last_checked = record_table.loc[record_table['是否保留'], '商品ID'].tolist()
        last_checked = [str(num) for num in last_checked]
        # 创建新的 HTML 结构
        new_html = '<div class="grid-container">'
        # 遍历每一行<tr>
        for row in table.find_all('tr'):
            # new_html += '<div class="grid-item">'
            # 获取每个字段的值
            keyword = row.select('td')[0].text
            link = row.select('td a')[0]['href']
            img_src = row.select('td img')[0]['src']
            type = row.select('td')[2].text
            whole_title = row.select('td')[3].text
            title = row.select('td')[3].text[:12] + '...' + row.select('td')[3].text[-12:]  # 标题过长部分隐藏
            item_id = row.select('td')[4].text
            shop = row.select('td')[5].text
            num_of_customers = row.select('td')[6].text
            # is_reserved = row.select('td input')[0]['class']
            # print(item_id)
            # print(last_checked)
            if str(item_id) in last_checked:
                is_reserved = '<input class ="fill-input1" type="checkbox" checked>'
                # print("在")
            else:
                # print("不在")
                is_reserved = '<input class ="fill-input1" type="checkbox">'

            # 构造新 HTML 结构
            new_html += f'''
                <div class="grid-item">
                    <div class="item-container">
                        <a href="{link}">
                            <img src="{img_src}" height=150 width=150 alt="" title="{keyword}">
                        </a>
                        <div class="item-info">
                            <div class="reserved">
                                {is_reserved}
                            </div>
                            <div class="type">{type}</div>
                            <div class="num-of-customers">{num_of_customers} 收货</div>
                        </div>
                    </div>
                    <div class="info">
                        <div class="title" title="{whole_title}">{title}</div>
                        <div class="shop">{shop}</div>
                        <div class="item-id">ID:{item_id}</div>
                    </div>
                </div>
            '''
            # new_html += '\n'
        new_html += '</div>'
    else:
        # 创建新的 HTML 结构
        new_html = '<div class="grid-container">'
        # 遍历每一行<tr>
        for row in table.find_all('tr'):
            # new_html += '<div class="grid-item">'

            # 获取每个字段的值
            keyword = row.select('td')[0].text
            link = row.select('td a')[0]['href']
            img_src = row.select('td img')[0]['src']
            type = row.select('td')[2].text
            whole_title = row.select('td')[3].text
            title = row.select('td')[3].text[:20] + '...'  # 标题过长部分隐藏
            item_id = row.select('td')[4].text
            shop = row.select('td')[5].text
            num_of_customers = row.select('td')[6].text
            is_reserved = row.select('td input')[0]['class']
            # is_reserved = '< input class ="fill-input1" type="checkbox" checked >'

            # 构造新 HTML 结构
            new_html += f'''
                <div class="grid-item">
                    <div class="item-container">
                        <a href="{link}">
                            <img src="{img_src}" height=150 width=150 alt="" title="{keyword}">
                        </a>
                        <div class="item-info">
                            <div class="reserved">
                                <input class="{is_reserved[0]}" type="checkbox">
                            </div>
                            <div class="type">{type}</div>
                            <div class="num-of-customers">{num_of_customers} 收货</div>
                        </div>
                    </div>
                    <div class="info">
                        <div class="title" title="{whole_title}">{title}</div>
                        <div class="shop">{shop}</div>
                        <div class="item-id">ID:{item_id}</div>
                    </div>
                </div>
            '''
            # new_html += '\n'
        new_html += '</div>'

    return new_html


@app.route('/generate_html', methods=['POST'])
def generate_html():
    """ 对应淘宝操作页中的 “生成html” 按钮 """
    global dir_data
    data = request.get_json()
    # 搜索关键词
    data_range = data.get('data_range')
    keyword = data.get('keyword')
    # 读取筛选词数据
    input_val = str(data.get('inputVal'))
    # 筛选词为空的情况
    if input_val == '':
        filter_data = dir_data.copy()
    else:
        black_list = input_val.split(' ')
        print(black_list)
        black_filter = dir_data['标题'].str.contains('|'.join(black_list), case=False, na=False)
        filter_data = dir_data[~black_filter]

    # 生成html文件
    generate_msg, html_content = show_dir_html(data_range, filter_data, tb_save_path_dir, keyword)
    # 转换html代码，即设计商品信息呈现排版
    table_content = tb_transform_table(html_content, keyword)
    if not table_content:
        table_content = '异常，表格为空'
    return jsonify({'success': True, 'msg': table_content})


@app.route('/tb_export-csv', methods=['POST'])
def tb_export_csv():
    """ 对应淘宝操作页中的 “确认勾选” 按钮 """
    data = request.get_json()
    keyword = data['keyword']
    record_data = data['record_data']
    result_data = pd.DataFrame(record_data, columns=['商品链接', '商品ID', '是否保留'])
    # 保存到localStorage文件夹，即含历史勾选信息的记录信息
    result_data.to_excel(rf'{tb_save_path_dir}\localStorage\tb-{keyword}-record.xlsx', index=False)

    return jsonify({'success': True})


@app.route('/start_tb_detail', methods=['POST'])
def start_tb_detail():
    """ 对应淘宝操作页中的启动爬取详情页按钮 """
    data = request.get_json()
    data_range = data.get('data_range')
    is_tax = data.get('is_tax')
    keyword = data.get('keyword')
    # 创建浏览器驱动
    driver, wait = create_driver()
    # 清除浏览器缓存
    driver.execute_cdp_cmd('Network.clearBrowserCache', {})
    # 清除所有的 Cookie
    driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
    # driver.delete_all_cookies()
    # 刷新页面
    driver.refresh()
    # 筛选出勾到的数据
    record_data = pd.read_excel(rf'{tb_save_path_dir}\localStorage\tb-{keyword}-record.xlsx')
    reserve_data = record_data[record_data['是否保留']]
    reserve_id_list = reserve_data['商品ID'].tolist()
    dir_data = pd.read_excel(rf'{tb_save_path_dir}\搜索页\tb-{keyword}-dir.xlsx')
    filter_data = dir_data[dir_data['商品ID'].isin(reserve_id_list)]
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

    if is_tax == '保税区':
        detail_data = detail_data[detail_data['是否保税区'] == '保税区发货']
    if is_tax == '非保税区':
        detail_data = detail_data[detail_data['是否保税区'] != '保税区发货']

    detail_data.to_excel(rf'{tb_save_path_dir}\详情页\tb-{keyword}-detail.xlsx', index=False)
    # 生成html文件
    html_content = show_detail_html(detail_data, tb_save_path_dir, keyword)

    # 执行关闭浏览器的 CDP 命令
    driver.execute_cdp_cmd('Browser.close', {})
    # 获取部分html代码展示在网站
    table_content = re.search(r'<table border="1" class="dataframe">(.*?)</table>', html_content, re.DOTALL)
    if table_content:
        table_content = table_content.group()
    else:
        table_content = '异常，表格为空'
    # msg = rf'详情页数据保存路径为: {save_path}\tb-{keyword}-detail.xlsx'
    return jsonify({'success': True, 'msg': table_content})


if __name__ == '__main__':
    # 网站运行端口号
    app.run(port=5001)