import os
import tarfile
import json
import time
import tkinter as tk
from tkinter import scrolledtext

class ShellEmulator:
    def __init__(self, config):
        self.hostname = config["hostname"]
        self.vfs_path = config["vfs_path"]
        self.current_dir = "/"
        self.vfs = {}
        self.start_time = time.time()
        self.load_vfs(self.vfs_path)

    #функция загрузки файловой системы
    def load_vfs(self, tar_path):
        with tarfile.open(tar_path, "r") as tar:
            for member in tar.getmembers():
                self.vfs[f"/{member.name}"] = {
                    "is_dir": member.isdir(),
                    "content": "" if member.isdir() else tar.extractfile(member).read().decode("utf-8")
                }
        self.current_dir = "/"

    #выводит список файлов в текущей директории (команда ls)
    def ls(self):
        files = []
        #путь + / если не корень, current_dir если корень
        prefix = self.current_dir if self.current_dir.endswith("/") else self.current_dir + "/"
        for path in self.vfs:
            if path.startswith(prefix): #проверяем путь
                sub_path = path[len(prefix):].split("/", 1)[0]
                if sub_path and sub_path not in files:
                    files.append(sub_path)
        return "\n".join(files)

    #функция изменения директории (команда cd)
    def change_dir(self, path):
        if path.startswith("/"):  #абсолютный путь
            new_path = path
        elif path == "..":  #переход на уровень выше
            if self.current_dir != "/":  #если мы не в корне
                new_path = os.path.dirname(self.current_dir)
            else:
                new_path = "/"
        else:  #относительный путь
            new_path = self.current_dir + "/"*(self.current_dir!="/") + path

        #проверка существует ли директория и директория ли она :0
        if new_path in self.vfs and self.vfs[new_path]["is_dir"] or new_path=="/":
            self.current_dir = new_path
        else:
            return f"cd: {path}: No such file or directory"

    #команда exit (выход)
    def exit_shell(self):
        return "exit"

    # команда uptime
    def uptime(self):
        uptime_seconds = time.time() - self.start_time #время работы эмулятора
        current_time = time.strftime("%H:%M:%S", time.localtime()) #время сейчас

        hours, remainder = divmod(int(uptime_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_formatted = f"{hours}h {minutes}m {seconds}s" #отображаем время работы эмулятора
        return f"Current Time: {current_time} Uptime: {uptime_formatted}"

    #функция создания файла (команда touch)
    def touch(self, filename):
        #путь нового файла - текущая + / если не корень + имя
        new_file_path = self.current_dir + "/"*(self.current_dir!="/") + filename
        if new_file_path not in self.vfs:
            self.vfs[new_file_path] = {"is_dir": False, "content": ""}
            return f"File {filename} created"
        return f"File {filename} already exists"

    #команда uniq - вывод уникальных строк
    def uniq(self, filename):
        file_path = self.current_dir + "/"*(self.current_dir!="/") + filename
        #если есть файл такой и он не директория
        if file_path in self.vfs and not self.vfs[file_path]["is_dir"]:
            lines = self.vfs[file_path]["content"].splitlines()
            uniq_lines = "\n".join(set(lines))
            return uniq_lines
        return f"uniq: {filename}: No such file or directory"

    #функция выполнения команды, принимает команду, вызывает метод и возвращает значение
    def execute_command(self, command):
        #print(f"Executing command: {command}")
        if command.startswith("ls"):
            return self.ls()
        elif command.startswith("cd "):
            path = command.split(" ", 1)[1]
            return self.change_dir(path)
        elif command == "exit":
            return self.exit_shell()
        elif command == "uptime":
            return self.uptime()
        elif command.startswith("touch "):
            filename = command.split(" ", 1)[1]
            return self.touch(filename)
        elif command.startswith("uniq "):
            filename = command.split(" ", 1)[1]
            return self.uniq(filename)
        else:
            return f"{command}: command not found"


class ShellGUI:
    def __init__(self, root, emulator):
        self.emulator = emulator #shellemulator object
        self.root = root #root window
        self.root.title(f"Shell Emulator - {emulator.hostname}") #title of the window

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30) #текстовое поле с прокруткой
        self.text_area.grid(column=0, row=0) #размещение поля
        self.text_area.configure(state=tk.DISABLED)  #запрет на ввод пользователем

        self.input_field = tk.Entry(root, width=100) #поле ввода
        self.input_field.grid(column=0, row=1) #размещение поля ввода
        self.input_field.bind("<Return>", self.process_input) #нажатие на enter вызывает rocess_input
        #self.input_field.focus_set()
        self.show_prompt() #выводим что готово к выполнению
        #print("constructor done")

    #функция вывода готовности к исполнению команд
    def show_prompt(self, message=""):
        self.text_area.configure(state=tk.NORMAL)  #временно включаем запись в текстовое поле
        if (message==""): #по умолчанию - выводим юзернейм (готовность к выполнению команды)
            self.text_area.insert(tk.END, f"{self.emulator.hostname}:~{self.emulator.current_dir}$ ")
        else: #иначе выводим сообщение
            self.text_area.insert(tk.END, f"{message}")
        self.text_area.configure(state=tk.DISABLED)  #запрещаем ввод пользователем
        self.text_area.see(tk.END)

    #функция выполнения команды и вывода результата
    def process_input(self, event=None):
        user_input = self.input_field.get()
        self.input_field.delete(0, tk.END)
        #self.text_area.insert(tk.END, user_input + "\n")
        self.show_prompt(user_input + "\n")
        result = self.emulator.execute_command(user_input)
        if result:
            #self.text_area.insert(tk.END, result + "\n")
            self.show_prompt(result + "\n")
        if result == "exit":
            self.root.quit()
        self.show_prompt()

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    config = load_config('config/config.json')
    emulator = ShellEmulator(config)

    root = tk.Tk()
    gui = ShellGUI(root, emulator)
    root.mainloop()

if __name__ == "__main__":
    main()


# def test_ls():
#     result  = ls(123)
#     assert result == a
