from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import tkinter as tk
import pandas as pd
from 商智自动化全流程 import delete_sku, view_click, get_trade_num
import pyautogui
import psutil
import time
import os

jd_save_path_dir = r'C:\Users\EDY\Desktop\data\JD'


# 创建浏览器实例函数
def create_browser_with_debugger_address(debugger_address):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", debugger_address)
    # options.add_argument(f"--remote-debugging-port={debugger_address}")
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/120.0.0.0 Safari/537.36")
    # chrome_driver_path = r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'  # 将此路径替换为你的 Chrome 驱动的路径
    # service = Service(chrome_driver_path)
    driver = webdriver.Chrome(options=options)
    # driver.maximize_window()
    # 模拟真实浏览器，防止被检测
    with open(r'stealth.min.js') as f:
        js = f.read()
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        "source": js
    })
    # 等待参数
    wait = WebDriverWait(driver, 5)
    return driver, wait


def close_alert(driver):
    """ 关闭商智网站的随时弹窗 """
    try:
        alert = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.bd-notice-modal > div > '
                                                             'div.bd-modal-wrap.absolute-center > div > div > div > '
                                                             'span')))
        alert.click()
        time.sleep(1)
    except:
        pass


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
    root.after(2000, close_popup)
    root.mainloop()


def config_click(driver, wait):
    """ 竞品配置自动点击 """
    close_alert(driver)
    # 首页竞争按键
    comp_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#competitions > a')))
    comp_btn.click()
    close_alert(driver)
    # 左侧竞争配置按键
    config_of_comp_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#competeAnalysiss > ul > li:nth-child(6) > a')))
    config_of_comp_btn.click()
    close_alert(driver)
    # 竞品配置按键
    config_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(2)')))
    config_btn.click()
    close_alert(driver)


def automatic_logon1(account, password, driver, wait):
    """ 自动登录 """
    # 访问目标站点
    time.sleep(0.5)
    driver.get('https://sz.jd.com/szweb/sz/view/competitionAnalysis/competitionConfig.html')
    driver.refresh()
    time.sleep(1.5)
    if 'login' in driver.current_url:
        try:
            # 登录按钮
            login_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#main > div.nav-item > div.ibd-affix > div > div > div.btn-wrapper.headv > a.login-btn.btn')))
            login_btn.click()
            time.sleep(2)
            # 切换到框架的上下文
            frame = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#dialogIframe')))
            driver.switch_to.frame(frame)
            # 定位账号密码输入框
            account_input = driver.find_element(By.CSS_SELECTOR, '#loginname')
            pwd_input = driver.find_element(By.CSS_SELECTOR, '#nloginpwd')
            # 输入账号和密码
            account_input.clear()
            pwd_input.clear()
            account_input.send_keys(account)
            pwd_input.send_keys(password)
            # 模拟按下回车键
            pwd_input.send_keys(Keys.RETURN)
            show_true_popup("滑动验证码")
            time.sleep(4)
            # 切回主文档的上下文
            driver.switch_to.default_content()
            # 如没进入则等待用户操作（最多30秒）
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#top-menu > ul,'
                                                                          'body > div.bd-notice-modal > div > div.bd-modal-wrap.absolute-center > div > div > div > span')))
            # 竞品配置自动点击
            config_click(driver, wait)
        except:
            show_true_popup("登录异常，人工操作登录！！")
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#top-menu > ul,'
                                                                          'body > div.bd-notice-modal > div > div.bd-modal-wrap.absolute-center > div > div > div > span')))
            # 竞品配置自动点击
            config_click(driver, wait)
    else:
        close_alert(driver)

        # 竞品配置按键
        config_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        '.jmtd-tabs-scroll-wrapper > div > div:nth-child(2)')))
        config_btn.click()
        close_alert(driver)


def add_sku(add_data_path, driver, wait):
    """ 批量添加SKU监控 """
    print("******** 添加操作开始 ***********\n")
    console_content = ''
    # 将要监控的SKU所在的数据表
    if '.csv' in add_data_path:
        add_data = pd.read_csv(add_data_path)
    else:
        add_data = pd.read_excel(add_data_path)
    # sku_list = add_data['SKU'].tolist()
    time.sleep(1)
    # 网页目前还在监控的SKU列表
    now_sku_list = [s.get_attribute('href').split('com/')[-1].replace('.html', '') for s in
                    driver.find_elements(By.CSS_SELECTOR, '#container > div.container-right > div.jmtd-loading > div > div.card-container > div:nth-child(n) > div.jmtd-card.jmtd-card-no-shadow > div > a')]
    # 读取待监控的SKU列表
    sku_list = add_data[(add_data['周成交单量'].isnull()) & (add_data['月成交单量'].isnull())]['SKU'].tolist()
    print("%d 个SKU 待添加" % len(sku_list))
    if len(sku_list) == 0:
        return None
    # 最多读取sku数为剩余空位最大数
    sku_list = [str(num) for num in sku_list[: 100 - len(now_sku_list)]]

    # 添加失败的列表
    dis_sku_list = []
    # 循环添加SKU
    for sku in sku_list:
        flag = False    # 内循环直接跳出所有循环标签
        if sku in now_sku_list:
            print(f'编号{sku}已在监控当中')
            console_content += f'编号{sku}已在监控当中\n'
            continue
        # try:
        # sku输入框
        sku_input = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#container > div.container-right > div.container-right-modules.header-wrapper > div.header-operation > div > div:nth-child(1) > div > div > div > input')))
        # 添加按键
        add_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        '#container > div.container-right > div.container-right-modules.header-wrapper > div.header-operation > div > div:nth-child(2) > button > span')))
        # 写入sku
        sku_input.click()
        sku_input.clear()
        for digit in sku:
            sku_input.send_keys(digit)
            time.sleep(0.1)
        time.sleep(1)
        error_tip = driver.find_elements(By.CSS_SELECTOR,
                                             '#container > div.container-right > div.container-right-modules.header-wrapper > div.header-operation > p')
        time.sleep(0.5)
        if '不需监控' in error_tip[0].text:
            print(f'sku:{sku}为自家商品，添加异常')
            console_content += f'sku:{sku}为自家商品，添加异常\n'
            # 加入sku添加异常列表
            dis_sku_list.append(sku)
            comp_st_btn = driver.find_element(By.CSS_SELECTOR, '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(1)')
            comp_st_btn.click()
            time.sleep(0.5)
            config_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(2)')))
            config_btn.click()
            continue

        if '不可监控' in error_tip[0].text:
            print(f'sku:{sku}添加异常，为不可监控商品')
            console_content += f'sku:{sku}添加异常，为不可监控商品\n'
            # 加入sku添加异常列表
            dis_sku_list.append(sku)
            comp_st_btn = driver.find_element(By.CSS_SELECTOR, '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(1)')
            comp_st_btn.click()
            time.sleep(0.5)
            config_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(2)')))
            config_btn.click()
            continue

        if '抱歉' in error_tip[0].text:
            print(f'sku:{sku}添加异常，无法找到')
            console_content += f'sku:{sku}添加异常，无法找到商品\n'
            # 加入sku添加异常列表
            dis_sku_list.append(sku)
            comp_st_btn = driver.find_element(By.CSS_SELECTOR, '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(1)')
            comp_st_btn.click()
            time.sleep(0.5)
            config_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(2)')))
            config_btn.click()
            continue

        if '所属店铺没有类目数据' in error_tip[0].text:
            print(f'sku:{sku}添加异常，所属店铺没有类目数据')
            console_content += f'sku:{sku}添加异常，所属店铺没有类目数据\n'
            # 加入sku添加异常列表
            dis_sku_list.append(sku)
            comp_st_btn = driver.find_element(By.CSS_SELECTOR, '.jmtd-tabs-scroll-wrapper > div > div:nth-child(1)')
            time.sleep(0.3)
            comp_st_btn.click()
            # time.sleep(0.3)
            config_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(2)')))
            config_btn.click()
            continue

        if '没有购买的行业类目' in error_tip[0].text:
            print(f'sku:{sku}添加异常，没有购买的行业类目')
            console_content += f'sku:{sku}添加异常，没有购买的行业类目\n'
            # 加入sku添加异常列表
            dis_sku_list.append(sku)
            comp_st_btn = driver.find_element(By.CSS_SELECTOR, '.jmtd-tabs-scroll-wrapper > div > div:nth-child(1)')
            time.sleep(0.3)
            comp_st_btn.click()
            # time.sleep(0.3)
            config_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(2)')))
            config_btn.click()
            continue

        add_btn.click()
        time.sleep(1)
        # 添加按照sku按键
        # add_extra_btn_element = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(6) > div > div.jmtd-modal-wrap.jmtd-modal-absolute-center > div > div > div > div > div > div:nth-child(2)')

        time.sleep(0.5)
        add_extra_btn = driver.find_elements(By.CSS_SELECTOR, '.product-pre-select > div > div > div:nth-child(2) > div > button')
        ActionChains(driver).move_to_element(add_extra_btn[0]).perform()
        # retry_num = 0
        # while len(add_extra_btn) == 0:
        #     retry_num += 1
        #     comp_st_btn = driver.find_element(By.CSS_SELECTOR, '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(1)')
        #     time.sleep(0.5)
        #     comp_st_btn.click()
        #     time.sleep(0.5)
        #     config_btn = wait.until(
        #         EC.element_to_be_clickable((By.CSS_SELECTOR,
        #                                     '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(2)')))
        #     config_btn.click()
        #     sku_input = wait.until(
        #         EC.element_to_be_clickable((By.CSS_SELECTOR,
        #                                     '#container > div.container-right > div.container-right-modules.header-wrapper > div.header-operation > div > div:nth-child(1) > div > div > div > input')))
        #     # 添加按键
        #     add_btn = wait.until(
        #         EC.element_to_be_clickable((By.CSS_SELECTOR,
        #                                     '#container > div.container-right > div.container-right-modules.header-wrapper > div.header-operation > div > div:nth-child(2) > button > span')))
        #     for digit in sku:
        #         sku_input.send_keys(digit)
        #         time.sleep(0.05)
        #     time.sleep(0.5)
        #     add_btn.click()
        #     time.sleep(0.5)
        #     add_extra_btn = driver.find_elements(By.CSS_SELECTOR,
        #                                          'body > div:nth-child(6) > div > div.jmtd-modal-wrap.jmtd-modal-absolute-center > div > div > div > div > div > div:nth-child(2) > div > button > span')
        #     if retry_num == 4:
        #         flag = True
        #         break
        # if flag:
        #     print(f'添加sku:{sku}时出现异常')
        #     console_content += f'添加sku:{sku}时出现异常\n'
        #     dis_sku_list.append(sku)
        #     continue
        try:
            time.sleep(0.2)
            add_extra_btn[0].click()
        except:
            add_extra_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                 '.product-pre-select > div > div > div:nth-child(2) > div > button')))
            add_extra_btn.click()
        # 最终确认按键
        add_confirm_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.jmtd-modal-wrap.jmtd-modal-absolute-center > div > div > div.jmtd-modal-tips-operate-btn > div > button.jmtd-button.jmtd-button-small.jmtd-button-primary.jmtd-button-clickable'))
        )
        add_confirm_btn.click()

        # 成功添加确认按键
        add_success_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.jmtd-modal-wrap.jmtd-modal-absolute-center > div > div > div.jmtd-modal-tips-operate-btn > div > button'))
        )
        add_success_btn.click()
        time.sleep(1)

    print('添加过程-异常sku列表：', dis_sku_list)
    console_content += '添加过程-异常sku列表：\n' + str(dis_sku_list)
    # print(console_content)
    print("******** 添加操作结束 ***********\n")
    # 目前监控sku总数
    sku_count = driver.find_element(By.CSS_SELECTOR,
                                    '#container > div.container-right > div.jmtd-loading > div > div.header-wrapper > div > div:nth-child(2) > span > span:nth-child(1)')
    # 如果监控sku数为0则说明监控面板一个sku都没监控
    if sku_count.text.strip() == '0':
        return None
    return console_content


def add_columns_by_sku(big_df, small_df, target_time):
    """ 将爬取的周/月成交单量根据SKU添加到总表 """
    # 创建一个字典，以 sku 作为键，新的两列数据作为值
    small_dict = dict(zip(small_df['SKU'], zip(small_df[target_time], small_df['标题'])))
    # print(small_dict)
    # big_df = big_df[(big_df['周成交单量'].isnull()) & (big_df['月成交单量'].isnull())]
    # 遍历大的DataFrame的每一行
    for index, row in big_df.iterrows():
        sku = row['SKU']
        # print(sku)
        # 如果在小的DataFrame中找到了相应的 sku
        # print(list(small_dict.keys()))
        if str(sku) in list(small_dict.keys()):
            # 将小的DataFrame中对应的两个字段的数据添加到原始的大的DataFrame中
            big_df.at[index, target_time] = int(small_dict[f'{sku}'][0].replace(',', ''))
            # big_df.at[index, '月成交单量'] = small_dict[sku][1]
            big_df.at[index, '标题'] = small_dict[f'{sku}'][1]
        # else:
            # 如果没找到，则填充空值
            # big_df.at[index, target_time] = None
            # big_df.at[index, '月成交单量'] = None

    return big_df


# def find_process_by_port(port):
#     for conn in psutil.net_connections(kind='inet'):
#         if conn.laddr.port == port:
#             return psutil.Process(conn.pid)
#     return None
#
#
# def kill_process_by_port(port):
#     proc = find_process_by_port(port)
#     if proc:
#         print(f"找到进程 {proc.name()} 在端口 {port} 上运行，正在结束进程...")
#         proc.kill()
#     else:
#         print(f"没有找到运行在端口 {port} 上的进程")


def all_webdriver_main(jd_save_path_dir, table_name, output_name):
    if not os.path.exists(rf'{jd_save_path_dir}\已筛选完\jd-{table_name}.xlsx'):
        add_data_path = rf'{jd_save_path_dir}\导出价格\jd-{table_name}-price.xlsx'
    else:
        add_data_path = rf'{jd_save_path_dir}\已筛选完\jd-{table_name}.xlsx'
    save_data_path = rf'{jd_save_path_dir}\查完销量\jd-{output_name}.xlsx'
    price_data = pd.read_excel(add_data_path)
    if not os.path.exists(save_data_path):
        price_data.to_excel(save_data_path, index=False)
        price_data = pd.read_excel(save_data_path)

    # 店铺信息列表
    store_list = [
        {"port": 9222, "account": "EST敏诗", "password": "", "num": "1"},
        # {"port": 9223, "account": "Commercial敏诗", "password": "", "num": "2"}, # 该店目前还没订购业务
        {"port": 9224, "account": "'SmarMoney敏诗", "password": "", "num": "3"},
        {"port": 9225, "account": "SpringRain敏诗", "password": "", "num": "4"}
    ]

    # 对每个浏览器依次进行操作
    for index, store in enumerate(store_list):
        # 快捷键打开指定端口浏览器
        pyautogui.hotkey('ctrl', 'alt', f'{store["num"]}')
        time.sleep(2)
        # 不同店铺创建带有调试模式的浏览器实例
        driver, wait = create_browser_with_debugger_address(f"127.0.0.1:{store['port']}")
        # 登录账号
        automatic_logon1(store['account'], store['password'], driver, wait)
        # 批量删除所有SKU监控
        delete_sku(driver, wait)
        # 第一个商铺，读取已筛选完文件夹的空表
        if index == 0:
            # 添加SKU监控
            msg = add_sku(add_data_path, driver, wait)
        # 后面的商铺读取查完销量的表，目的为了续加
        else:
            # 添加SKU监控
            msg = add_sku(save_data_path, driver, wait)

        # 如果待监控表格需要监控的sku为0个或者监控面板为空白，则跳过后面查单步骤
        if msg is None:
            # 执行关闭浏览器的 CDP 命令
            driver.execute_cdp_cmd('Browser.close', {})
            continue
        # 竞品概况自动点击
        view_click(driver, wait)
        # 上周成交单量数据
        last_week_data = get_trade_num("/html/body/div[3]/div/div[2]/div[1]/div[2]/div/p/div/ul/li[4]", '周成交单量', driver, wait)
        # 上月成交单量数据
        last_month_data = get_trade_num("/html/body/div[3]/div/div[2]/div[1]/div[2]/div/p/div/ul/li[5]", '月成交单量', driver, wait)
        # 将爬取的周/月成交单量根据SKU添加到总表
        price_data = pd.read_excel(save_data_path)
        all_data = add_columns_by_sku(price_data, last_week_data, '周成交单量')
        all_data = add_columns_by_sku(all_data, last_month_data, '月成交单量')
        # 将结果保存到 Excel 文件中
        all_data.to_excel(save_data_path, index=False)
        # 执行关闭浏览器的 CDP 命令
        driver.execute_cdp_cmd('Browser.close', {})

