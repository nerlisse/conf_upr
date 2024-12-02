# Визуализатор графа зависимостей  

## Общее описание

Проект представляет собой инструмент командной строки для визуализации графа зависимостей, включая транзитивные зависимости. Зависимости определяются по имени пакета ОС Ubuntu (apt). Для описания графа зависимостей используется представление Mermaid. Визуализатор выводит результат на экран в виде графического изображения графа.

### Структура проекта


```css
homework2/
├── config/
│   └── config.yaml  #конфигурационный файл
├── src/
│   └── ShellEmulator.py #основной файл с программой
└── test/
    └── TestEmulator.py #тесты для программы
```

## Описание функций и настроек

### Класс **`DependencyVisualizer`**

`def __init__(self, config_path)`

```Python
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.package = self.config["package"]
        self.repo_url = self.config["repo_url"]
        self.visualizer_path = self.config["visualizer_path"]
        self.dependencies = defaultdict(list)
```
* Описание: инициализирует визуализатор зависимостей.
* Принимаемые параметры: 
  * `config_path` - путь к конфигурационному файлу.

`load_config(self, path)`

```Python
    def load_config(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)
```
* Описание: безопасно загружает содержимое конфигурационного yaml-файла.
* Параметры:
* `path` - путь к конфигурационному файлу.


`load_data(self)`

```Python
#функция загрузки списка пакетов и зависимостей из репозитория
    def load_data(self):
           response = requests.get(self.repo_url, stream=True)
           if response.status_code != 200:
               print(f"error fetching package list from {self.repo_url}", file=sys.stderr)
               sys.exit(1)

            #распаковка gzip и парсинг файла
           package_data = {}
           f = gzip.open(response.raw, encoding="utf-8", mode="rt")
           #проходим по каждой строке
           for line in f:
               line = line.strip()
               if line.startswith("Package:"):
                   #рассмотрение текущего пакета
                   current_package = line.split(":", 1)[1].strip()
               elif line.startswith("Depends:") and current_package:
                   #зависимости текущего пакета
                   depends_raw = line.split(":", 1)[1].strip()
                   dependencies = [
                       dep.split("|")[0].strip().split()[0].strip()  #убираем альтернативные зависимости
                       for dep in depends_raw.split(",")
                   ]
                   package_data[current_package] = dependencies
           return package_data
```

* Описание: получает данные о зависимостях пакета из указанного репозитория, затем образовывает словарь из пакетов и их зависимостей.
* Возвращаемое значение: `package_data` - словарь с именами пакетов и их зависимостей.


`build_dependency_graph(self)`

```Python
    def build_dependency_graph(self):
        metadata = self.load_data()
        visited = set()
        queue = [self.package] #очередь на определение зависимостей пакетов

        while queue:
            #удаляем из очереди первый элемент и проверяем, определяли ли для него зависимость
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            if current in metadata:
                dependencies = metadata[current]
                self.dependencies[current] = dependencies
                #добавляем все зависимые пакеты в очередь
                for dep in dependencies:
                    if dep not in visited:
                        queue.append(dep)
```

* Описание: по очереди получает зависимости для данного пакета и для полученных зависимостей, затем записывает в словарь необходимых зависимостей.


`build_dependency_graph(self)`

```Python
    def generate_mermaid_diagram(self):
        lines = ["graph TD"] #определяем диаграмму mermaid сверху-вниз
        #зпаисываем каждую зависимость в lines
        for package, deps in self.dependencies.items():
            for dep in deps:
                lines.append(f"    {package} --> {dep}")
        return "\n".join(lines) #объединяем и возвращаем
```

* Описание: преобразовывает полученный словарь зависимостей в синтаксис mermaid-диаграммы.
* Возвращаемое значение - строка со всеми зависимостями в синтаксисе mermaid-диаграммы, отделенных переносом.

`visualize(self, output_path="graph.png")`

```Python
    def visualize(self, output_path="graph.png"):
        mermaid_content = self.generate_mermaid_diagram()
        #print(mermaid_content)
        #записываем во временный файл содержимое диаграммы
        temp_file = "temp.mmd"
        with open(temp_file, "w") as f:
            f.write(mermaid_content)

        #вызов инструмента mmdc для генерации изображения
        try:
            subprocess.run(
                [self.visualizer_path, "-i", temp_file, "-o", output_path],
                check=True
            )
            print(f"graph generated at {output_path}")
            os.startfile(output_path)
        finally:
            os.remove(temp_file)  #удаление временного файла
```

* Описание: отрисовывает визуальное изображение графа зависимостей и автоматически открывает его.
* Принимаемые параметры: 
  * `output_path` - путь к результирующему файлу - картинке с графом, по умолчанию `graph.png`.


## Описание команд для сборки проекта

Для работы с проектом необходимо иметь установленный Python 3.11 или выше.

### Клонирование репозитория и запуск проекта

```bash
git clone https://github.com/nerlisse/conf_upr.git
cd homework2
```

### Установка зависимостей
В данном проекте используются сторонние библиотеки python, поэтому перед запуском проекта необходимо запустить скрипт из файла `requirements.sh`.

Перед запуском необходимо настроить конфигурационный файл `config/config.yaml`, состоящий из 3 полей:
* `visualizer_path` - путь к программе, отрисовывающей граф.
* `package` - название пакета.
* `repo_url` - URL-адрес репозитория, где находится информация о зависимостях.

После настройки необходимо запустить программу командой:

```bash
python src/Visualizer.py
```

### Пример работы программы
![image.ong](https://github.com/user-attachments/assets/b6470629-71d5-4886-b860-e9b764e1ed3f)


### Результат прогона тестов
![image.png](https://github.com/user-attachments/assets/aa2dfb11-d449-436a-9610-d1e9a678ca71)
