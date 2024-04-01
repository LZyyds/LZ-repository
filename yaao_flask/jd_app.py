# -*- encoding=utf8 -*-
__author__ = "EDY"

import time
import pandas as pd
import re
from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


def jd_add_columns_by_sku(big_df, small_df):
    """ 将爬取app价格数据根据SKU添加到总表 """
    # 创建一个字典，以 sku 作为键，新的两列数据作为值
    small_dict = dict(zip(small_df['SKU'], zip(small_df['价格1'], small_df['价格2'], small_df['价格3'], small_df['发货地区'])))
    # print(small_dict)
    # big_df = big_df[(big_df['周成交单量'].isnull()) & (big_df['月成交单量'].isnull())]
    # 遍历大的DataFrame的每一行
    for index, row in big_df.iterrows():
        sku = row['SKU']
        # print(sku)
        # 如果在小的DataFrame中找到了相应的 sku
        # print(list(small_dict.keys()))
        sku_list = [str(x) for x in list(small_dict.keys())]
        if str(sku) in sku_list:
            # 将小的DataFrame中对应的两个字段的数据添加到原始的大的DataFrame中
            big_df.at[index, '价格1'] = small_dict[f'{sku}'][0]
            big_df.at[index, '价格2'] = small_dict[f'{sku}'][1]
            big_df.at[index, '价格3'] = small_dict[f'{sku}'][2]
            big_df.at[index, '发货地区'] = small_dict[f'{sku}'][3]
            # print(small_dict[f'{sku}'][0], small_dict[f'{sku}'][1], small_dict[f'{sku}'][2], small_dict[f'{sku}'][3])
        # else:
            # 如果没找到，则填充空值
            # big_df.at[index, target_time] = None
            # big_df.at[index, '月成交单量'] = None

    return big_df


def process_app_df(df):
    """ 处理数据格式 """
    df['价格1'] = df['价格1'].apply(
        lambda x: float(str(x).replace("¥", '').replace('.00', '')) if str(x).replace("¥", '').replace('.00', '').replace('.', '', 1).isdigit() else x)
    df['价格2'] = df['价格2'].apply(
        lambda x: float(str(x).replace("¥", '').replace('.00', '')) // 2 if str(x).replace("¥", '').replace('.00', '').replace('.', '', 1).isdigit() else x)
    df['价格3'] = df['价格3'].apply(
        lambda x: float(str(x).replace("¥", '').replace('.00', '')) // 3 if str(x).replace("¥", '').replace('.00', '').replace('.', '', 1).isdigit() else x)

    columns_to_fill = ['周成交单量', '月成交单量']
    value_to_fill = '/'  # 你想要替换的值
    df[columns_to_fill] = df[columns_to_fill].fillna(value_to_fill)
    df.rename(columns={'价格2': '拍2件平均价', '价格3': '拍3件平均价'}, inplace=True)
    # 转换成列表的形式
    list_of_lists = df.values.tolist()

    # 遍历列表，根据需要插入空字符串列表
    result = []
    prev_col2_value = None  # 用于存储上一行的col2的值
    x = 0
    for i, item in enumerate(list_of_lists):
        result.append(item)
        if prev_col2_value is not None and item[1] != prev_col2_value:
            result.insert(i + x, [''] * len(df.columns))  # 在需要的地方插入空行
            x += 1
        prev_col2_value = item[1]

    # 将列表转回DataFrame
    new_df = pd.DataFrame(result, columns=df.columns)
    return new_df


def jd_app_main(jd_save_path_dir, table_name):
    auto_setup(__file__)

    poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

    poco(text="京东").click()
    poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.jingdong.app.mall:id/tf").offspring("com.jingdong.app.mall:id/az_").offspring("搜索栏").child("android.widget.ImageView").wait_for_appearance(timeout=10)
    poco("android.widget.FrameLayout").offspring("android:id/content").offspring("com.jingdong.app.mall:id/tf").offspring("com.jingdong.app.mall:id/az_").offspring("搜索栏").child("android.widget.ImageView").click()

    if os.path.exists(rf"{jd_save_path_dir}\导出价格\jd-{table_name}.xlsx"):
        df = pd.read_excel(rf"{jd_save_path_dir}\导出价格\jd-{table_name}.xlsx")
    else:
        df = pd.read_excel(rf"{jd_save_path_dir}\查完销量\jd-{table_name}.xlsx")
    # store_name_list = df["店铺"].tolist()
    sku_list = df[df["价格1"].isnull()]["SKU"].tolist()

    place_list, price_list1, price_list2, price_list3 = [], [], [], []
    try:
        for sku in sku_list:
            sku = str(sku)
            poco(nameMatches="com.jd.lib.search.feature:id/a_.*").set_text(f"{sku}")
            poco(text="搜索").click()
            # 弹窗干扰
            if poco(desc="关闭").exists():
                poco(desc="关闭").click()
            # 商品无货情况
            if poco("无货").exists():
                print(f'sku:{sku}无货')
                price_list1.append("无货")
                price_list2.append("无货")
                price_list3.append("无货")
                place_list.append("无货")
                # 输入框清除上一个sku
                poco(desc="删除").click()
                continue

            # 点入商品详情页\
            time.sleep(1)
            # poco(nameMatches="com.jd.lib.search.feature:id/a7.*").wait_for_appearance(timeout=5)
            if poco(nameMatches="com.jd.lib.search.feature:id/a7.*").exists():
                poco(nameMatches="com.jd.lib.search.feature:id/a7.*").click()
                time.sleep(0.5)
                # 到货通知情况
                if poco(text="到货通知").exists():
                    price_list1.append('无货')
                    price_list2.append('无货')
                    price_list3.append('无货')
                    place_list.append("无货")
                    # 模拟返回上一级操作
                    keyevent("BACK")
                    time.sleep(0.3)
                    # 模拟返回上一级操作
                    keyevent("BACK")
                    time.sleep(0.3)
                    # 输入框清除上一个sku
                    poco(desc="删除").click()
                    continue
                poco.swipe([0.5, 0.7], [0.5, 0.4], duration=0.3)
                time.sleep(0.3)
                if poco("com.jd.lib.productdetail.feature:id/baj").child().exists():
                    place = poco("com.jd.lib.productdetail.feature:id/baj").child().get_text()
                    place = re.sub(r'.*从', '', place.split('发货')[0])
                    place = re.sub(r'现.*前', '', place)
                    if place == '':
                        place_list.append('店铺')
                    else:
                        place_list.append(place)
                    print(f'{sku}发货地:{place}')
                else:
                    place_list.append('/')

                # 点击“选择”
                poco(nameMatches="com.jd.lib.productdetail.feature:id/k.*", text="选择").click()
                # 商品不匹配
                if poco(textMatches="编号:.*").exists():
                    good_id = poco(textMatches="编号:.*").get_text().replace("编号: ", "")
                    if good_id != str(sku):
                        print(f'sku:{sku}商品不匹配')
                        price_list1.append("不匹配")
                        price_list2.append("不匹配")
                        price_list3.append("不匹配")
                        place_list[-1] = '不匹配'
                        # 模拟返回上一级操作
                        keyevent("BACK")
                        time.sleep(0.5)
                        # 模拟返回上一级操作
                        keyevent("BACK")
                        time.sleep(0.5)
                        # 输入框清除上一个sku
                        poco(desc="删除").click()
                        continue
                # 到货通知情况
                if poco(text="到货通知").exists():
                    price_list1.append('无货')
                    price_list2.append('无货')
                    price_list3.append('无货')
                    # 模拟返回上一级操作
                    keyevent("BACK")
                    time.sleep(0.3)
                    # 模拟返回上一级操作
                    keyevent("BACK")
                    time.sleep(0.3)
                    # 输入框清除上一个sku
                    poco(desc="删除").click()
                    continue
                # 进入填写订单页面
                poco(nameMatches=r"com.jd.lib.productdetail.feature:id/i\d").click()
                time.sleep(0.3)
                # 定位价格
                # price = poco("com.jd.lib.productdetail.feature:id/we").get_text()
                price1 = poco("com.jd.lib.settlement.feature:id/ke").get_text()
                print(f'{sku}价格一: {price1}')
                price_list1.append(price1)
                # 模拟返回上一级操作
                keyevent("BACK")
                time.sleep(0.3)

                # 增加一件
                time.sleep(0.2)
                poco.swipe([0.5, 0.8], [0.5, 0.4], duration=0.3)
                time.sleep(0.2)
                # poco(desc="增加数量").click()
                result = poco(desc="增加数量") or poco(descMatches=".*暂时无法操作")
                result.click()
                # 进入填写订单页面
                poco(nameMatches=r"com.jd.lib.productdetail.feature:id/i\d").click()
                time.sleep(0.3)
                if poco(text="返回上一页").exists():
                    poco(text="返回上一页").click()
                    price_list2.append('/')
                    price_list3.append('/')
                    # 模拟返回上一级操作
                    keyevent("BACK")
                    time.sleep(0.3)
                    # 模拟返回上一级操作
                    keyevent("BACK")
                    time.sleep(0.3)
                    # 输入框清除上一个sku
                    poco(desc="删除").click()
                    continue
                price2 = poco("com.jd.lib.settlement.feature:id/ke").get_text()
                if price2 != price1:
                    print(f'{sku}价格二: {price2}')
                    price_list2.append(price2)
                else:
                    price_list2.append('/')
                # 模拟返回上一级操作
                keyevent("BACK")
                time.sleep(0.3)

                # 增加两件
                result = poco(desc="增加数量") or poco(descMatches=".*暂时无法操作")
                result.click()
                # poco(desc="增加数量").click()
                # 进入填写订单页面
                poco(nameMatches=r"com.jd.lib.productdetail.feature:id/i\d").click()
                time.sleep(0.3)
                if poco(text="返回上一页").exists():
                    poco(text="返回上一页").click()
                    price_list3.append('/')
                    # 模拟返回上一级操作
                    keyevent("BACK")
                    time.sleep(0.3)
                    # 模拟返回上一级操作
                    keyevent("BACK")
                    time.sleep(0.3)
                    # 输入框清除上一个sku
                    poco(desc="删除").click()
                    continue
                price3 = poco("com.jd.lib.settlement.feature:id/ke").get_text()
                if price3 != price2:
                    print(f'{sku}价格三: {price3}')
                    price_list3.append(price3)
                else:
                    price_list3.append('/')
                # 模拟返回上一级操作
                keyevent("BACK")
                time.sleep(0.3)

                # 模拟返回上一级操作
                keyevent("BACK")
                time.sleep(0.3)
                # 模拟返回上一级操作
                keyevent("BACK")
                time.sleep(0.3)
                # 输入框清除上一个sku
                poco(desc="删除").click()
            else:
                # 输入框清除上一个sku
                poco(desc="删除").click()
                place_list.append('无法找到')
                price_list1.append('无法找到')
                price_list2.append('无法找到')
                price_list3.append('无法找到')

                continue
    except Exception as e:
        print("错误信息: " + str(e))
        common_line = min(len(sku_list), len(place_list), len(price_list1), len(price_list2), len(price_list3))
        price_df = pd.DataFrame({
            "SKU": sku_list[:common_line],
            "发货地区": place_list[:common_line],
            "价格1": price_list1[:common_line],
            "价格2": price_list2[:common_line],
            "价格3": price_list3[:common_line],
        })
        print(price_df)

        price_df['SKU'] = price_df['SKU'].apply(lambda x: str(x))
        all_data = jd_add_columns_by_sku(df, price_df)
        # 将结果保存到 Excel 文件中
        all_data.to_excel(rf'{jd_save_path_dir}\导出价格\jd-{table_name}.xlsx', index=False)
        for i in range(7):
            # 模拟返回上一级操作
            keyevent("BACK")

    for i in range(7):
        # 模拟返回上一级操作
        keyevent("BACK")

    price_df = pd.DataFrame({
        "SKU": sku_list,
        "发货地区": place_list,
        "价格1": price_list1,
        "价格2": price_list2,
        "价格3": price_list3,
    })
    print(price_df)

    price_df['SKU'] = price_df['SKU'].apply(lambda x: str(x))
    # 将app端爬取的数据写入原表
    all_data = jd_add_columns_by_sku(df, price_df)
    # 处理格式
    all_data = process_app_df(all_data)
    # 将结果保存到 Excel 文件中
    all_data.to_excel(rf'{jd_save_path_dir}\导出价格\jd-{table_name}.xlsx', index=False)