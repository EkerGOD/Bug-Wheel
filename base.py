from threading import Thread, Event


class System:
    def __init__(self):
        self.systemStore = None

    def binding(self):
        """
        绑定数据，在SystemStore载入所有元素后会执行一次
        :return:
        """
        pass


class ThreadSystem(System):
    def __init__(self):
        super().__init__()
        self.thread_list = []

    def build(self):
        self._clearThreadList()

    def start(self):
        for thread in self.thread_list:
            thread.start()

    def pause(self):
        for thread in self.thread_list:
            thread.resuming.clear()

    def resume(self):
        for thread in self.thread_list:
            thread.resuming.set()

    def clear(self):
        for thread in self.thread_list:
            thread.running.clear()

    def _clearThreadList(self):
        if self.thread_list:
            self.clear()
            self.thread_list.clear()

    def query(self):
        result = "uid,name,status\n"
        for thread in self.thread_list:
            status = (True if thread.resuming.isSet() and thread.running.isSet() else False)
            result += f"{thread.uid},{thread.name},{status}\n"
        self.systemStore.get('app').write(result, mode="table")


class BaseThread(Thread):
    def __init__(self):
        super().__init__()
        self.uid: int
        self.name: str

        self.running = Event()
        self.running.set()
        self.resuming = Event()
        self.resuming.clear()
