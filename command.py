import re
import utils
from base import System
import sys
import threading


class Command:
    def __init__(self, name, help_info, params):
        self.name = name
        self.help_info = help_info
        self.params = params

        self.commandController = None
        self.threadSystem = None
        self.app = None

    def execute(self, *args, **kwargs):
        raise NotImplementedError("Each command must implement an execute method")

    def help(self):
        help_msg = f"命令：{self.name}\n"
        help_msg += f"用法：{self.help_info}\n"
        for param in self.params:
            help_msg += f"{param['name']}：{param.get('description', '无描述')}，默认值：{param.get('default', '无默认值')}\n"
        return help_msg.strip()


class CommandController(System):
    def __init__(self):
        super().__init__()
        self.commands = {}
        self.app = None

    def binding(self):
        self.app = self.systemStore.get('app')

    def register(self, command):
        self.commands[command.name] = command
        command.commandController = self
        command.threadSystem = self.systemStore.threadSystem
        command.app = self.app

    def parse(self, command_str):
        parts = command_str.split()
        cmd_name = parts[0]
        params = parts[1:]

        if cmd_name in self.commands:
            cmd = self.commands[cmd_name]
            required_params = [param for param in cmd.params if param.get('required')]

            # 简单的参数解析，实际使用时可能需要更复杂的解析逻辑
            kwargs = {param['name']: param.get('default') for param in cmd.params}
            for param in params:
                # 这里只是一个示例，实际参数解析需要根据具体参数格式来实现
                if '=' in param:
                    key, value = param.split('=')
                else:
                    key = required_params.pop(0)['name']
                    param = utils.strConvert(param)
                    value = param
                kwargs[key] = value
            cmd.execute(**kwargs)
        else:
            self.app.write("未知命令")
            # print("未知命令")

    def show_help(self, command_str):
        if command_str in self.commands:
            self.app.write(self.commands[command_str].help())
            # print(self.commands[command_str].help())
        else:
            self.app.write("没有找到相关命令的帮助信息")
            # print("没有找到相关命令的帮助信息")


class Help(Command):
    def __init__(self):
        super().__init__(
            name="help",
            help_info="查看指令帮助",
            params=[
                {"name": "command_name", "required": True, "type": str, "default": 'help', "description": "命令名称"}
            ]
        )

    def execute(self, command_name):
        self.commandController.show_help(command_name)


class StartSystem(Command):
    def __init__(self):
        super().__init__(
            name="start",
            help_info="启动全部系统",
            params=[]
        )
        self.executed = False

    def execute(self):
        """
        启动所有动态系统
        :return:
        """
        if not self.executed:
            for system_name in self.commandController.systemStore.threadSystem:
                self.commandController.systemStore.get(system_name).start()
                self.app.write(f"[CommandController]启动{system_name}完毕！")
            self.executed = True
        else:
            self.app.write(f"[CommandController]只能启动系统一次！")


class PauseSystem(Command):
    def __init__(self):
        super().__init__(
            name="pause",
            help_info="暂停系统系统",
            params=[
                {"name": "system_name", "required": True, "type": str, "default": 'all', "description": "需要暂停的系统名称"}
            ]
        )

    def execute(self, system_name):
        """
        暂停系统线程
        :return:
        """
        threadSystem = self.commandController.systemStore.threadSystem
        app = self.commandController.systemStore.get('app')
        if system_name == 'all':
            for system_name in threadSystem:
                self.commandController.systemStore.get(system_name).pause()
        else:
            if system_name not in threadSystem:
                app.write("所暂停的系统不在动态类列表中！")
            else:
                self.commandController.systemStore.get(system_name).pause()


class ResumeSystem(Command):
    def __init__(self):
        super().__init__(
            name="resume",
            help_info="重启所有系统",
            params=[
                {"name": "system_name", "required": True, "type": str, "default": 'all', "description": "需要重启的系统名称"}
            ]
        )

    def execute(self, system_name):
        """
        暂停系统线程
        :return:
        """
        if system_name == 'all':
            for system_name in self.threadSystem:
                self.commandController.systemStore.get(system_name).resume()
                self.app.write(f"重启{system_name}完毕！")
        else:
            if system_name not in self.threadSystem:
                self.app.write("所启动的系统不在动态类列表中！")
            else:
                self.commandController.systemStore.get(system_name).resume()


class QuerySystemStatus(Command):
    def __init__(self):
        super().__init__(
            name="query",
            help_info="查询系统状态",
            params=[
                {"name": "system_name", "required": True, "type": str, "default": 'all', "description": "需要查询的系统名称"}
            ]
        )

    def execute(self, system_name):
        """
        查询系统状态
        :return:
        """
        threadSystem = self.commandController.systemStore.threadSystem
        if system_name == 'all':
            for system_name in threadSystem:
                self.commandController.systemStore.get(system_name).query()
        else:
            self.commandController.systemStore.get(system_name).query()


class ClearSystem(Command):
    def __init__(self):
        super().__init__(
            name="clear",
            help_info="注销所有系统",
            params=[]
        )

    def execute(self):
        """
        退出所有系统
        :return:
        """
        for system_name in self.threadSystem:
            self.commandController.systemStore.get(system_name).clear()


class Exit(Command):
    def __init__(self):
        super().__init__(
            name="exit",
            help_info="退出面板",
            params=[]
        )

    def execute(self):
        sys.exit()


class QueryQueue(Command):
    def __init__(self):
        super().__init__(
            name="query_queue",
            help_info="查询队列",
            params=[]
        )

    def execute(self):
        self.commandController.systemStore.get('queueController').queryQueue()


class GetActivateThread(Command):
    def __init__(self):
        super().__init__(
            name="get_activate_thread",
            help_info="获取活跃的线程",
            params=[]
        )

    def execute(self):
        # 检查线程是否在活动列表中
        for thread in threading.enumerate():
            self.app.write(f"线程ID: {thread.ident}, 线程名称: {thread.name}, 是否存活: {thread.is_alive()}")


def buildCommand(commandController: CommandController):
    # 注册命令
    commandController.register(Help())
    commandController.register(StartSystem())
    commandController.register(ResumeSystem())
    commandController.register(PauseSystem())
    commandController.register(QuerySystemStatus())
    commandController.register(ClearSystem())
    commandController.register(Exit())
    commandController.register(GetActivateThread())
    commandController.register(QueryQueue())

    return commandController
