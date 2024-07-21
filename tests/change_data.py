import curses
import time, threading
from curses import wrapper
from curses.textpad import Textbox

lines = []


def viewstrings(lines, win):  # 显示区域更新函数，行数超过区域限高报错，所以需要截取，循环调用的话可以实现向上滚动效果（但不支持向上翻页
    if len(lines) < curses.LINES - 2:
        win.clear()
        for i in range(len(lines)):
            win.addstr(i, 0, lines[i])
            win.refresh()
            # stdscr.getkey()
    elif len(lines) >= curses.LINES - 2:
        win.clear()
        lines = lines[len(lines) - (curses.LINES - 2):len(lines)]
        for i in range(len(lines)):
            win.addstr(i, 0, lines[i])
            win.refresh()


class run():
    def __init__(self):
        self._flag = False  # 退出标记

    def run(self, msg, win):  # 后台更新显示区域逻辑，为了测试效果这里使用死循环每1s添加一行字符，可以自行编写逻辑
        n = 0
        while True:
            if self._flag:
                break
            n += 1
            lines.append(msg + "->" + str(n))
            t = threading.Thread(target=viewstrings, args=(lines, win,))  # 使用线程去更新一次显示区域
            t.start()
            t.join()
            time.sleep(1)
        print("roll线程退出")

    def terminates(self):  # 退出函数
        self._flag = True


def main(stdscr):
    stdscr.clear()
    win = curses.newwin(curses.LINES - 2, curses.COLS - 1, 0, 0)  # 文本显示区域
    rollfun = run()
    t1 = threading.Thread(target=rollfun.run, args=("thread1 out", win,))  # 为了可以在后台不断添加行，使用线程在后台循环
    t1.start()
    win2 = curses.newwin(1, curses.COLS - 1, curses.LINES - 1, 0)  # 文本输入区域
    stdscr.refresh()
    while True:
        tbox = Textbox(win2)  # 在win2里放置一个textbox
        tbox.edit()  # textbox等待用户输入
        message = tbox.gather()  # 获得用户输入值
        message = message[:len(message) - 1]  # 实际测试中字符串会比实际多出一个字符，原因不明，可能是换行或者什么别的标志符吧
        if message == "exit":
            rollfun.terminates()
            return
        elif message == "help":
            lines.append("Help:'exit' to exit.")
            t2 = threading.Thread(target=viewstrings, args=(lines, win,))
            t2.start()
            t2.join()
            win2.clear()
        else:
            lines.append("User input:'" + message + "'")
            t2 = threading.Thread(target=viewstrings, args=(lines, win,))
            t2.start()
            t2.join()
            win2.clear()


if __name__ == "__main__":
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    wrapper(main)
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    print("主进程结束")