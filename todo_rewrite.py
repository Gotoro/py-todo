import curses
from string import ascii_letters, punctuation
from curses import wrapper
from os.path import isfile

class ToDo():
    # read the contents of todo file
    def open_todo(self) -> list[str]:
        if not isfile("todo.txt"):
            with open("todo.txt", "w") as txt:
                txt.write("")

        # read all lines into a list
        with open("todo.txt") as txt:
            out_txt = txt.read().split("\n")

        return out_txt

    # add a new task to the list
    def add_new_task(self, task_to_add: str) -> None:
        with open("todo.txt", "a") as txt:
            txt.write(task_to_add + "\n")

    # remove a task from the list
    def remove_task(self, task_id: int):
        read_txt = self.open_todo()
        read_txt.pop(task_id - 1)

        # update the file
        with open("todo.txt", "w") as txt:
            txt.write("")
            txt.write("\n".join(read_txt))

        # update internal todo_list with the new todo file
        self.todo_list = self.open_todo()

    # print out the tasks on the screen
    def print_tasks(self):
        for i, task in enumerate(self.todo_list):
            self.screen.addstr(i+1, 0, f"{i + 1}) {task}")

    def __init__(self, screen):
        self.todo_list = self.open_todo()
        self.current_len = len(self.todo_list)
        self.screen = screen

        self.STATUS_BAR_TEMPLATE = "Enter: add a new task, Delete: delete a task, ↑↓ to select a task, Q: exit"
        self.ALLOWED_LETTERS = ascii_letters + punctuation + str([*range(10)]) + " "
        self.y_cord = 1
        self.DIR_KEYS = {
            "KEY_UP": -1,
            "KEY_DOWN": 1,
        }

    def clear_screen(self):
        self.screen.clear()

    def print_status_bar(self):
        self.screen.addstr(
            0,
            0,
            # f"y: {self.y_cord}, amount of tasks: {self.current_len} {self.STATUS_BAR_TEMPLATE}"
            f"tasks: {self.current_len} {self.STATUS_BAR_TEMPLATE}"
        )

    def get_key(self) -> str:
        # this saves the last pressed key into a variable for ease of accessing it later
        self.last_key = self.screen.getkey(self.y_cord, 0)

        # but also returns the key for use in things like while loops
        return self.last_key

    # arrow nav handling
    def handle_arrows(self) -> None:
        if self.last_key in self.DIR_KEYS:
            self.y_cord += self.DIR_KEYS[self.last_key]

            # limit vertical movement
            self.y_cord = min(self.y_cord, self.current_len)
            self.y_cord = max(self.y_cord, 1)

    # handle new task adding
    def handle_new_task(self) -> None:
        task_to_add = ""
        # move cursor one down to add a new task
        self.current_len += 1
        self.y_cord = self.current_len

        self.screen.addstr(
            self.current_len,
            0,
            f"{self.current_len})"
        )

        # getting the prompt
        while self.get_key() != "\n":
            # erasing with backspace
            if self.last_key == "KEY_BACKSPACE" and task_to_add != "":
                task_to_add = task_to_add[:-1]
            else:
                # allow only certain symbols
                if self.last_key in self.ALLOWED_LETTERS:
                    task_to_add += self.last_key

            self.screen.clrtoeol()
            self.screen.addstr(
                self.current_len,
                0,
                f"{self.current_len}) {task_to_add}"
            )

        # update the file
        self.add_new_task(task_to_add)

    def handle_delete_task(self) -> None:
        # check if we have any tasks to delete
        if self.current_len <= 0:
            return

        # remove the task from file,
        # clear the screen, update the screen tasks,
        # update current cursor pos
        # update current tasks len
        self.remove_task(self.y_cord)
        self.clear_screen()
        self.print_tasks()
        self.y_cord -= 1
        # don't set y to 0
        self.y_cord = max(self.y_cord, 1)
        self.current_len -= 1

    # certain actions on a key press
    def handle_action(self, key: str) -> None:
        match key:
            case "\n":
                self.handle_new_task()
            case "KEY_DC":
                self.handle_delete_task()
            case "KEY_UP" | "KEY_DOWN":
                self.handle_arrows()
            # DEBUG: outputs currently pressed key
            # case _:
            #     print(f"Got {key}, exiting")


def main(stdscr):
    # define background
    curses.use_default_colors()
    # use default terminal fg and bg
    # initialises a so called "curses color pair" assigning it the id of 1
    curses.init_pair(1, -1, -1)
    # fill the background with empty " " symbol,
    # use the color pair with the id of 1
    stdscr.bkgd(" ", curses.color_pair(1))

    # init the todo class
    todo = ToDo(stdscr)

    # init print status bar and current tasks
    todo.print_status_bar()
    todo.print_tasks()

    # exit on Q
    while todo.get_key() != "Q":
        # arrow handling, update current cursor coordinates
        todo.handle_action(todo.last_key)
        todo.print_status_bar()
        todo.print_tasks()

        todo.screen.refresh()



# curses wrapper
# handles a bunch of things automatically
if __name__ == "__main__":
    wrapper(main)