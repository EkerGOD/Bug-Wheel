import traceback

import crawl
from file import HistoryController, SiteController
import config

import logging
import time

from utils import initial_logger


def start_crawl():
    # 初始化日志系统
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    log_name = 'log/' + now + '.log'
    logger = initial_logger('main', log_name, root_logger=True)

    # 启动爬虫
    logger.info('Crawl starting...')

    # 获取站点数据
    logger.info('Getting site...')
    siteController = SiteController(config.SITE_PATH)
    logger.info('Get ' + str(len(siteController.get()["sites"])) + ' sites')

    # 获取历史数据
    logger.info('Getting history...')
    historyController = HistoryController(config.HISTORY_PATH)
    logger.info('Get ' + str(len(historyController.get())) + ' history(The extra one is the template.)')

    # 检查需要爬取的站点
    logger.info('Check the sites that need to be crawled...')
    sites_need_to_be_crawled = []
    for site in siteController.get()['sites']:
        logger.info('Checking ' + site['name'] + '...')
        # 获取站点配置爬取间隔
        internal = site['internal']
        # 获取上次爬取时间字符串
        # logger.debug(historyController.get())
        # logger.debug(site['uid'])
        latest_crawl_time = historyController.get()[str(site['uid'])]['latest_crawl_time']
        # 从时间字符串提取时间戳
        latest_crawl_timestamp = time.mktime(time.strptime(latest_crawl_time, "%Y-%m-%d-%H_%M_%S"))
        # 获取当前时间戳
        now_timestamp = time.time()

        # 计算实际间隔
        actual_internal = now_timestamp - latest_crawl_timestamp

        # 当实际间隔大于配置间隔，将站点放入待爬取列表
        if actual_internal >= internal:
            logger.info('This site is added to the list.')
            sites_need_to_be_crawled.append(site)
    logger.info('Get ' + str(len(sites_need_to_be_crawled)) + ' sites that need to be crawled')

    thread_list = crawl.build(sites_need_to_be_crawled, historyController, log_name)

    for thread in thread_list:
        thread.start()

    # 等待全部线程执行完毕
    for thread in thread_list:
        thread.join()

    logger.info('Crawl completed!')
