import curses
from window.window import Window
from window.item import BoolItem, MenuItem, StringItem, EnumItem


class MenuWindow(Window):
    def __init__(self, win):
        super().__init__()
        self.__win = win
        self.__items = []
        self.cur_cursor = 0

    @property
    def win(self):
        return self.__win

    @property
    def items(self):
        return [item for item in self.__items if item.valid]

    def cur_item(self):
        if self.items:
            return self.items[self.cur_cursor]

    def add_item(self, item, depend_bool=None, depend_string=None):
        item.valid = True
        item.depends = {}
        if depend_bool:
            for depend_key in depend_bool:
                item.depends[depend_key] = True
        if depend_string:
            for depend_key, depend_val in depend_string:
                item.depends[depend_key] = depend_val
        self.__items.append(item)

    def update_item(self):
        for item in self.__items:
            if item.depends:
                self.check_item_depends(item)

    def check_item_depends(self, check_item):
        check = []
        for depend_key, depend_val in check_item.depends.items():
            for item in self.__items:
                if item.symbol == depend_key:
                    if type(item.value) == list and depend_val in item.value:
                        check.append(True)
                    elif depend_val == item.value:
                        check.append(True)
                    else:
                        check.append(False)
        if check:
            check_item.valid = all(check)
        
    def draw(self):
        self.update_item()
        self.win.clear()
        max_y, max_x = self.win.getmaxyx()
        max_prefix_len = max([len(item.prefix_str) for item in self.items])
        max_symbol_len = max([len(item.symbol_str) for item in self.items])
        symbol_pos = max_prefix_len + 5
        help_pos = symbol_pos + max_symbol_len +5
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        for idx, item in enumerate(self.items):
            #  format the option string
            item_str = ""
            if item.prefix_str:
                item_str += item.prefix_str 
            if item.symbol_str:
                item_str += " "*(max_prefix_len-len(item.prefix_str)+5) 
                item_str += item.symbol_str 
            if item.help_str:
                item_str += " "*(max_symbol_len-len(item.symbol_str)+5) 
                item_str += item.help_str
            #  highlight the chosen option
            if idx == self.cur_cursor:
                self.win.addstr(idx, 0, item_str, curses.A_REVERSE+curses.color_pair(1))
            else:
                self.win.addstr(idx, 0, item_str)

    def down(self):
        if self.cur_cursor < len(self.items)-1:
            self.cur_cursor += 1
        else:
            self.cur_cursor = len(self.items)-1

    def up(self):
        if self.cur_cursor > 0:
            self.cur_cursor -= 1
        else:
            self.cur_cursor = 0

    def main_loop(self):
        #  draw the menu
        self.draw()
        #  process user input
        user_input = self.win.getch()
        if user_input == ord('q'):
            return self.EXIT
        elif user_input == ord('\n'):
            cur_item = self.cur_item()
            return cur_item.toggle()
        else:
            if user_input == curses.KEY_DOWN:
                self.down()
            elif user_input == curses.KEY_UP:
                self.up()
            return self.STAY
        
    def get_all_values(self):
        value_dict = {}
        for item in self.items:
            value_dict[item.symbol] = item.value
        return value_dict
