import io

from flask import Flask, render_template, request, g, Response, jsonify
from crawl_sohu import SohuSpider
import pymysql
import matplotlib.pyplot as plt
import re
import tkinter as tk
import csv
import os
import matplotlib.font_manager as font_manager
import pandas as pd
import bag

# 设置中文字体为SimHei
font_path = r'./static/SimHei.ttf'  # 根据实际字体文件的路径进行修改
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

app = Flask(__name__)
app.static_folder = os.path.join(app.root_path, 'static')
app.template_folder = os.path.join(app.root_path, 'templates')
app.debug = True
# 数据库连接信息
mysql_connect_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'sohu',
}


def connect_db():
    """
    获取数据库连接
    :return:
    """
    # 创建数据库连接
    conn = pymysql.connect(host=mysql_connect_config['host'],
                           user=mysql_connect_config['user'],
                           password=mysql_connect_config['password'],
                           database=mysql_connect_config['database'],
                           charset='utf8mb4')
    cursor = conn.cursor()
    return conn, cursor


def close_db(cursor, conn):
    # 关闭游标和连接
    cursor.close()
    conn.close()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/index')
def home():
    return index()


@app.route('/start_crawl')
def start_crawl():
    return render_template("start_crawl.html")


def data_review(table_name):
    data_list = []
    # 连接数据库
    conn, cursor = connect_db()
    # 查询sql语句
    sql = f"select * from `{table_name}` order by `发布时间` desc;"
    cursor.execute(sql)
    data = cursor.fetchall()
    for item in data:
        data_list.append(item)
    close_db(conn, cursor)

    current_page = int(request.args.get('page', 1))  # 获取URL参数中的页码值，默认为1
    total_pages = len(data_list) // 30  # 计算总页数

    return data_list, current_page, total_pages
@app.route('/news')
def news_table():
    table_name = '新闻'
    data_list, current_page, total_pages = data_review(table_name)

    return render_template("data_view.html", data_list=data_list, table_name=table_name,
                           current_page=current_page, total_pages=total_pages)


@app.route('/yule')
def yule_table():
    table_name = '娱乐'
    data_list, current_page, total_pages = data_review(table_name)

    return render_template("data_view.html", data_list=data_list, table_name=table_name,
                           current_page=current_page, total_pages=total_pages)


@app.route('/car')
def car_table():
    table_name = '汽车'
    data_list, current_page, total_pages = data_review(table_name)

    return render_template("data_view.html", data_list=data_list, table_name=table_name,
                           current_page=current_page, total_pages=total_pages)


@app.route('/tech')
def tech_table():
    table_name = '科技'
    data_list, current_page, total_pages = data_review(table_name)

    return render_template("data_view.html", data_list=data_list, table_name=table_name,
                           current_page=current_page, total_pages=total_pages)

@app.route('/fina')
def fina_table():
    table_name = '财经'
    data_list, current_page, total_pages = data_review(table_name)

    return render_template("data_view.html", data_list=data_list, table_name=table_name,
                           current_page=current_page, total_pages=total_pages)

@app.route('/table_info', methods=['POST'])
def table_info():
    response = request.get_json()
    table_name = response.get('table_name')
    conn, cursor = connect_db()
    sql = f"select * from `{table_name}`;"
    cursor.execute(sql)
    data = cursor.fetchall()
    close_db(conn, cursor)
    # 将数据转换为 DataFrame
    df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
    df = df.replace('', pd.NA).replace('\t', pd.NA)
    buffer = io.StringIO()
    df.info(buf=buffer, verbose=True)
    df_info_str = buffer.getvalue().replace("<class 'pandas.core.frame.DataFrame'>\n", '')

    return jsonify({'success': True, 'msg': df_info_str})

@app.route('/drop_null', methods=['POST'])
def drop_null():
    response = request.get_json()
    table_name = response.get('table_name')
    conn, cursor = connect_db()
    count_sql = f"SELECT COUNT(*) FROM `{table_name}` WHERE `正文` = '\t';"
    cursor.execute(count_sql)
    count = cursor.fetchone()[0]
    msg = f'{table_name} 表中有 {count} 条无效数据\n已删除···'
    delete_sql = f"DELETE FROM `{table_name}` WHERE `正文` = '\t';"
    cursor.execute(delete_sql)
    # 提交更改
    cursor.connection.commit()
    close_db(conn, cursor)

    return jsonify({'success': True, 'msg': msg})

@app.route('/crawl_news', methods=['POST'])
def crawl_news():
    article_type = '新闻'
    url_dict = {
        'https://www.sohu.com/xchannel/tag?key=%E6%96%B0%E9%97%BB-%E6%97%B6%E6%94%BF': [article_type, '时政'],
        'https://www.sohu.com/xchannel/tag?key=%E6%96%B0%E9%97%BB-%E5%9B%BD%E9%99%85': [article_type, '国际'],
        'https://www.sohu.com/xchannel/tag?key=%E6%96%B0%E9%97%BB-%E8%B4%A2%E7%BB%8F': [article_type, '财经'],
    }
    spider = SohuSpider(url_dict)
    spider.spider_main()
    return jsonify({'success': True, 'msg': spider.console})

@app.route('/crawl_yule', methods=['POST'])
def crawl_yule():
    article_type = '娱乐'
    url_dict = {
        'https://www.sohu.com/xchannel/tag?key=%E5%A8%B1%E4%B9%90-%E6%98%8E%E6%98%9F': [article_type, '明星'],
        'https://www.sohu.com/xchannel/tag?key=%E5%A8%B1%E4%B9%90-%E5%85%AB%E5%8D%A6': [article_type, '八卦'],
        'https://www.sohu.com/xchannel/tag?key=%E5%A8%B1%E4%B9%90-%E5%BD%B1%E8%A7%86%E9%9F%B3%E4%B9%90': [article_type,
                                                                                                          '影视音乐'],
        'https://www.sohu.com/xchannel/tag?key=%E5%A8%B1%E4%B9%90-%E7%BD%91%E7%BB%9C%E7%BA%A2%E4%BA%BA': [article_type,
                                                                                                          '网络红人'],
    }
    spider = SohuSpider(url_dict)
    spider.spider_main()
    return jsonify({'success': True, 'msg': spider.console})

@app.route('/crawl_car', methods=['POST'])
def crawl_car():
    article_type = '汽车'
    url_dict = {
        'https://www.sohu.com/xchannel/TURBd01EQTNNekV3': [article_type, '新车快报'],
        'https://www.sohu.com/xchannel/TURBd01EQTNNekV4': [article_type, '买车必看'],
        'https://www.sohu.com/xchannel/TURBd01EQTNNekV5': [article_type, '新能源'],
        'https://www.sohu.com/xchannel/TURBd01EQTNNekV6': [article_type, '车市行情'],
    }
    spider = SohuSpider(url_dict)
    spider.spider_main()
    return jsonify({'success': True, 'msg': spider.console})

@app.route('/crawl_tech', methods=['POST'])
def crawl_tech():
    article_type = '科技'
    url_dict = {
        'https://www.sohu.com/xchannel/tag?key=%E7%A7%91%E6%8A%80-%E9%80%9A%E8%AE%AF': [article_type, '通讯'],
        'https://www.sohu.com/xchannel/tag?key=%E7%A7%91%E6%8A%80-%E6%95%B0%E7%A0%81': [article_type, '数码'],
        'https://www.sohu.com/xchannel/tag?key=%E7%A7%91%E6%8A%80-%E6%99%BA%E8%83%BD%E7%A1%AC%E4%BB%B6': [article_type,
                                                                                                          '智能硬件'],
    }
    spider = SohuSpider(url_dict)
    spider.spider_main()
    return jsonify({'success': True, 'msg': spider.console})

@app.route('/crawl_fina', methods=['POST'])
def crawl_fina():
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
    return jsonify({'success': True, 'msg': spider.console})

@app.route('/job_types')
def job_types():
    # 连接数据库
    conn, cursor = connect_db()

    job_types1 = []
    num1 = []
    sql1 = "select `栏目`, count(`栏目`) count from `新闻` group by `栏目` ORDER BY count DESC;"
    cursor.execute(sql1)
    data1 = cursor.fetchall()
    for item in data1:
        job_types1.append(str(item[0]))
        num1.append(item[1])

    # 第二个查询
    job_types2 = []
    num2 = []
    sql2 = "select `发布省份`, count(`发布省份`) count from `娱乐` group by `发布省份` ORDER BY count DESC LIMIT 7;"
    cursor.execute(sql2)
    data2 = cursor.fetchall()
    for item in data2:
        job_types2.append(str(item[0]))
        num2.append(item[1])

    # 第三个查询
    job_types3 = []
    num3 = []
    sql3 = "select `栏目`, count(`栏目`) count from `财经` group by `栏目` ORDER BY count DESC;"
    cursor.execute(sql3)
    data3 = cursor.fetchall()
    for item in data3:
        job_types3.append(str(item[0]))
        num3.append(item[1])

    # 第四个查询
    job_types4 = []
    num4 = []
    sql4 = "select `栏目`, count(`栏目`) count from `汽车` group by `栏目` ORDER BY count DESC;"
    cursor.execute(sql4)
    data4 = cursor.fetchall()
    for item in data4:
        job_types4.append(str(item[0]))
        num4.append(item[1])

    cursor.close()
    conn.close()

    chart_data1 = []
    for i in range(len(job_types1)):
        chart_data1.append({
            'value': num1[i],
            'name': job_types1[i]
        })

    chart_data2 = []
    for i in range(len(job_types2)):
        chart_data2.append({
            'value': num2[i],
            'name': job_types2[i]
        })

    chart_data3 = []
    for i in range(len(job_types3)):
        chart_data3.append({
            'value': num3[i],
            'name': job_types3[i]
        })

    chart_data4 = []
    for i in range(len(job_types4)):
        chart_data4.append({
            'value': num4[i],
            'name': job_types4[i]
        })

    return render_template("job_types.html", chart_data1=chart_data1, chart_data2=chart_data2,
                           chart_data3=chart_data3, chart_data4=chart_data4)


# 添加数据的路由
# noinspection PyUnresolvedReferences
@app.route('/add', methods=['GET', 'POST'])
def add():
    return render_template('add.html')


# 导出数据的路由
# noinspection PyUnresolvedReferences
@app.route('/export')
def export():
    return render_template('export.html')


def is_excel_or_csv_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() in ['.xlsx', '.xls', '.xlsm']:
        return 'Excel'
    elif file_extension.lower() == '.csv':
        return 'CSV'
    else:
        return 'Unknown'


def field(path, sheet_name='Sheet1'):
    judge = is_excel_or_csv_file(path)
    if judge == 'Excel':
        data = bag.Bag.read_excel(path, sheet_name=sheet_name)
        return tuple(data[0])
    elif judge == 'CSV':
        data = bag.Bag.read_csv(path)
        return tuple(data[0])
    else:
        print('不支持的文件格式！')


def show_error_popup(message):
    root = tk.Tk()
    root.title("Error Message")

    # 设置窗口大小
    window_width = 300
    window_height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = screen_width - window_width - 500  # 将窗口定位到右下角，留一定的边距
    y = screen_height - window_height - 400
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 将窗口设置为最顶层
    root.attributes('-topmost', True)

    label = tk.Label(root, text=message, padx=20, pady=20)
    label.pack()

    root.mainloop()


def show_true_popup(message):
    root = tk.Tk()
    root.title("True Message")

    # 设置窗口大小和位置
    window_width = 300
    window_height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = screen_width - window_width - 500  # 将窗口定位到右下角，留一定的边距
    y = screen_height - window_height - 400
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 将窗口设置为最顶层
    root.attributes('-topmost', True)

    label = tk.Label(root, text=message, padx=20, pady=20)
    label.pack()

    def close_popup():
        root.destroy()

    # 设置定时器，在3秒后调用关闭弹窗函数
    root.after(3000, close_popup)

    root.mainloop()


def get_possible_field_values(cursor, table_name, field_name):
    query = "SELECT DISTINCT {} FROM {}".format(field_name, table_name)
    cursor.execute(query)
    results = cursor.fetchall()
    values = [row[0] for row in results]
    values.append('')
    return values


@app.route('/export_data', methods=['POST'])
def export_data():
    data = request.get_json()
    table_name = data['table_name']
    item = data['item']
    scene = data['scene']
    quantity = data['quantity']
    # 连接数据库
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    filename = os.path.join(app.static_folder, 'exported_data.csv')

    # 判断字段是否存在
    if not (f'{item}' in get_possible_field_values(cursor, f'{table_name}', 'item')) \
            or not (f'{scene}' in get_possible_field_values(cursor, f'{table_name}', 'scene')):
        msg = f"********* 该字段不存在 *********\n请检查是否输入正确信息"
        show_error_popup(msg)
        cursor.close()
        conn.close()
        return jsonify({'error': msg})

    try:
        # 导出整个表格数据
        if not bool(item) and not bool(scene) and not bool(quantity):
            # 查询数据
            sql = f'SELECT * FROM {table_name}'
            cursor.execute(sql)
            data = cursor.fetchall()

            # 导出数据为CSV文件
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['ID', 'Classification', 'Item', 'Scene', 'Brand', 'Trade', 'Job Types', 'Title', 'Content',
                     'types_of', 'tone', 'crowd', 'Keywords', 'Url'])
                writer.writerows(data)

        # 导出表格部分数据
        elif not bool(item) and not bool(scene) and bool(quantity):
            sql = f'SELECT * FROM {table_name} limit {quantity};'
            cursor.execute(sql)
            data = cursor.fetchall()

            # 导出数据为CSV文件
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['ID', 'Classification', 'Item', 'Scene', 'Brand', 'Trade', 'Job Types', 'Title', 'Content',
                     'types_of',
                     'tone', 'crowd', 'Keywords', 'Url'])
                writer.writerows(data)
        # 导出item的所有数据
        elif bool(item) and not bool(scene) and not bool(quantity):
            sql = f"SELECT * FROM {table_name} where item='{item}';"
            cursor.execute(sql)
            data = cursor.fetchall()

            # 导出数据为CSV文件
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['ID', 'Classification', 'Item', 'Scene', 'Brand', 'Trade', 'Job Types', 'Title', 'Content',
                     'types_of',
                     'tone', 'crowd', 'Keywords', 'Url'])
                writer.writerows(data)
        # 导出item的部分数据
        elif bool(item) and not bool(scene) and bool(quantity):
            sql = f"SELECT * FROM {table_name} where item='{item}' limit {quantity};"
            cursor.execute(sql)
            data = cursor.fetchall()

            # 导出数据为CSV文件
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['ID', 'Classification', 'Item', 'Scene', 'Brand', 'Trade', 'Job Types', 'Title', 'Content',
                     'types_of',
                     'tone', 'crowd', 'Keywords', 'Url'])
                writer.writerows(data)
        # 导出scene的所有数据
        elif not bool(item) and bool(scene) and not bool(quantity):
            sql = f"SELECT * FROM {table_name} where scene='{scene}';"
            cursor.execute(sql)
            data = cursor.fetchall()

            # 导出数据为CSV文件
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['ID', 'Classification', 'Item', 'Scene', 'Brand', 'Trade', 'Job Types', 'Title', 'Content',
                     'types_of',
                     'tone', 'crowd', 'Keywords', 'Url'])
                writer.writerows(data)
        # 导出scene的部分数据
        elif not bool(item) and bool(scene) and bool(quantity):
            sql = f"SELECT * FROM {table_name} where scene='{scene}' limit {quantity};"
            cursor.execute(sql)
            data = cursor.fetchall()

            # 导出数据为CSV文件
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['ID', 'Classification', 'Item', 'Scene', 'Brand', 'Trade', 'Job Types', 'Title', 'Content',
                     'types_of',
                     'tone', 'crowd', 'Keywords', 'Url'])
                writer.writerows(data)
        # 导出item和scene的所有数据
        elif bool(item) and bool(scene) and not bool(quantity):
            sql = f"SELECT * FROM {table_name} where item='{item}' and scene='{scene}';"
            cursor.execute(sql)
            data = cursor.fetchall()

            # 导出数据为CSV文件
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['ID', 'Classification', 'Item', 'Scene', 'Brand', 'Trade', 'Job Types', 'Title', 'Content',
                     'types_of',
                     'tone', 'crowd', 'Keywords', 'Url'])
                writer.writerows(data)
        # 导出item和scene相交的所有数据
        elif bool(item) and bool(scene) and not bool(quantity):
            sql = f"SELECT * FROM {table_name} where item='{item}' and scene='{scene}';"
            cursor.execute(sql)
            data = cursor.fetchall()

            # 导出数据为CSV文件
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['ID', 'Classification', 'Item', 'Scene', 'Brand', 'Trade', 'Job Types', 'Title', 'Content',
                     'types_of',
                     'tone', 'crowd', 'Keywords', 'Url'])
                writer.writerows(data)
        # 导出item和scene相交的部分数据
        elif bool(item) and bool(scene) and bool(quantity):
            sql = f"SELECT * FROM {table_name} where item='{item}' and scene='{scene}' limit {quantity};"
            cursor.execute(sql)
            data = cursor.fetchall()

            # 导出数据为CSV文件
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['ID', 'Classification', 'Item', 'Scene', 'Brand', 'Trade', 'Job Types', 'Title', 'Content',
                     'types_of',
                     'tone', 'crowd', 'Keywords', 'Url'])
                writer.writerows(data)

        # 显示导出成功信息
        show_true_popup("数据导出成功！！")

    except Exception as e:
        msg = f"导出数据时发生错误: {str(e)}"
        return jsonify({'error': msg})
    # 关闭数据库连接
    cursor.close()
    conn.close()

    return jsonify(filename)


@app.route('/get_data', methods=['POST'])
def get_data():
    table_name = request.form['table_name']
    offset = int(request.form.get('offset', 0))
    limit = 50  # 每次加载50条数据

    # 连接数据库
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # 查询数据
    sql = f'SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}'
    cursor.execute(sql)
    data = cursor.fetchall()

    # 关闭数据库连接
    cursor.close()
    conn.close()

    return jsonify(data)


@app.route('/get_data1', methods=['POST'])
def get_data1():
    data = request.get_json()
    table_name = data['table_name']

    result = []
    # 连接数据库
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # 查询数据
    sql = f'SELECT * FROM {table_name}'
    cursor.execute(sql)
    data = cursor.fetchall()

    for i in data:
        tup = i[1:4]
        if tup not in result:
            result.append(tup)

    # 关闭数据库连接
    cursor.close()
    conn.close()

    return jsonify(result)


@app.route('/upload_data', methods=['POST'])
def upload_data():
    db_path = database_path
    save_dir = os.path.dirname(db_path)
    table_name = request.form.get('table_name')
    file = request.files['file']
    sheet_name = 'Sheet1'  # 待优化

    with sqlite3.connect(db_path) as conn:
        file_path = os.path.join(save_dir, file.filename)
        file.save(file_path)

        s = field(file_path, sheet_name=sheet_name)
        count = list(s)
        VALUE = '?' * len(count)
        fie_tit = f"INSERT INTO {table_name} ({', '.join(s)}) VALUES ({','.join(VALUE)})"

        data = bag.Bag.read_excel(file_path)
        for info in data[1:]:
            conn.execute(fie_tit, tuple(info))
        conn.commit()

    return jsonify({'success': True, 'message': '上传成功'})


@app.route('/add_table')
def add_table():
    return render_template('start_crawl.html')


@app.route('/createTable', methods=['POST'])
def create_table():
    data = request.get_json()
    tableNameCn = data.get('tableNameCn')
    tableNameEn = data.get('tableNameEn')
    dynamicFields = data.get('dynamicFields')

    if tableNameCn is None:
        return jsonify({'error': '表格名字不能为空'})

    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    c.execute(f"CREATE TABLE IF NOT EXISTS {tableNameEn} ("
              f"id INTEGER PRIMARY KEY, "
              f"classification TEXT, "
              f"item TEXT, "
              f"scene TEXT)")

    for field in dynamicFields:
        fieldName = field.get('name')
        fieldType = field.get('type')
        # 检查列是否存在
        c.execute(f"PRAGMA table_info({tableNameEn})")
        columns = [column[1] for column in c.fetchall()]
        if fieldName not in columns:
            # 添加新列
            c.execute(f"ALTER TABLE {tableNameEn} ADD COLUMN {fieldName} {fieldType}")

    conn.commit()
    conn.close()

    additional_content = f'<option value="{tableNameEn}">{tableNameCn}</option>'

    html_file_path = './templates/export.html'  # 导出html
    html_file_path1 = './templates/add.html'  # 导入html

    with open(html_file_path, mode='r', encoding='utf8') as file:
        html_content = file.read()
    modified_html_content = html_content.replace("</select>", additional_content + "</select>")

    ls = re.findall(r'<option.*?value="(.*?)">', html_content, re.S)
    if tableNameEn in ls:
        return jsonify({'message': '表格已存在，无需创建'})
    else:
        '''导出html增加下拉列表值'''
        with open(html_file_path, "w", encoding="utf-8") as w_file:
            w_file.write(modified_html_content)
        '''导入html增加下拉列表值'''
        with open(html_file_path1, mode='r', encoding='utf8') as file1:
            html_content1 = file1.read()
        modified_html_content1 = html_content1.replace("</select>", additional_content + "</select>")
        with open(html_file_path1, "w", encoding="utf-8") as w_file1:
            w_file1.write(modified_html_content1)

    return jsonify({'message': '表格创建成功，请刷新页面加载表格'})


if __name__ == '__main__':
    app.run(port=5001)
