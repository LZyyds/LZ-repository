from flask import Flask, render_template, request, jsonify, g
from crawl_sohu import SohuSpider
from public_funs import *
from datetime import datetime, timedelta
from collections import defaultdict
import pymysql
import matplotlib.pyplot as plt
import io
import tkinter as tk
import os
import matplotlib.font_manager as font_manager
import pandas as pd
import paddlehub as hub

# 设置中文字体为SimHei
font_path = r'./static/SimHei.ttf'  # 根据实际字体文件的路径进行修改
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
# 数据库连接信息
mysql_connect_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'sohu',
}
app = Flask(__name__)
app.static_folder = os.path.join(app.root_path, 'static')
app.template_folder = os.path.join(app.root_path, 'templates')
app.debug = True


class SentimentAnalysisModel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.senta = hub.Module(name="senta_lstm")
        return cls._instance


def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(host=mysql_connect_config['host'],
                               user=mysql_connect_config['user'],
                               password=mysql_connect_config['password'],
                               database=mysql_connect_config['database'],
                               charset='utf8mb4')
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.teardown_appcontext
def teardown_db(exception):
    close_db()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/index')
def home():
    return index()


@app.route('/start_crawl')
def start_crawl():
    return render_template("start_crawl.html")



@app.route('/data_screen')
def data_screen():
    # 连接数据库
    conn = get_db()
    cursor = conn.cursor()

    queries = [
        ("新闻", "chart_data1"),
        ("科技", "chart_data2"),
        ("汽车", "chart_data3"),
        ("财经", "chart_data4"),
        ("娱乐", "chart_data5"),
    ]

    chart_data = defaultdict(list)

    for table, chart_name in queries:
        job_types = []
        num = []
        sql = f"select `栏目`,count(`栏目`) count from `{table}` group by `栏目` ORDER BY count DESC;"
        cursor.execute(sql)
        data = cursor.fetchall()

        for item in data:
            job_types.append(str(item[0]))
            num.append(item[1])

        for i in range(len(job_types)):
            chart_data[chart_name].append({
                'value': num[i],
                'name': job_types[i]
            })

    cursor.close()

    return render_template("data_screen.html", **chart_data)


@app.route('/data_mining', methods=['POST', 'GET'])
def data_mining():
    data_list = []
    keyword = request.args.get('keyword', '')
    time = request.args.get('time')
    if time == "last_week":
        start_date = datetime.now() - timedelta(days=7)
    elif time == "last_month":
        start_date = datetime.now() - timedelta(days=30)
    else:
        start_date = datetime(1970, 1, 1)
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    # 连接数据库
    conn = get_db()
    cursor = conn.cursor()
    # 构建查询条件
    condition = "`发布时间` >= %s"
    params = [start_date_str] * 5  # 为每个表提供一个参数
    if len(keyword) != 0:
        condition += " AND `正文` LIKE %s"
        params.extend([f"%{keyword}%"] * 5)  # 为每个表提供一个参数
    # 构建查询sql语句
    sql = f"""
    (SELECT * FROM `新闻` WHERE {condition})
    UNION ALL
    (SELECT * FROM `娱乐` WHERE {condition})
    UNION ALL
    (SELECT * FROM `汽车` WHERE {condition})
    UNION ALL
    (SELECT * FROM `科技` WHERE {condition})
    UNION ALL
    (SELECT * FROM `财经` WHERE {condition})
    ORDER BY `发布时间` DESC;
    """
    cursor.execute(sql, params)
    data = cursor.fetchall()
    for item in data:
        data_list.append(item)
    cursor.close()
    current_page = int(request.args.get('page', 1))  # 获取URL参数中的页码值，默认为1
    total_pages = len(data_list) // 30  # 计算总页数
    print(len(data_list))

    return render_template("data_mining.html", data_list=data_list, keyword=keyword, time=time,
                           current_page=current_page, total_pages=total_pages)


@app.route('/translate', methods=['POST', 'GET'])
def translate_text():
    response = request.get_json()
    text = response.get('text', '404')
    if len(text) > 5000:
        text = text[:5000]
    result = translate(text)

    return jsonify({'success': True, 'result': result})


@app.route('/get_keywords', methods=['POST', 'GET'])
def get_keywords():
    response = request.get_json()
    text = response.get('text', '404')
    if text == '404':
        result = text
    else:
        text = text.strip().replace(' ', '').replace('\n', '')
        result1 = tf_idf(text)
        result2 = TextRank(text)
        result3 = lsi(text)
        result = result1 + result2 + result3

    return jsonify({'success': True, 'result': result})


@app.route('/sent_lstm', methods=['POST', 'GET'])
def sent_lstm():
    response = request.get_json()
    text = response.get('text', '404')
    if text == '404':
        result = text
    else:
        senta_model = SentimentAnalysisModel()
        text = text.strip().replace(' ', '').replace('\n', '')
        text_list = [text]
        result_list = senta_model.senta.sentiment_classify(texts=text_list)
        result_dict = result_list[0]
        result = f'LSTM模型情感分析结果为：\n' \
                 f'"sentiment_key": {result_dict["sentiment_key"]},\n' \
                 f'"positive_probs": {result_dict["positive_probs"]},\n' \
                 f'"negative_probs": {result_dict["negative_probs"]}'

    return jsonify({'success': True, 'result': result})


def data_view(table_name):
    data_list = []
    # 连接数据库
    conn = get_db()
    cursor = conn.cursor()
    # 查询sql语句
    sql = f"select * from `{table_name}` order by `发布时间` desc;"
    cursor.execute(sql)
    data = cursor.fetchall()
    for item in data:
        data_list.append(item)
    cursor.close()  # 关闭游标
    current_page = int(request.args.get('page', 1))  # 获取URL参数中的页码值，默认为1
    total_pages = len(data_list) // 30  # 计算总页数

    return data_list, current_page, total_pages


@app.route('/table_info', methods=['POST'])
def table_info():
    response = request.get_json()
    table_name = response.get('table_name')
    conn = get_db()
    cursor = conn.cursor()
    sql = f"select * from `{table_name}`;"
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
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
    conn = get_db()
    cursor = conn.cursor()
    count_sql = f"SELECT COUNT(*) FROM `{table_name}` WHERE `正文` = '\t' OR `正文` = '';"
    cursor.execute(count_sql)
    count = cursor.fetchone()[0]
    msg = f'{table_name} 表中有 {count} 条无效数据\n已删除···'
    delete_sql = f"DELETE FROM `{table_name}` WHERE `正文` = '\t' OR `正文` = '';"
    cursor.execute(delete_sql)
    # 提交更改
    cursor.connection.commit()
    cursor.close()

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


@app.route('/news')
def news_table():
    table_name = '新闻'
    data_list, current_page, total_pages = data_view(table_name)

    return render_template("data_view.html", data_list=data_list, table_name=table_name,
                           current_page=current_page, total_pages=total_pages)


@app.route('/yule')
def yule_table():
    table_name = '娱乐'
    data_list, current_page, total_pages = data_view(table_name)

    return render_template("data_view.html", data_list=data_list, table_name=table_name,
                           current_page=current_page, total_pages=total_pages)


@app.route('/car')
def car_table():
    table_name = '汽车'
    data_list, current_page, total_pages = data_view(table_name)

    return render_template("data_view.html", data_list=data_list, table_name=table_name,
                           current_page=current_page, total_pages=total_pages)


@app.route('/tech')
def tech_table():
    table_name = '科技'
    data_list, current_page, total_pages = data_view(table_name)

    return render_template("data_view.html", data_list=data_list, table_name=table_name,
                           current_page=current_page, total_pages=total_pages)


@app.route('/fina')
def fina_table():
    table_name = '财经'
    data_list, current_page, total_pages = data_view(table_name)

    return render_template("data_view.html", data_list=data_list, table_name=table_name,
                           current_page=current_page, total_pages=total_pages)



def show_popup(message):
    root = tk.Tk()
    root.title("Popup Message")

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


if __name__ == '__main__':
    app.run(port=5001)
