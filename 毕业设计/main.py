# -*- coding = utf-8 -*-
# @Time :  2024/4/4 18:43
# @Author : 梁正
# @File : main.py
# @Software : PyCharm

import concurrent.futures
from datetime import datetime
import 新闻, 财经, 娱乐, 科技, 汽车


def execute_target(target):
    target.main()


if __name__ == '__main__':
    # 开始时间
    first_time = datetime.now()
    targets = [新闻.main(), 财经.main(), 娱乐.main(), 科技.main(), 汽车.main()]

    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
        executor.map(execute_target, targets)

    last_time = datetime.now()
    # 花费的时间
    cost_time = last_time - first_time
    print(f'全程一共花了 {cost_time.total_seconds()} 秒')
