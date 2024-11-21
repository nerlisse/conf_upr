# Эмулятор для языка оболочки ОС 

## Общее описание

Проект представляет собой эмулятор оболочки языка OS, реализованный на Python. Эмулятор поддерживает команды командной строки, такие как  `ls`, `cd`, `exit`, `uptime`, `touch`, `uniq` и работает в режиме GUI. Виртуальная файловая система загружается из архива tar.

### Основные особенности
* Эмуляция команд UNIX-подобной оболочки.
* Поддержка виртуальной файловой системы, загружаемой из архива tar.
* Поддержка базовых команд для работы с файлами и директориями.
* Работа в режиме GUI.

### Структура проекта


```
homework1/
├── config/
│   ├── config.json  #конфигурационный файл
│   └── archive.tar #виртуальная файловая система
├── src/
│   └── ShellEmulator.py #основной файл с программой
└── test/
    └── TestEmulator.py #тесты для программы
```

## Описание функций и настроек

### Класс **`ShellEmulator`**

`def __init__(self, config)`

```
    def __init__(self, config):
        self.hostname = config["hostname"]
        self.vfs_path = config["vfs_path"]
        self.current_dir = "/"
        self.vfs = {}
        self.start_time = time.time()
        self.load_vfs(self.vfs_path)
```

* Описание: инициализирует эмулятор оболочки.
* Принимаемые параметры: 
  * `config` - путь к конфигурационному файлу.

`load_vfs(self, tar_path)`

```
def load_vfs(self, tar_path):
    with tarfile.open(tar_path, "r") as tar:
        for member in tar.getmembers():
            self.vfs[f"/{member.name}"] = {
                "is_dir": member.isdir(),
                "content": "" if member.isdir() else tar.extractfile(member).read().decode("utf-8")
            }
    self.current_dir = "/"
```    

* Описание: загружает виртуальную файловую систему из архива .tar.
* Параметры:
  * `tar_path` - путь к архиву.


`ls(self)`

```
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
```

* Описание: список файлов и директорий в текущей директории.
* Возвращаемое значение: строка с именами файлов и папок, разделенных переносом строки.


`change_dir(self, path)`

```
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
```
* Описание: изменяет текущую директорию. Поддерживает относительные пути и переход на уровень выше через "..".
* Параметры:
  * `path` - относительный или абсолютный путь к директории.
* Возвращаемое значение: строка об успешном или неудачном выполнении файла

`exit_shell(self)`

```
    def exit_shell(self):
        return "exit"
```
* Описание: завершает сеанс эмулятора.
* Возвращаемое значение: "exit", которое интерпретируется GUI как команда на закрытие.


`uptime(self)`
```
    def uptime(self):
        uptime_seconds = time.time() - self.start_time #время работы эмулятора
        current_time = time.strftime("%H:%M:%S", time.localtime()) #время сейчас

        hours, remainder = divmod(int(uptime_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_formatted = f"{hours}h {minutes}m {seconds}s" #отображаем время работы эмулятора
        return f"Current Time: {current_time} Uptime: {uptime_formatted}"
```
* Описание: показывает текущее время и время работы эмулятора.
* Возвращаемое значение: строка в формате `Current Time: HH:MM:SS Uptime: Xh Ym Zs`.


`touch(self, filename)`
```
    def touch(self, filename):
        #путь нового файла - текущая + / если не корень + имя
        new_file_path = self.current_dir + "/"*(self.current_dir!="/") + filename
        if new_file_path not in self.vfs:
            self.vfs[new_file_path] = {"is_dir": False, "content": ""}
            return f"File {filename} created"
        return f"File {filename} already exists"
```
* Описание: создает новый файл в текущей директории.
* Параметры:
  * `filename` - имя файла.
* Возвращаемое значение: подтверждение создания файла или сообщение об ошибке, если файл уже существует.



`uniq(self, filename)`
```
    def uniq(self, filename):
        file_path = self.current_dir + "/"*(self.current_dir!="/") + filename
        #если есть файл такой и он не директория
        if file_path in self.vfs and not self.vfs[file_path]["is_dir"]:
            lines = self.vfs[file_path]["content"].splitlines()
            uniq_lines = "\n".join(set(lines))
            return uniq_lines
        return f"uniq: {filename}: No such file or directory"
```

* Описание: возвращает уникальные строки из содержимого файла.
* Параметры:
  * `filename` - имя файла.
* Возвращаемое значение: уникальные строки или сообщение об ошибке.

`execute_command(self, command)`

```
def execute_command(self, command):
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
```

* Описание: интерпретирует команду и вызывает соответствующий метод.
* Параметры:
  *  `command` - строка команды.
* Возвращаемое значение: результат выполнения команды.

### Класс **`ShellGUI`**


`__init__(self, root, emulator)`
```
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
```
* Описание: инициализирует GUI оболочки.
* Параметры:
  * `root` - объект корневого окна.
  * `emulator` - объект ShellEmulator.

`show_prompt(message="")`

```
def show_prompt(self, message=""):
    self.text_area.configure(state=tk.NORMAL)
    if message == "":
        self.text_area.insert(tk.END, f"{self.emulator.hostname}:~{self.emulator.current_dir}$ ")
    else:
        self.text_area.insert(tk.END, f"{message}")
    self.text_area.configure(state=tk.DISABLED)
    self.text_area.see(tk.END)
```
* Описание: показывает приглашение ввода или выводит результат команды.
* Параметры:
  * `message` - сообщение для вывода.

`process_input(self, event=None)`

```
def process_input(self, event=None):
    user_input = self.input_field.get()
    self.input_field.delete(0, tk.END)
    self.show_prompt(user_input + "\n")
    result = self.emulator.execute_command(user_input)
    if result:
        self.show_prompt(result + "\n")
    if result == "exit":
        self.root.quit()
    self.show_prompt()
```

* Описание: обрабатывает ввод команды, выводит результат и обновляет интерфейс.
* Параметры:
  * `event`: событие (нажатие клавиши Enter).


## Описание команд для сборки проекта

Для работы с проектом необходимо иметь установленный Python 3.11 или выше.

### Клонирование репозитория и запуск проекта

```
git clone https://github.com/nerlisse/conf_upr.git
cd homework1
python src/ShellEmulator.py
```

### Результат прогона тестов
![img.png](img.png)

