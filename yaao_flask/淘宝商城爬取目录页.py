# -*- coding = utf-8 -*-
# @Time :  2023/12/12 10:31
# @Author : 梁正
# @File : 淘宝商城爬取目录页.py
# @Software : PyCharm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import pandas as pd
import tkinter as tk
import pyautogui
import random
import jieba
import time
import re


def dir_create_driver():
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


def login_click(driver, wait, keyword):
    """ 登录并自动点击 """
    driver.get('https://www.taobao.com/')
    time.sleep(2)
    # 登录按钮
    login_btn = driver.find_elements(By.CSS_SELECTOR,
                                     '.member-logout.J_UserMemberLogout > a.btn-login.ml1.tb-bg.weight')
    # 如果是未登录状态,须先人工扫码登录
    if '登录' in login_btn[0].text:
        login_btn[0].click()
        show_true_popup("请人工扫码处理")
        time.sleep(2)

        # 转到新窗口
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        # # 二维码按钮
        # login_QR_btn = wait.until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, '#login > div.corner-icon-view.view-type-qrcode > i')))
        # login_QR_btn.click()
        # time.sleep(1)

        # 等待用户扫码操作（最多30秒）
        WebDriverWait(driver, 80).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))

    # 关键词输入
    keyword_input = driver.find_element(By.CSS_SELECTOR, '#q')
    keyword_input.clear()
    # 输入
    keyword_input.send_keys(keyword)
    # 模拟按下回车键
    keyword_input.send_keys(Keys.RETURN)
    time.sleep(2)
    # # 识别是否成功进入
    # iframe = driver.find_elements(By.CSS_SELECTOR, 'body > div.J_MIDDLEWARE_FRAME_WIDGET > iframe')
    # if iframe:
    #     time.sleep(20)
    # 模拟点击按销量排行
    sales_btn = WebDriverWait(driver, 40).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, '.next-tabs-bar.SortBar--customTab--OpWQmfy > div > div > div > ul > li:nth-child(2) > div')))
    # try:
    sales_btn.click()
    time.sleep(2)
    sales_btn.click()
    # except:
    #     time.sleep(30)
    #     sales_btn.click()


def get_dir_info(driver, wait, keyword):
    """ 爬取商城搜索页信息 """
    # 判断天猫类型的特征列表
    tm_label_list = [
        "https://gw.alicdn.com/imgextra/i4/O1CN01cmlWEd1SQssmcMUM9_!!6000000002242-2-tps-291-42.png",
        "https://gw.alicdn.com/tfs/TB10a5neaL7gK0jSZFBXXXZZpXa-78-42.png",
        "https://gw.alicdn.com/imgextra/i1/O1CN01HHb1vo28pLirwhfg7_!!6000000007981-2-tps-146-42.png",
        "https://gw.alicdn.com/tfs/TB1LWu6fbH1gK0jSZFwXXc7aXXa-135-42.png",
        "https://gw.alicdn.com/imgextra/i1/O1CN01lXCp071WzTG4DaI73_!!6000000002859-2-tps-251-42.png",
        "https://img.alicdn.com/imgextra/i3/O1CN01T2nOUf1fq9kXx0Xz7_!!6000000004057-2-tps-214-48.png",
        "https://img.alicdn.com/imgextra/i1/O1CN01oEz0tT202mztuDuI8_!!6000000006792-2-tps-204-42.png",
        "https://img.alicdn.com/imgextra/i2/O1CN01UB8sl71Ij4TJLirRd_!!6000000000928-2-tps-198-42.png",
        "https://img.alicdn.com/imgextra/i2/O1CN01HD5QkO1TS5Z0NAmWH_!!6000000002380-2-tps-242-42.png",
        "https://img.alicdn.com/imgextra/i1/O1CN015ewfNk1r8RLigDVZA_!!6000000005586-2-tps-242-42.png"
    ]
    console_output = []
    links = []
    titles = []
    stores = []
    nums = []
    types = []
    pics = []
    total_count = 0
    i = 1
    # 循环翻页爬取,最多到15页
    for i in range(1, 3, 1):
        time.sleep(random.uniform(2, 3))
        # 防止验证码出现，增加人工介入时间
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.next-tabs-bar.SortBar--customTab--OpWQmfy > div > div > div > ul > li:nth-child(2) > div')))
        except TimeoutException:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.next-tabs-bar.SortBar--customTab--OpWQmfy > div > div > div > ul > li:nth-child(2) > div')))
            time.sleep(1)

        print(f'正在爬取[{keyword}]的第[{i}]页')
        # while not is_at_bottom():
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #     time.sleep(1)
        # 商品链接
        for l in driver.find_elements(By.CSS_SELECTOR,
                                      '.PageContent--contentWrap--mep7AEm > div.LeftLay--leftWrap--xBQipVc > div.LeftLay--leftContent--AMmPNfB > div.Content--content--sgSCZ12 > div > div:nth-child(n) > a'):
            links.append(l.get_attribute('href'))
            content = l.get_attribute("outerHTML")

            # 构造并识别’类型‘字段('淘宝'还是'天猫')
            if '>全球购</span>' in content:
                types.append('全球购')
            elif any(x in content for x in tm_label_list):
                types.append('天猫')
            else:
                types.append('常规')
        num_count = [l.text.strip() for l in driver.find_elements(By.CSS_SELECTOR,
                                                                  '.PageContent--contentWrap--mep7AEm > div.LeftLay--leftWrap--xBQipVc > div.LeftLay--leftContent--AMmPNfB > div.Content--content--sgSCZ12 > div > div:nth-child(n) > a')]
        print(f"该页共有[{len(num_count)}]个商品")
        total_count += len(num_count)
        # 触发加载所有主图操作
        for x in range(0, 42, 2):
            try:
                # 定位要悬停的元素
                element_to_hover_over = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                f".PageContent--contentWrap--mep7AEm > div.LeftLay--leftWrap--xBQipVc > div.LeftLay--leftContent--AMmPNfB > div.Content--content--sgSCZ12 > div > div:nth-child({len(num_count) - x}) > a")))

                # 使用ActionChains模拟鼠标悬停操作
                ActionChains(driver).move_to_element(element_to_hover_over).perform()
            except Exception:
                break
        # 商品主图链接
        for p in driver.find_elements(By.CLASS_NAME, 'MainPic--mainPic--rcLNaCv'):
            pics.append(p.get_attribute('src'))
        # 商品标题
        for t in driver.find_elements(By.CSS_SELECTOR,
                                      '.Content--content--sgSCZ12 > div > div:nth-child(n) > a > div > div.Card--mainPicAndDesc--wvcDXaK > div.Title--descWrapper--HqxzYq0 > div > span'):
            titles.append(t.text.strip())
        # 商品店铺
        for s in driver.find_elements(By.CSS_SELECTOR,
                                      '.Content--content--sgSCZ12 > div > div:nth-child(n) > a > div > div.ShopInfo--shopInfo--ORFs6rK > div.ShopInfo--TextAndPic--yH0AZfx > a'):
            stores.append(s.text.strip())
        # 收货人数
        for n in driver.find_elements(By.CSS_SELECTOR,
                                      '.Content--content--sgSCZ12 > div > div:nth-child(n) > a > div > div.Card--mainPicAndDesc--wvcDXaK > div.Price--priceWrapper--Q0Dn7pN > span.Price--realSales--FhTZc7U'):
            nums.append(n.text.strip().split('人')[0])

        # 如果出现收货人数为0，则跳出循环，停止翻页
        if '0' in nums:
            break

        # 定位输入页数按钮元素
        page_input = driver.find_elements(By.CSS_SELECTOR,
                                         '.Pagination--pgWrap--kfPsaVv > div > div > span.next-input.next-medium.next-pagination-jump-input > input')
        if page_input:
            page_input = page_input[0]
            page_input.clear()
            # 输入数字
            page_input.send_keys(f'{i + 1}')
            # 模拟按下回车键
            page_input.send_keys(Keys.RETURN)
        # 如果没有输入框
        else:
            next_button = driver.find_elements(By.CSS_SELECTOR, '.Pagination--pgWrap--kfPsaVv > div > div > button.next-btn.next-medium.next-btn-normal.next-pagination-item.next-next > span')
            if next_button:
                next_button[0].click()

    msg = f'[{keyword}]一共爬取了{i}页，有{total_count}个商品'
    print(msg)
    return types, links, titles, stores, nums, pics, msg


def process_dir_data(keyword, types, links, titles, stores, nums, pics):
    """ 处理数据集 """
    ids = [l.split('&ns')[0].split('id=')[-1] for l in links]
    # 将结果添加到 DataFrame 中
    all_data = pd.DataFrame({
        '关键词': [f'{keyword}'] * len(links),
        '商品链接': links,
        '类型': types,
        '标题': titles,
        '商品ID': ids,
        '店铺': stores,
        '收货人数': nums,
        '主图链接': pics,
    })
    all_data['商品链接'] = all_data['商品链接'].str.replace('#detail', '')
    print(f"数据已爬完")

    print(all_data.tail(5))
    # 查看重复值
    print(f'数据中有%d条重复数据' % all_data.duplicated().sum())
    # 删除重复数据
    all_data.drop_duplicates(inplace=True)

    return all_data


def show_dir_html(data_range, filter_data, save_path, keyword):
    """ 将数据展示在html网页上 """
    def main_pic_to_html(image_url):
        return f'<img src="{image_url}" height=150 width=150 alt="">'

    def qr_link_to_html(image_url):
        return f'<img src="{image_url}" height=130 width=130 alt="">'

    def link_html(link_url):
        return f'<a href="{link_url}">{link_url}</a>'

    # 创建一个新的 DataFrame，同时插入空白列
    modified_data = filter_data.copy()
    if data_range == '淘宝':
        modified_data = modified_data[modified_data['类型'] != '天猫']
    elif data_range == '天猫':
        modified_data = modified_data[modified_data['类型'] == '天猫']
    else:
        modified_data = modified_data

    modified_data['是否保留'] = ''

    # 将 DataFrame 导出为 HTML 文件，并在指定字段上应用自定义函数
    # modified_data['二维码链接'] = modified_data['二维码链接'].apply(qr_link_to_html)
    modified_data['主图链接'] = modified_data['主图链接'].apply(main_pic_to_html)
    modified_data['商品链接'] = modified_data['商品链接'].apply(link_html)

    # 重新设置索引
    modified_data.reset_index(drop=True, inplace=True)
    # 将 DataFrame 转换为 HTML 字符串
    html_content = modified_data.to_html(index=True, escape=False)

    # 在导出 HTML 文件之前，将包含 DataFrame 内容的字符串进行处理
    html_header = """
<!DOCTYPE html>
<html>
<head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>淘宝test</title>
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
        .fill-input1 {
            width: 20px; /* 调整宽度 */
            height: 20px; /* 调整高度 */
            vertical-align: middle; /* 垂直居中对齐 */
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
  // 获取所有带有类名"fill-input1"的复选框元素
  var inputElements = document.querySelectorAll('.fill-input1');

  // 为每个复选框元素设置不同的id
  inputElements.forEach(function(inputElement, index) {
    inputElement.id = 'input-' + (index + 1);
  });

  // 从本地存储中获取之前保存的值，并将其赋值给复选框的checked属性
  inputElements.forEach(function(inputElement) {
    var savedValue = localStorage.getItem(inputElement.id + '-value');
    if (savedValue) {
      inputElement.checked = (savedValue === true);
    }

    // 监听复选框的改变事件，当状态改变时保存新的值到本地存储
    inputElement.addEventListener('change', function(event) {
      var newValue = event.target.checked;
      localStorage.setItem(event.target.id + '-value', newValue);
    });
  });

  // 添加事件监听器以导出数据
  var exportButton = document.getElementById('exportButton');
  exportButton.addEventListener('click', function() {
    exportToExcel();
  });

  // 添加清空按钮的点击事件处理程序
  var clearButton = document.getElementById('clearButton');
  clearButton.addEventListener('click', function() {
    clearInputs();
  });
});

// 清空复选框和本地存储的值
function clearInputs() {
  var inputElements = document.querySelectorAll('.fill-input1');
  inputElements.forEach(function(inputElement) {
    inputElement.checked = false;
    localStorage.removeItem(inputElement.id + '-value');
  });
}
// 导出数据到Excel
function exportToExcel() {
  var headers = ['', '关键词', '商品链接', '类型', '标题', '商品ID', '店铺', '收货人数', '是否保留']; // 替换成你的实际字段名
  var csvContent = "data:text/csv;charset=utf-8";

  var data = [];
  var price_data = [];

  // 获取复选框元素的值
  var inputElements = document.querySelectorAll('.fill-input1');
  inputElements.forEach(function(inputElement) {
    price_data.push(inputElement.checked);
  });

  // 获取商品行元素
  var productRows = document.body.querySelector('tbody').querySelectorAll('tr');
  productRows.forEach(function(row) {
    var rowData = [];
    // 获取<tr>中的第1到第7个<td>的值
    var tableData = row.querySelectorAll('td');
    for (var i = 0; i <= 6; i++) {
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

    # 在 HTML 的表格行中插入 input 元素，并为 input 元素添加 class属性
    html_content = html_content.replace(
        '<td></td>',
        '<td><input class="fill-input1" type="checkbox"></td>'
    )
    # 添加html尾部代码
    html_content = html_content.replace('</table>', html_tail)
    # 将处理后的 HTML 字符串保存为 HTML 文件
    with open(rf'{save_path}\搜索页\tb-{keyword}-dir.html', 'w', encoding='utf-8') as file:
        file.write(html_content)

    generate_msg = rf' html生成路径为：{save_path}\搜索页\tb-{keyword}-dir.html'
    return generate_msg, html_content


def seg_word(line):
    """ 分词算法 """
    stopwords = [line.strip() for line in open('stop_words.txt', encoding='UTF-8').readlines()]
    # seg=jieba.cut_for_search(line.strip())
    seg = jieba.cut(line.strip())
    temp = ""
    counts = {}
    wordstop = stopwords
    for word in seg:
        if word not in wordstop:
            if word != ' ':
                temp += word
                temp += '\n'
                counts[word] = counts.get(word, 0) + 1  # 统计每个词出现的次数
    # return temp  # 显示分词结果
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:100]  # 统计出现前一百最多的词及次数


def count_and_save(dir_data, save_path, keyword):
    """ 统计词频并添加到目录页数据表 """
    string = ''
    for i in dir_data['标题'].tolist():
        string += str(i)
    # 用正则筛掉“xxx g”这种无用词语
    string = re.sub("[0-9]+g", "", string)
    result = seg_word(string)
    new_result = ''
    for item in result:
        new_result += str((item[0], item[1])) + '\n'
    # result = [str((item[0], item[1]))+'\n' for item in result]
    # print(new_result)

    count_keys = [item[0] for item in result]
    count_values = [item[1] for item in result]
    count_df = pd.DataFrame({
        '': [''] * len(count_keys),
        '分词': count_keys,
        '词频': count_values,
    })

    all_data = pd.concat([dir_data, count_df], axis=1)
    all_data.to_excel(rf'{save_path}\搜索页\tb-{keyword}-dir.xlsx', index=False, sheet_name=f'{keyword}')
    msg = rf'保存路径为: {save_path}\搜索页\tb-{keyword}-dir.xlsx'
    return msg + '\n\n爬取标题词频如下:\n' + str(new_result)


if __name__ == '__main__':
    # 搜索关键词
    keyword = 'a2奶粉三段'
    # 储存数据文件夹路径
    save_path = r"C:\Users\EDY\Desktop\data\TB"
    # 添加保持登录的数据路径：安装目录一般在C:\Users\****\AppData\Local\Google\Chrome\User Data
    user_data_dir = r"C:\Users\EDY\AppData\Local\Google\Chrome\User Data"
    # 数据范围选择，0只要淘宝系的数据，1只要天猫系的数据，不填或其余元素则不筛选
    data_range = '淘宝'

    # 创建浏览器驱动
    driver, wait = dir_create_driver()
    # 登录并自动点击
    login_click(driver, wait, keyword)
    # 获取淘宝搜索页数据
    types, links, titles, stores, nums, pics, msg = get_dir_info(driver, wait, keyword)
    # 处理并划分两种类型数据
    dir_data = process_dir_data(keyword, types, links, titles, stores, nums, pics)
    # 统计所有行标题出现的词频并保存excel
    count_and_save(dir_data, save_path, keyword)
    # 关闭浏览器
    driver.close()
    # 筛选数据
    black_list = ['伊利', '飞帆', '飞鹤', '君乐宝', '美赞臣', '金领']
    if black_list:  # 如果黑名单不为空
        black_filter = dir_data['标题'].str.contains('|'.join(black_list), case=False, na=False)
        filter_data = dir_data[~black_filter]
    else:
        filter_data = dir_data.copy()
    # 生成html文件
    generate_msg, html_content = show_dir_html(data_range, filter_data, save_path, keyword)
