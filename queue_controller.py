import queue
import threading
import utils
import config

from base import ThreadSystem, BaseThread

"""
队列控制器配置
"""
# 创建线程数
THREAD_NUM = 1
# 队列控制器检测间隔
MONITOR_INTERNAL = 10


class QueueOperator(BaseThread):
    def __init__(self, uid, name, data_queue: queue.Queue, porterPool, app):
        super().__init__()
        self.uid = uid
        self.name = name
        self.data_queue = data_queue
        self.porterPool = porterPool
        self.app = app

    def run(self) -> None:
        while self.running.isSet():
            self.resuming.wait()
            if self.data_queue.qsize() > 100:
                self.app.write(f"[{self.name}]增加搬运工数量，当前搬运工数量：{len(self.porterPool.thread_list)}")
                self.porterPool.add()
            elif self.data_queue.qsize() < 25 and len(self.porterPool.thread_list) > 1:
                self.app.write(f"[{self.name}]减少搬运工数量，当前搬运工数量：{len(self.porterPool.thread_list)}")
                self.porterPool.remove()

            utils.sleepMonitor(MONITOR_INTERNAL, self.running)
            # time.sleep(config.MONITOR_INTERNAL)


class QueueController(ThreadSystem):
    def __init__(self, data_queue: queue.Queue):
        super().__init__()
        self.data_queue = data_queue
        self.porterPool = None

    def binding(self):
        self.porterPool = self.systemStore.get('porterPool')

    def build(self):
        """
        初始化完之后，执行改命令构建线程
        :return:
        """
        # 如果存在已构建的内容，则退出线程，重新构建
        super().build()
        for i in range(THREAD_NUM):
            self.thread_list.append(QueueOperator(
                i,
                "queueOperator-" + str(i),
                self.data_queue,
                self.porterPool,
                self.systemStore.get('app')
            ))

    def queryQueue(self):
        self.systemStore.get('app').write(f"[queueController]当前队列剩余：{self.data_queue.qsize()}")
