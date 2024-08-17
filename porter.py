import queue
import config
import database
from base import ThreadSystem, BaseThread
import utils

"""
搬运工配置
"""
# 初始搬运工数量
PORTER_NUM = 5

# 等待队列超时时间
QUEUE_TIMEOUT = 10

# 搬运间隔
INTERNAL = 1


class Porter(BaseThread):
    def __init__(self, uid, name, porterPool):
        super().__init__()
        self.uid = uid
        self.name = name
        self.porterPool = porterPool
        self.data_queue = porterPool.data_queue
        self.mongoDB = porterPool.mongoDB
        self.app = porterPool.app

    def run(self) -> None:
        while self.running.isSet():
            self.resuming.wait()
            data = self.data_queue.get()
            self.app.write(f"[{self.name}]获取值为：{data}")
            if data is None:
                self.running.clear()
                continue
            self.mongoDB.insert(data)
            self.data_queue.task_done()

            # utils.sleepMonitor(INTERNAL, self.running)

        self.porterPool.removePorter(self)


class PorterPool(ThreadSystem):
    def __init__(self, data_queue: queue.Queue = None):
        super().__init__()
        self.data_queue = data_queue
        """
        待绑定数据
        """
        self.mongoDB = None
        self.app = None

    def binding(self):
        self.mongoDB = self.systemStore.get('mongoDB')
        self.app = self.systemStore.get('app')

    def build(self):
        super().build()
        thread_list = []
        for i in range(PORTER_NUM):
            thread_list.append(Porter(
                uid=i,
                name="porter-" + str(i),
                porterPool=self
            ))

        # 赋值属性
        self.thread_list = thread_list

    def clear(self):
        super().clear()
        for _ in self.thread_list:
            self.data_queue.put(None)

    def add(self):
        """
        添加搬运工
        :return:
        """
        max_uid = max(thread.uid for thread in self.thread_list)
        self.thread_list.append(Porter(
            uid=max_uid + 1,
            name="porter-" + str(max_uid+1),
            porterPool=self
        ))

    def remove(self):
        """
        移除搬运工
        :return:
        """
        self.data_queue.put(None)

    def removePorter(self, porter):
        self.thread_list.remove(porter)
        self.app.write(f"[porterPool]已移除{porter.name}")
