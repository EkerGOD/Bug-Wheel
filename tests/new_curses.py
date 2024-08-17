import curses

from cusser import Cusser

def app(stdscr) -> None:
    """Start a new application."""
    if not isinstance(stdscr, Cusser):
        stdscr = Cusser(stdscr)

    ultra_violet = (100, 83, 148)
    x, y = 34, 12
    stdscr.addstr(
         f"\033[2J\033[{x};{y}H"
       "\033[1;32mHello "
       f"\033[;3;38;2;{';'.join(map(str, ultra_violet))}m"
         "cusser"
      "\033[m 🤬!"
    )
    stdscr.refresh()
    stdscr.getch()


curses.wrapper(app)