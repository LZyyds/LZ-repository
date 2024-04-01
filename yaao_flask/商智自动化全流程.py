# -*- coding = utf-8 -*-
# @Time :  2023/12/21 10:31
# @Author : 梁正
# @File : 商智自动化全流程.py
# @Software : PyCharm
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from datetime import datetime, date
import tkinter as tk
import pandas as pd
import time


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


def close_alert(driver):
    """ 关闭商智网站的随时弹窗 """
    try:
        alert = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.bd-notice-modal > div > div.bd-modal-wrap.absolute-center > div > div > div > span')))
        alert.click()
        time.sleep(1)
    except:
        pass


def create_driver():
    """ 创建chrome driver """
    # chrome浏览器设置选项
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # 配置参数
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument("--disable-blink-features")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/120.0.0.0 Safari/537.36")
    # 浏览器驱动
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    # 模拟真实浏览器，防止被检测
    with open(r'stealth.min.js') as f:
        js = f.read()
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        "source": js
    })
    # 隐式等待参数
    wait = WebDriverWait(driver, 5)

    return driver, wait


def automatic_logon(account, password, driver, wait):
    """ 自动登录 """
    # 访问目标站点
    driver.get('https://sz.jd.com/sz/view/competitionAnalysis/competePros.html')
    time.sleep(2)
    try:
        # 登录按钮
        login_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#main > div.nav-item > div.ibd-affix > div > div > div.btn-wrapper.headv > a.login-btn.btn')))
        login_btn.click()
        time.sleep(1)
        # 切换到框架的上下文
        frame = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#dialogIframe')))
        driver.switch_to.frame(frame)
        # 定位账号密码输入框
        account_input = driver.find_element(By.CSS_SELECTOR, '#loginname')
        pwd_input = driver.find_element(By.CSS_SELECTOR, '#nloginpwd')
        # 输入账号和密码
        account_input.send_keys(account)
        pwd_input.send_keys(password)
        # 模拟按下回车键
        pwd_input.send_keys(Keys.RETURN)
        time.sleep(2)
        # 切回主文档的上下文
        driver.switch_to.default_content()
        # 如没进入则等待用户操作（最多30秒）
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#top-menu > ul,'
                                                                      'body > div.bd-notice-modal > div > div.bd-modal-wrap.absolute-center > div > div > div > span')))
    except:
        show_true_popup("登录异常，人工操作登录！！")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#top-menu > ul,'
                                                                      'body > div.bd-notice-modal > div > div.bd-modal-wrap.absolute-center > div > div > div > span')))


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


def delete_sku(driver, wait):
    """ 批量删除所有SKU监控 """
    print("******** 删除操作开始 ***********\n")
    first_index_not_today = -1  # -1为条件判断标签
    # 目前监控sku总数
    sku_count = driver.find_element(By.CSS_SELECTOR,
                                    '#container > div.container-right > div.jmtd-loading > div > div.header-wrapper > div > div:nth-child(2) > span > span:nth-child(1)')
    # 监控sku总数不为零
    if sku_count.text.strip() != '0':
        # 所有商品的添加时间列表
        add_time_list = driver.find_elements(By.CSS_SELECTOR,
                                             '#container > div.container-right > div.jmtd-loading > div > div.card-container > div:nth-child(n) > div.jmtd-card.jmtd-card-no-shadow > div > span.jmtd-typography-color-placeholder')
        # 格式转换
        processed_times = []
        for add_time in add_time_list:
            time_obj = datetime.strptime(add_time.text.strip().split(' ')[0], "%Y-%m-%d").date()
            processed_times.append(time_obj)

        # 找到第一个非今日的sku位置
        today = date.today()
        for i, processed_time in enumerate(processed_times):
            if processed_time != today:
                first_index_not_today = i + 1
                break

    error_num = 0
    # 循环批量删除sku
    for i in range(1, 101, 1):
        sku_count = driver.find_element(By.CSS_SELECTOR,
                                        '#container > div.container-right > div.jmtd-loading > div > div.header-wrapper > div > div:nth-child(2) > span > span:nth-child(1)')
        # 如果监控sku数为0则直接跳出循环
        if sku_count.text.strip() == '0':
            all_del_msg = "监控商品已全部删除完毕！目前监控0个"
            print(all_del_msg)
            show_true_popup(all_del_msg)
            break
        # 如果监控的sku全为今日添加直接跳出循环
        if first_index_not_today == -1:
            add_limit_msg = "SKU全为今日添加，删不了一点！"
            print(add_limit_msg)
            show_true_popup(add_limit_msg)
            break
        # 如果
        # 定位要悬停的元素（为了触发删除按钮显示）
        element_to_hover_over = driver.find_elements(By.CSS_SELECTOR, f"#container > div.container-right > div.jmtd-loading > div > div.card-container > div:nth-child({first_index_not_today}) > div.jmtd-card.jmtd-card-no-shadow > div > a")
        if len(element_to_hover_over) == 0:
            some_del_msg = "[非今日]添加的sku都已删除完毕！"
            print(some_del_msg)
            show_true_popup(some_del_msg)
            break
        try:
            # 使用ActionChains模拟鼠标悬停操作
            element_to_hover_over = driver.find_element(By.CSS_SELECTOR, f"#container > div.container-right > div.jmtd-loading > div > div.card-container > div:nth-last-child(1) > div.jmtd-card.jmtd-card-no-shadow > div")
            ActionChains(driver).move_to_element(element_to_hover_over).perform()
            time.sleep(0.6)
            # 删除按键
            del_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.card-container > div:nth-last-child(1) > div.del-button')))
            # del_btn = driver.find_element(By.CSS_SELECTOR, '.card-container > div:nth-last-child(1) > div.del-button')
            # ActionChains(driver).move_to_element(del_btn).perform()
            ActionChains(driver).move_to_element_with_offset(del_btn, 1, 1).move_to_element_with_offset(del_btn, -1, -1).click().perform()

            time.sleep(0.5)
            # 删除后的确认按键
            del_confirm_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.jmtd-modal-wrap.jmtd-modal-absolute-center > div > div > div.jmtd-modal-confirm-down > div > div > button.jmtd-button.jmtd-button-small.jmtd-button-primary.jmtd-button-clickable')))
            del_confirm_btn.click()
            time.sleep(0.8)
            # 防止操作过快，缓冲
            if i // 20 == 0:
                time.sleep(3)

        except Exception as e:
            # 未知异常处理
            error_num += 1
            if error_num == 5:
                del_break_msg = "未知异常第五次，强制退出删除操作"
                print(del_break_msg)
                show_true_popup(del_break_msg)
                break
            else:
                unknown_error_msg = f"删除第{i}次失败，未知错误"
                print(f"未知异常第{error_num}次,具体错误信息：{str(e)}")
                show_true_popup(unknown_error_msg)
                config_of_comp_btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#competeAnalysiss > ul > li:nth-child(6) > a')))
                config_of_comp_btn.click()
                time.sleep(1)
                config_btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(2)')))
                config_btn.click()
                # first_index_not_today += 1
                time.sleep(1)
                continue
    print("******** 删除操作结束 ***********\n")
    time.sleep(1)


def add_sku(add_data_path, driver, wait):
    """ 批量添加SKU监控 """
    print("******** 添加操作开始 ***********\n")
    console_content = ''
    # 将要监控的SKU所在的数据表
    if '.csv' in add_data_path:
        add_data = pd.read_csv(add_data_path)
    else:
        add_data = pd.read_excel(add_data_path)
    sku_list = add_data[(add_data['周成交单量'].isnull()) & (add_data['月成交单量'].isnull())]['SKU'].tolist()

    # sku_list = [str(num) for num in sku_list]
    # 目前还在监控的SKU列表
    now_sku_list = [s.get_attribute('href').split('com/')[-1].replace('.html', '') for s in
                    driver.find_elements(By.CSS_SELECTOR, '#container > div.container-right > div.jmtd-loading > div > div.card-container > div:nth-child(n) > div.jmtd-card.jmtd-card-no-shadow > div > a')]
    # print(now_sku_list)
    # print(sku_list)
    # 最多读取sku数为剩余空位最大数
    sku_list = [str(num) for num in sku_list[: 100 - len(now_sku_list)]]
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
            comp_st_btn = driver.find_element(By.CSS_SELECTOR, '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(1)')
            comp_st_btn.click()
            time.sleep(0.5)
            config_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(2)')))
            config_btn.click()
            continue

        add_btn.click()
        time.sleep(1)
        # 添加按照sku按键
        add_extra_btn = driver.find_elements(By.CSS_SELECTOR, 'body > div:nth-child(6) > div > div.jmtd-modal-wrap.jmtd-modal-absolute-center > div > div > div > div > div > div:nth-child(2) > div > button')
        retry_num = 0
        while len(add_extra_btn) == 0:
            retry_num += 1
            comp_st_btn = driver.find_element(By.CSS_SELECTOR, '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(1)')
            time.sleep(0.5)
            comp_st_btn.click()
            time.sleep(0.5)
            config_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            '#container > div.container-right > div.container-right-modules.header-wrapper > div.jmtd-tabs.jmtd-tabs-small.jmtd-line-tabs.jmtd-tabs-scroll-disable-start.jmtd-tabs-scroll-disable-end.jmtd-tabs-initialed > div.jmtd-tabs-scroll-wrapper > div > div:nth-child(2)')))
            config_btn.click()
            sku_input = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            '#container > div.container-right > div.container-right-modules.header-wrapper > div.header-operation > div > div:nth-child(1) > div > div > div > input')))
            # 添加按键
            add_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            '#container > div.container-right > div.container-right-modules.header-wrapper > div.header-operation > div > div:nth-child(2) > button > span')))
            for digit in sku:
                sku_input.send_keys(digit)
                time.sleep(0.1)
            time.sleep(0.5)
            add_btn.click()
            time.sleep(0.5)
            add_extra_btn = driver.find_elements(By.CSS_SELECTOR,
                                                 'body > div:nth-child(6) > div > div.jmtd-modal-wrap.jmtd-modal-absolute-center > div > div > div > div > div > div:nth-child(2) > div > button')
            if retry_num == 4:
                flag = True
                break
        if flag:
            print(f'添加sku:{sku}时出现异常')
            console_content += f'添加sku:{sku}时出现异常\n'
            dis_sku_list.append(sku)
            continue
        try:
            add_extra_btn[0].click()
        except:
            add_extra_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                 'body > div:nth-child(6) > div > div.jmtd-modal-wrap.jmtd-modal-absolute-center > div > div > div > div > div > div:nth-child(2) > div > button')))
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
    console_content += '添加过程-异常sku列表：\n'+str(dis_sku_list)
    # print(console_content)
    print("******** 添加操作结束 ***********\n")
    return console_content


def view_click(driver, wait):
    """ 竞品概况点击自动化 """
    print("******** 查单操作开始 ***********\n")
    time.sleep(1)
    # 左侧竞争概况按键
    view_of_comp_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#competeAnalysiss > ul > li:nth-child(3) > a')))
    view_of_comp_btn.click()
    close_alert(driver)
    driver.refresh()
    time.sleep(1)
    # SKU按键
    sku_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#container > div > div.content-header.container-right-modules.clearfix > div.common-switch-container > span > span:nth-child(2)')))
    sku_btn.click()
    close_alert(driver)
    # # 悬停元素
    # element_to_hover_over = driver.find_element(By.CSS_SELECTOR,
    #                                             ".grace-grid-pagination > div:nth-child(2) > div > div:nth-child(3) > span > span")
    # # 使用ActionChains模拟鼠标悬停操作
    # ActionChains(driver).move_to_element(element_to_hover_over).perform()
    # 选择单页容量按键
    page_size_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.grace-grid-pagination > div:nth-child(2) > div > div:nth-child(3)')))
    page_size_btn.click()
    # 选择展示数量（100条）
    target_size_btn = driver.find_elements(By.CSS_SELECTOR, 'body > ul > li:nth-child(4)')
    # 有时候找不到 target_size_btn 增加几次容错
    for i in range(3):
        if len(target_size_btn) > 0:
            target_size_btn[0].click()
            break
        else:
            page_size_btn.click()
            target_size_btn = driver.find_elements(By.CSS_SELECTOR, 'body > ul > li:nth-child(4)')


def get_trade_num(xpath, target_time, driver, wait):
    """ 获取成交单数信息 """
    num_list = []
    link_list = []
    title_list = []
    sku_id_list = []
    close_alert(driver)
    # 定位要悬停的元素（为了让下一个元素出现）
    if target_time == '周成交单量':
        element_to_hover_over = driver.find_element(By.CSS_SELECTOR, "#container > div > div.content-header.container-right-modules.clearfix > div.clearfix.mg-b20 > div.fr.datetool > div > p > input")
        # 使用ActionChains模拟鼠标悬停操作
        ActionChains(driver).move_to_element(element_to_hover_over).perform()
        # 第二处需要悬停的元素
        try:
            element_to_hover_over2 = driver.find_element(By.CSS_SELECTOR,
                                                         ".quick-type-list > li:nth-child(4)")
            ActionChains(driver).move_to_element(element_to_hover_over2).click().perform()
        except:
            element_to_hover_over2 = driver.find_element(By.CSS_SELECTOR, ".quick-type-list > li:nth-child(4)")
            ActionChains(driver).move_to_element(element_to_hover_over2).click().perform()
    else:
        # 第二处需要悬停的元素
        try:
            element_to_hover_over2 = driver.find_element(By.CSS_SELECTOR, ".quick-type-list > li:nth-child(5)")
            ActionChains(driver).move_to_element(element_to_hover_over2).click().perform()
        except:
            element_to_hover_over2 = driver.find_element(By.CSS_SELECTOR, ".quick-type-list > li:nth-child(5)")
            ActionChains(driver).move_to_element(element_to_hover_over2).click().perform()
    # 目标时间粒度按键
    target_time_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.quick-date-dashbord > div > div > span')))
    target_time_btn.click()
    time.sleep(2)
    # SKU编号列表和标题名称
    for s in driver.find_elements(By.CSS_SELECTOR, '.text-align-left > div > span > span > p > span:nth-child(1) > a'):
        link = s.get_attribute('href')
        link_list.append(link)
        # 数据切割得到SKU编号
        sku_id_list.append(link.split('com/')[-1].replace('.html', ''))
        title_list.append(s.get_attribute('title') if s.get_attribute('title') else '')
    # 成交单量
    for n in driver.find_elements(By.CSS_SELECTOR, '.text-align-right > div > span'):
        num_list.append(n.text.strip() if n else '')
    finish_num_list = num_list[4::4]

    # 将结果添加到 DataFrame 中
    all_data = pd.DataFrame({
        '商品链接': link_list,
        '标题': title_list,
        'SKU': sku_id_list,
        f'{target_time}': finish_num_list,
    })
    time.sleep(1)

    return all_data


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


if __name__ == '__main__':
    # 创建浏览器驱动和等待参数
    driver, wait = create_driver()
    # 自动登录（选择不同店铺需改账号密码）
    account = ''
    password = ''
    automatic_logon(account, password, driver, wait)
    # 需要添加监控SKU的excel表（更改文件路径）
    add_data_path = r'D:\WeChat\File\WeChat Files\wxid_zu92okxcv8e122\FileStorage\File\2024-01\2024_1_17 17_48_33.csv'
    # 查到填完价格后的数据表，需要有['周成交单量','月成交单量']字段
    price_data = pd.read_csv(add_data_path)

    # 竞品配置自动点击
    config_click(driver, wait)
    # 批量删除所有SKU监控
    delete_sku(driver, wait)
    # 批量添加所有SKU监控
    msg = add_sku(add_data_path, driver, wait)
    # 竞品概况自动点击
    view_click(driver, wait)
    # 上周成交单量数据
    last_week_data = get_trade_num("/html/body/div[3]/div/div[2]/div[1]/div[2]/div/p/div/ul/li[4]", '周成交单量', driver, wait)
    # 上月成交单量数据
    last_month_data = get_trade_num("/html/body/div[3]/div/div[2]/div[1]/div[2]/div/p/div/ul/li[5]", '月成交单量', driver, wait)
    # 关闭浏览器
    driver.close()
    # 合并两种时间粒度的数据表（按照 SKU 进行合并）
    merged_data = pd.merge(last_week_data, last_month_data, on='SKU', how='inner')
    # print(merged_data)
    # merged_data.to_excel(rf'C:\Users\EDY\Desktop\data\JD\merged_test.xlsx', index=False)
    # 本次操作商智爬取到的成交单量暂存为sale_data
    sale_data = pd.DataFrame({
        '标题': merged_data['标题_x'],
        'SKU': merged_data['SKU'],
        '周成交单量': merged_data['周成交单量'],
        '月成交单量': merged_data['月成交单量']
    })
    sale_data.to_excel(rf'C:\Users\EDY\Desktop\data\JD\sale_data.xlsx', index=False)
    sale_data = pd.read_excel(rf'C:\Users\EDY\Desktop\data\JD\sale_data.xlsx')
    # 将爬取的周/月成交单量根据SKU添加到总表
    all_data = add_columns_by_sku(price_data, sale_data)
    # 将结果保存到 Excel 文件中
    all_data.to_excel(rf'C:\Users\EDY\Desktop\data\JD\jd_all_data_test.xlsx', index=False)
    print("******** 所有操作完毕 ***********\n")
    show_true_popup("操作完毕！")
