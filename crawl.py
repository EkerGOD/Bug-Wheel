import threading
from threading import Thread

import utils

import logging

from database import NewMongoDB
from utils import initial_logger

class NewCrawl(Thread):
    def __init__(self, name, uid, url, actions, internal, newest_flag, logger, mongoDB):
        super().__init__()
        self.name = name
        self.uid = uid
        self.url = url
        self.actions = actions
        self.internal = internal
        self.newest_flag = newest_flag  # 初始化历史记录
        self.logger = logger
        self.mongoDB = mongoDB


    def run(self) -> None:
        try:
            self.logger.info("Running...")

            tree = utils.getTree(self.url)

            data_list = extract(tree, self.actions)
            self.logger.info(f'{len(data_list)} data items have been obtained!')

            # 爬取和判断最新分开进行，先全部爬取完成，最后判断是否重复
            data_should_be_saved = []
            for data_dict in data_list:

                if self.newest_flag != data_dict['title']:  # 当当前标题等于历史记录标题时，不再向链接池添加
                    data_should_be_saved.append(data_dict)
                else:
                    break  # 当出现相同则跳出循环，后面所有都不添加

            self.newest_flag = data_list[0]['title']  # 更新历史记录

            # 数据库写入数据
            for data_dict in data_should_be_saved:
                self.mongoDB.insert(data_dict)
        except Exception as e:
            self.logger.error(e)


def build(sites_need_to_be_crawled, historyController, log_name):
    logger = initial_logger('main.crawl.build', log_name)
    logger.info('Building crawls...')

    sites = sites_need_to_be_crawled
    history_data = historyController.get()
    thread_list = []
    for site in sites:
        uid = site['uid']
        logger.info('Now building crawl ' + str(uid) + '...')

        logger.info('Building mongoDB...')
        newMongoDB = NewMongoDB(log_name)

        if str(uid) not in history_data.keys():
            historyController.add(uid)
        thread_list.append(
            NewCrawl(
                site['name'],
                uid,
                site['url'],
                site['actions'],
                site['internal'],
                history_data[str(uid)]['newest_flag'],
                initial_logger('main.crawl.' + site['name'], log_name),
                newMongoDB
                ))

    return thread_list


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
