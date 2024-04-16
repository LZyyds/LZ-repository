笔记本


Git常用操作：
1、先将远程仓库clone到本地：在本地目标文件夹打开终端/在终端cd到目标文件夹，执行git clone “远程的ssh/https地址”

2、在开发工具pycharm的 ‘File’ —》‘Open’ 中打开刚克隆的项目文件

3、新建分支（‼️在本地master分支基础上新建，新建分支前update本地master同步远程master代码‼️）并切换到该分支（pycharm点点点，过程填写分支名（分支名：‘fix-xxx-xxx’），相当于 git checkout -b ‘fix-xxx-xxx’）

4、编辑修改代码

5、 在pycharm的commit视图勾选需要提交并推送到远程仓库的文件，
	填写commit message解释提交的信息（fix：修复/优化xxx逻辑；feat：新增xxx模块/功能）

6、点击commit，然后push到远程仓库（因为前面clone过已建立连接，否则需要先确定本地和远程仓库的对象，
	并且push后远程仓库自动创建对应分支，类似具有自动跟踪）
      （这里5和6介绍都是在pycharm上操作, 相当于git add.     git commit -m 和 git push，pycharm操作更直观方便）

7、在gitlab/github平台，点击Merge requests（后续简称MR）
	选择好Source branch和Target branch分别创建两个MR（填写MR title和解释具体操作内容、创建者）
	一个合并到develop分支，用于测试，自行通过合并请求，不用指定reviewer，创建过程不要勾选删除源分支选项
	一个合并到master分支，待上线，需要指定reviewer人员，待reviewer审批MR，创建过程勾选“如果通过commit即删除源分支”选项

8、在没Merge requests没成功Merge之前，可继续在本地分支修改代码并提交推送到远程对应分支即可

9、删除本地分支git branch -d/D xxx-xxx 	删除远程分支git push origin --delete xxx-xxx
￼


Mac快捷键：
- [ ] command+空格：聚焦搜索
- [ ] command+shift+g：通过路径打开目标所在文件夹
- [ ] command+shift+4/5:高级截图


1、全局代理：
Wi-Fi —》网络偏好设置 —〉高级 —》 代理 —〉网页代理/安全网络代理 —> 配置域名和端口
2、Google 网页插件（仅Google浏览器代理）：
插件商店 —》安装proxy switchyomega插件 —> 配置域名和端口 —>选择打开模式
3、python终端：
Terminal —》export http_proxy=http://px-local.sosobtc.com:xxxx —> pip install xxx

pip清华镜像源：https://pypi.tuna.tsinghua.edu.cn/simple


Scrapy：
1、cd 到目标文件夹，如pycharmproject下
2、scrapy startproject 项目名
3、cd 进入项目名文件夹，scrapy genspider 爬虫名 起始url地址

Scrapy在pycharm的调试实现：
调试设置
打开pycharm工程调试配置界面（Run -> Edit Configurations）。

1选择工程。选择调试工程 xxx_spider，官方文档提供的示例工程。
设置执行脚本（Script）。设置为 H:\Python\Python36\Lib\site-packages\scrapy\cmdline.py， cmdline.py 是 scrapy 提供的命令行调用脚本，此处将启动脚本设置为 cmdline.py，将需要调试的工程作为参数传递给此脚本。
（Mac版的 cmdline.py 路径为/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages/scrapy/cmdline.py）

2设置执行脚本参数（Script parameters）。设置为 crawl ’xxx‘，参数命令参照官方文档提供的爬虫执行命令：scrapy crawl ’xxx‘，与之不同的是设置参数时不包含 scrapy。（’xxx‘为spider的唯一name）

3设置工作目录（Work Directory）。设置为工程根目录/Users/colink/PycharmProjects/news-flash，根目录下包含爬虫配置文件 scrapy.cfg。
￼

pycharm操作mongodb：http://t.csdnimg.cn/SeJGJ
mongodb命令大全：http://t.csdnimg.cn/gWuPq

mongodb待优化：http://t.csdnimg.cn/mKZ8O
查看端口命令：  lsof -i:27017
* 进入mongodb：mongod --dbpath /usr/local/mongodb/data > 终端输入mongo
* 退出mongodb：> use admin > db.shutdownServer({force : true})



Redis安装：http://t.csdnimg.cn/dLi6C
To start redis now and restart at login:
  brew services start redis
Or, if you don't want/need a background service you can just run:
  /opt/homebrew/opt/redis/bin/redis-server /opt/homebrew/etc/redis.conf
￼

Scrapy-redis项目：http://t.csdnimg.cn/kiQAG

设计模式 https://refactoringguru.cn/design-patterns

浅拷贝（shallow copy）和深拷贝（deep copy）
在 Python 中，浅拷贝（shallow copy）和深拷贝（deep copy）是两种不同的拷贝方式，它们在处理对象的引用和嵌套对象时有所不同。
1. 浅拷贝（Shallow Copy）：
    * 浅拷贝创建一个新的对象，但是对于对象内部的引用类型（如列表、字典等），浅拷贝只会复制引用，而不会创建新的对象。
    * 也就是说，原始对象和浅拷贝对象共享相同的嵌套对象引用。
    * 对浅拷贝对象进行修改时，如果修改的是不可变对象（如数字、字符串等），则不会影响原始对象；但如果修改的是可变对象（如列表、字典等），则会影响原始对象和所有浅拷贝对象。
    * 可以使用切片操作 [:] 或者 list() 函数来创建列表的浅拷贝，使用 dict() 函数来创建字典的浅拷贝。
				shallow_copy = original_list[:]  # 或者 shallow_copy = list(original_list)

2. 深拷贝（Deep Copy）：
    * 深拷贝创建一个新的对象，并且递归地复制原始对象内部的所有嵌套对象，创建完全独立的副本。
    * 深拷贝后的对象与原始对象之间没有任何引用共享，修改深拷贝对象不会影响原始对象。
    * 可以使用 copy 模块的 deepcopy() 函数来创建对象的深拷贝。

在 Python 中，使用赋值语句 shallow_copy = original_list 实际上并不是浅拷贝，而是创建了一个对原始对象的引用。这意味着 shallow_copy 和 original_list 实际上指向同一个对象。
当你修改 shallow_copy 时，实际上是在修改 original_list，因为它们引用相同的对象。同样地，修改 original_list 也会反映在 shallow_copy 上。
修改 shallow_copy 的第一个元素不会影响 original_list，因为它们是不同的对象。但是，对于嵌套的可变对象（如列表 [2, 3]），浅拷贝仍然共享相同的引用，修改嵌套对象会影响到原始对象和浅拷贝对象。

DNS (Domain Name System) 解析
是将域名转换为 IP 地址的过程。以下是 DNS 解析的流程,分点总结:
1. 浏览器缓存查询
    * 浏览器首先检查自己的缓存中是否存在已解析过的域名对应的 IP 地址。
    * 如果缓存中有记录,直接使用缓存的 IP 地址,解析过程结束。
2. 操作系统缓存查询
    * 如果浏览器缓存中没有找到对应的 IP 地址,则查询操作系统的 DNS 缓存。
    * 操作系统维护了一个 DNS 缓存,存储最近解析过的域名和 IP 地址的映射关系。
    * 如果操作系统缓存中有记录,直接返回对应的 IP 地址,解析过程结束。
3. 本地 DNS 服务器查询
    * 如果操作系统缓存中也没有找到对应的 IP 地址,则向本地 DNS 服务器发送查询请求。
    * 本地 DNS 服务器通常由 ISP (互联网服务提供商)提供,如电信、移动、联通等。
    * 本地 DNS 服务器收到查询请求后,会先检查自己的缓存,如果有记录则直接返回 IP 地址。
4. 递归查询
    * 如果本地 DNS 服务器的缓存中没有找到对应的 IP 地址,它会向根 DNS 服务器发起递归查询。
    * 根 DNS 服务器是 DNS 查询的起点,它知道所有顶级域 (如 .com、.org 等)的权威 DNS 服务器的地址。
    * 本地 DNS 服务器向根 DNS 服务器发送查询请求,根 DNS 服务器返回负责该顶级域的权威 DNS 服务器的地址。
5. 迭代查询
    * 本地 DNS 服务器收到顶级域的权威 DNS 服务器地址后,向其发送查询请求。
    * 权威 DNS 服务器返回负责该二级域名 (如 example.com)的权威 DNS 服务器的地址。
    * 本地 DNS 服务器继续向二级域名的权威 DNS 服务器发送查询请求,获取负责该域名的权威 DNS 服务器的地址。
6. 权威 DNS 服务器查询
    * 本地 DNS 服务器向负责该域名的权威 DNS 服务器发送查询请求。
    * 权威 DNS 服务器存储了该域名的 DNS 记录,包括 IP 地址等信息。
    * 权威 DNS 服务器返回该域名对应的 IP 地址给本地 DNS 服务器。
7. 本地 DNS 服务器缓存和返回结果
    * 本地 DNS 服务器收到权威 DNS 服务器返回的 IP 地址后,将其缓存下来,并将结果返回给操作系统。
    * 操作系统将 IP 地址返回给浏览器,浏览器使用该 IP 地址与 Web 服务器建立连接。


asyncio异步编程：
基础概念：http://t.csdnimg.cn/JANQr

import asyncio

async def task1():
    print("执行 Task 1")
    await asyncio.sleep(1)
async def task2():
    print("执行 Task 2")
    await asyncio.sleep(1)
async def main():
    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(task1()), loop.create_task(task2())]
    await asyncio.wait(tasks)
	# 或者# result1, result2 = await asyncio.gather(task1(), task2())

asyncio.run(main())

在这个示例中:
1. 我们定义了两个协程函数 task1() 和 task2(),它们分别打印一条消息并使用 asyncio.sleep() 模拟等待1秒钟。
2. 在 main() 协程中,我们使用 asyncio.get_event_loop() 函数获取当前的事件循环。
3. 接下来,我们使用 loop.create_task() 方法将 task1() 和 task2() 创建为任务,并将它们添加到一个任务列表中。
4. 然后,我们使用 asyncio.wait() 函数将任务列表作为参数传递,等待所有任务完成。
5. 最后,我们使用 asyncio.run() 函数运行 main() 协程。
get_event_loop() 函数的作用是获取当前的事件循环,可以通过该事件循环来管理和执行协程任务。它允许我们对事件循环进行更细粒度的控制,例如添加回调函数、设置异常处理程序等。
现在,让我们简单说明一下 get_event_loop() 和 gather() 的区别:
* get_event_loop() 函数用于获取当前的事件循环,它返回一个事件循环对象。通过该对象,我们可以手动管理和控制协程的执行,例如使用 create_task()、run_until_complete() 等方法。
* gather() 函数是一个用于并发执行协程的工具函数。它接受多个协程作为参数,并返回一个协程,该协程会等待所有传入的协程完成。gather() 函数会自动将传入的协程提交给事件循环执行,无需手动管理事件循环。
总的来说,get_event_loop() 提供了更底层的事件循环控制,允许我们手动管理协程的执行,而 gather() 则提供了一种更高层次的抽象,用于方便地并发执行多个协程任务。在大多数情况下,使用 gather() 函数可以更简洁地编写并发代码,而 get_event_loop() 则用于需要对事件循环进行更细粒度控制的场景。


多线程ThreadPoolExecutor使用方法
progress_bar = tqdm(total=len(holder_list), desc='进度')
# 创建线程池
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {
        executor.submit(self.get_arkham_label, address): address
        for address in holder_list
    }
    # 处理任务结果
    for future in as_completed(futures):
        address = futures[future]  # 根据future获取对应的address
        arkham_entity, arkham_label = future.result()
        if arkham_entity is not None or arkham_label is not None:
            self.label_dict[address] = {}
            if arkham_entity is not None:
                self.label_dict[address]['arkham_entity'] = arkham_entity
            if arkham_label is not None:
                self.label_dict[address]['arkham_label'] = arkham_label
        # 更新进度条
        progress_bar.update(1)

异步编程(使用 asyncio)和多线程编程(使用 ThreadPoolExecutor)在并发处理任务时有一些区别
1. 编程模型:
    * 异步编程使用协程(coroutine)和事件循环(event loop)的概念。协程通过 async/await 语法来定义,通过 await 来等待异步操作完成,而事件循环负责调度和执行这些协程。
    * 多线程编程使用线程(thread)的概念。每个任务在一个单独的线程中执行,线程由操作系统调度。ThreadPoolExecutor 是一个线程池,用于管理和重用线程。
2. 并发性:
    * 异步编程通过单个线程中的协程实现并发。协程通过在等待 I/O 操作完成时让出控制权,允许其他协程执行,从而实现并发。
    * 多线程编程通过多个线程实现并发。每个线程可以并行执行,由操作系统负责调度。
3. 上下文切换:
    * 异步编程中的上下文切换发生在协程之间,由事件循环控制。当一个协程等待 I/O 操作完成时,事件循环可以切换到另一个协程执行。
    * 多线程编程中的上下文切换发生在线程之间,由操作系统内核控制。当一个线程被阻塞或时间片用完时,操作系统可以切换到另一个线程执行。
4. 资源消耗:
    * 异步编程通常比多线程编程消耗更少的资源。协程是轻量级的,创建和切换的开销较小。
    * 多线程编程中,每个线程都有自己的栈和上下文,创建和切换线程的开销较大。此外,线程之间的同步和通信也需要额外的资源。
5. 适用场景:
    * 异步编程适用于 I/O 密集型任务,如网络通信、文件读写等。当任务主要涉及等待 I/O 操作完成时,异步编程可以通过协程的切换来提高效率。
    * 多线程编程适用于 CPU 密集型任务,如复杂计算、数据处理等。当任务主要依赖 CPU 进行计算时,多线程可以通过并行执行来提高效率。
6. 编程复杂度:
    * 异步编程可能稍微更复杂一些,因为需要理解协程、事件循环和 async/await 语法。但是,Python 的 asyncio 库提供了较好的抽象和工具,使得异步编程变得更加简单。
    * 多线程编程相对更直观,但需要注意线程安全和同步问题。ThreadPoolExecutor 简化了线程池的使用,但仍需要注意线程之间的通信和协调。