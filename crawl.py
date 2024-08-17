import threading

import utils
from base import ThreadSystem, BaseThread


class Crawl(BaseThread):
    def __init__(self, name, uid, url, actions, internal, newest_flag, app, data_queue):
        super().__init__()
        self.name = name
        self.uid = uid
        self.url = url
        self.actions = actions
        self.internal = internal

        self.newest_flag = newest_flag  # 初始化历史记录

        self.app = app
        self.data_queue = data_queue

        # self.app.write(f"[{self.name}]初始化{self.name}完成")
        # print("初始化" + self.name + "完成")

    def run(self) -> None:
        while self.running.isSet():
            self.resuming.wait()
            self.app.write(f"[{self.name}]正在运行...")

            tree = utils.getTree(self.url)

            data_list = extract(tree, self.actions)
            self.app.write(f"[{self.name}]已获取数据{len(data_list)}条")

            # 爬取和判断最新分开进行，先全部爬取完成，最后判断是否重复
            for data_dict in data_list:

                if self.newest_flag != data_dict['title']:  # 当当前标题等于历史记录标题时，不再向链接池添加
                    self.data_queue.put(data_dict)
                else:
                    break  # 当出现相同则跳出循环，后面所有都不添加

            self.newest_flag = data_list[0]['title']  # 更新历史记录

            # url_pool = []
            # for action in self.actions:
            #     # print(action['name'])
            #     if action['name'] == "list":
            #         ul = tree.xpath(action['ul_xpath'])[0]
            #         li = ul.xpath("li")
            #
            #         index = 1
            #         change_newest_flag = self.newest_flag  # 初始化更改记录
            #         for each in li:
            #
            #             url = each.xpath('.//a' + "/@href")
            #             title = each.xpath('.//a' + "/text()")
            #             if url:
            #                 title = title[0]
            #                 if self.newest_flag != title:
            #                     if index == 1:
            #                         change_newest_flag = title
            #                     url_pool.append(url[0])
            #                 else:  # 当当前标题等于历史记录标题时，不再向链接池添加
            #                     break
            #
            #             index += 1
            #         self.newest_flag = change_newest_flag  # 更新历史记录
            #         # print(self.newest_flag)
            #         # print("已获取新链接" + str(len(url_pool)))
            #     if action['name'] == "extract":
            #         if not url_pool:
            #             self.app.write(f"[{self.name}]未发现新数据")
            #         else:
            #             extract_data_list = []
            #             for url in url_pool:
            #                 extract_data_dict = {}
            #                 branch_tree = utils.getTree(url)
            #                 # 执行提取操作的各项数据
            #                 for extract_item in action['extract_list']:
            #                     extract_data = branch_tree.xpath('string(' + extract_item['xpath'] + ')')
            #                     if extract_data:
            #                         cleaned_extract_data = utils.cleanText(extract_data)
            #                         extract_data_dict[extract_item['name']] = cleaned_extract_data
            #                 self.data_queue.put(extract_data_dict)
            #                 extract_data_list.append(extract_data_dict)
            #             # print("已获取数据" + str(len(extract_data_list)) + "条")
            #             self.app.write(f"[{self.name}]已获取数据{len(url_pool)}条")
            # print(extract_data_dict)
            # print("Task Complete!")

            # 间隔多久执行
            # 将间隔分成一秒一秒执行，每一秒监听是否退出，如果退出直接跳出休眠
            utils.sleepMonitor(self.internal, self.running)


class CrawlPool(ThreadSystem):
    def __init__(self, data_queue):
        super().__init__()
        """
        待绑定数据
        """
        self.data_queue = data_queue
        self.historyController = None
        # 格式化后的爬虫数据
        self.crawl_dict = {}

    def binding(self):
        self.historyController = self.systemStore.get('historyController')

    def build(self):
        super().build()
        site_data = self.systemStore.get('siteController').get()
        history_data = self.systemStore.get('historyController').get()
        sites = site_data['sites']
        thread_list = []
        for site in sites:
            uid = site['uid']
            if str(uid) not in history_data.keys():
                self.historyController.add(uid)
            thread_list.append(
                Crawl(site['name'],
                      uid,
                      site['url'],
                      site['actions'],
                      site['internal'],
                      history_data[str(uid)]['newest_flag'],
                      self.systemStore.get('app'),
                      data_queue=self.data_queue
                      ))
        self.thread_list = thread_list
        self.formatRawData()

    # 将原本的数组类型转化为字典类型，便于通过uid访问
    def formatRawData(self):
        for crawl in self.thread_list:
            uid = crawl.uid
            self.crawl_dict[uid] = crawl

    def clear(self, name=None, uid=None):
        if name is None and uid is None:
            for crawl in self.thread_list:
                crawl.running.clear()

                self.historyController.update(crawl.uid, {'newest_flag': crawl.newest_flag})
        elif uid is not None:
            self.crawl_dict[uid].running.clear()

            self.historyController.update(uid, {'newest_flag': self.crawl_dict[uid].newest_flag})
        else:
            for crawl in self.thread_list:
                if crawl.getName() == name:
                    crawl.running.clear()

                    self.historyController.update(crawl.uid, {'newest_flag': crawl.newest_flag})

        self.historyController.save()

    # # 暂停爬虫
    # def pause(self, name=None, uid=None):
    #     if name is None and uid is None:
    #         for crawl in self.thread_list:
    #             crawl.resuming.clear()
    #     elif uid is not None:
    #         self.crawl_dict[uid].resuming.clear()
    #     else:
    #         for crawl in self.thread_list:
    #             if crawl.getName() == name:
    #                 crawl.resuming.clear()
    #
    # # 恢复爬虫
    # def resume(self, name=None, uid=None):
    #     if name is None and uid is None:
    #         for crawl in self.thread_list:
    #             crawl.resuming.set()
    #     elif uid is not None:
    #         self.crawl_dict[uid].resuming.set()
    #     else:
    #         for crawl in self.thread_list:
    #             if crawl.getName() == name:
    #                 crawl.resuming.set()


def extract(etree, actions):
    data = {}
    data_list = []
    is_branch = False
    for action in actions:
        if action['type'] == 'text':
            if etree.xpath(action['xpath'] + "/text()"):
                data[action['name']] = utils.cleanText(etree.xpath(action['xpath'] + "/text()")[0])
        elif action['type'] == 'all_text':
            if etree.xpath(f"string({action['xpath']})"):
                data[action['name']] = utils.cleanText(etree.xpath(f"string({action['xpath']})"))
        elif action['type'] == 'href':
            if etree.xpath(action['xpath'] + "/@href"):
                data[action['name']] = utils.cleanText(etree.xpath(action['xpath'] + "/@href")[0])
        elif action['type'] == 'jump':
            if etree.xpath(action['xpath'] + "/@href"):
                new_etree = utils.getTree(etree.xpath(action['xpath'] + "/@href")[0])
                data = extract(new_etree, action['next'])
        else:
            is_branch = True
            etree_list = etree.xpath(action['xpath'])
            for new_etree in etree_list:
                if len(etree_list) != 1:
                    if extract(new_etree, action['next']):
                        data_list.append(extract(new_etree, action['next']))
                else:
                    data_list = extract(new_etree, action['next'])

    if is_branch:
        return data_list
    else:
        return data
