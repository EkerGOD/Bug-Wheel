from file import HistoryController, SiteController
from crawl import CrawlPool
from porter import PorterPool
import queue
from database import MongoDB
from queue_controller import QueueController
from ui import Application
from command import CommandController, buildCommand
import config


def initialize():
    # 构建窗口UI
    app = Application()

    # 构建历史记录文件管理器
    historyController = HistoryController(config.HISTORY_PATH)
    # 构建站点数据文件管理器
    siteController = SiteController(config.SITE_PATH)

    # 构建数据队列
    data_queue = queue.Queue()

    # 构建数据库
    mongoDB = MongoDB()

    # 初始化搬运工
    porterPool = PorterPool(data_queue)

    # 初始化队列控制器
    queueController = QueueController(data_queue)

    # 构建爬虫池
    crawlPool = CrawlPool(data_queue)

    # 初始化命令控制器
    commandController = CommandController()

    # 仓库存储列表
    systemDict = {
        'historyController': historyController,
        'siteController': siteController,
        'mongoDB': mongoDB,
        'porterPool': porterPool,
        'queueController': queueController,
        'crawlPool': crawlPool,
        'commandController': commandController,
        'app': app
    }
    """
    定义动态类
    动态类可以被暂停启动，查询状态
    """
    threadSystem = [
        "porterPool",
        "queueController",
        "crawlPool"
    ]
    # 构建系统仓库
    systemStore = SystemStore(systemDict, threadSystem)

    # 给所有系统共享系统仓库
    for key, value in systemDict.items():
        value.systemStore = systemStore
        value.binding()  # 触发每一个系统绑定函数
    """
    所有需要用到系统仓库的都放在绑定后使用
    !!!需要绑定的内容!!!
    """
    # 构建爬虫池
    crawlPool.build()
    # 构建搬运工
    porterPool.build()
    # 构建命令控制器
    buildCommand(commandController)
    # 构建队列控制器
    queueController.build()
    # return crawlPool

    return systemStore


class SystemStore:
    def __init__(self, systemDict, threadSystem):
        self.systemDict = systemDict
        self.threadSystem = threadSystem

    def get(self, name=None):
        if name is None:
            return self.systemDict
        else:
            if name not in self.systemDict:
                print("访问的系统不存在！")
            return self.systemDict[name]


if __name__ == '__main__':
    newSystemStore = initialize()
    print(newSystemStore.get())
    print(newSystemStore.get('historyController').systemStore)
