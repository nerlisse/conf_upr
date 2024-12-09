# Учебный конфигурационный язык  

## Общее описание

Проект представляет собой инструмент командной строки для учебного конфигурационного
языка, синтаксис которого приведен далее. Этот инструмент преобразует текст из
входного формата в выходной. Синтаксические ошибки выявляются с выдачей
сообщений.
Входной текст на учебном конфигурационном языке принимается из
стандартного ввода. Выходной текст на языке yaml попадает в стандартный
вывод.

Массивы: `<< значение, значение, значение, ... >>`

Словари: 
`table(

 имя => значение,

 имя => значение,

 имя => значение,

 ...

)`


Имена: `[a-zA-Z][_a-zA-Z0-9]*`.


Значения:
* Числа.
* Массивы.
* Словари.


Объявление константы на этапе трансляции: `(def имя значение)`.

Вычисление константы на этапе трансляции: `#[имя]`. Результатом вычисления константного выражения является значение

### Структура проекта


```css
homework3/
├── src/
│   └── ConfLang.py #основной файл с программой
└── test/
    └── TestLang.py #тесты для программы
```

## Описание функций и настроек

### Класс **`ConfigParser`**

`def __init__(self)`

```Python
    def __init__(self):
        self.constants = {}  # массив с константами
```

* Описание: инициализирует парсер.

`def parse_table(self, text)`

```Python
    def parse_table(self, text):
        result = {}
        key = None
        value = ""
        depth = 0
        i = 0
        text = text.replace("\n", "").replace(" ", "")

        while i < len(text):  # проходим по элементам строки
            char = text[i]

            if char == 't' and text[i:i + 6] == 'table(':  # если встретился вложенный словарь
                depth += 1
                value += 'table('
                i += 5
            elif char == '<' and text[i:i + 2] == '<<':  # если встретился вложенный массив
                depth += 1
                value += '<<'
                i += 1
            elif char == ')' and depth > 0:  # если закончился вложенный словарь
                depth -= 1
                value += ')'
            elif char == '>' and text[i:i + 2] == '>>' and depth > 0:  # если закончился внутренний массив
                depth -= 1
                value += '>>'
                i += 1
            elif char == ',' and depth == 0:  # если закончилось текущее значение
                if key is not None:
                    result[key.strip()] = self.parse_value(value.strip())
                    key = None
                    value = ""
            elif char == '=' and text[i:i + 2] == '=>' and depth == 0: # если был введен ключ и переход к значению
                key = value.strip()
                value = ""
                i += 1
            else:
                value += char

            i += 1

        if key is not None:  # считаем последний элемент
            result[key.strip()] = self.parse_value(value.strip())

        return result
```

* Описание: обрабатывает значения словаря с учетом всех возможных вложенностей.
* Принимаемые параметры:  `text` - имена и значения словаря.
* Возвращаемые параметры: `result` - итоговый словарь.


`def parse_array(self, text)`

```Python
    def parse_array(self, text):
        values = []
        depth = 0
        current_value = ""
        i = 0

        while i < len(text):  # проходим по всем элементам
            char = text[i]

            if char == '<' and text[i:i + 2] == '<<':  # если встретили вложенный массив
                depth += 1
                current_value += '<<'
                i += 1
            elif char == '>' and text[i:i + 2] == '>>' and depth > 0:  # если закончился вложенный массив
                depth -= 1
                current_value += '>>'
                i += 1
            elif char == 't' and text[i:i + 6] == "table(":  # если встретили вложенный словарь
                depth += 1
                current_value += 'table('
                i += 5
            elif char == ')' and depth > 0:  # если закончился вложенный словарь
                depth -= 1
                current_value += ')'
            elif char == ',' and depth == 0:  # если закончилось текущее значение
                values.append(current_value.strip())
                current_value = ""
            else:  # иначе сохраняем значение
                current_value += char

            i += 1

        if current_value.strip():  # если осталось значение
            values.append(current_value.strip())

        return [self.parse_value(value) for value in values]
```

* Описание: обрабатывает значения массива с учетом всех возможных вложенностей.
* Принимаемые параметры:  `text` - элементы массива.
* Возвращаемые параметры: итоговый массив.

`def parse_value(self, value)`

```Python
    def parse_value(self, value):
        if re.match(self.PATTERN_TABLE, value):  # если встретили словарь
            return self.parse_table(value[6:-1])
        elif re.match(self.PATTERN_ARRAY, value):  # если встретили массив
            return self.parse_array(value[2:-2])
        elif re.match(r'\d+', value):  # если встретили число
            return int(value)
        elif re.match(self.PATTERN_CONST, value):  # если встретили константу
            const_name = re.match(self.PATTERN_CONST, value).group(1)
            if const_name in self.constants:
                return self.constants[const_name]
            else:
                raise ValueError(f"Undefined constant: {const_name}")
        else:
            raise ValueError(f"Invalid value: {value}")
```

* Описание: обрабатывает полученное значение - массив, словарь, константу, число.
* Принимаемые параметры:  `value` - исследуемое значение.
* Возвращаемые параметры: обработанное значение.

`def process_config(self, text)`

```Python
    def process_config(self, text):

        text = text.replace("\n", "").strip()

        current_def = None
        current_value = ""
        i = 0
        depth = 0

        while i < len(text): # идем посимвольно
            char = text[i]

            if char == '(' and text[i:i + 5] == '(def ':  # определение константы
                # если определяется константа, когда другая не доопределена или присутствуют сторонние символы
                if current_def or current_value.strip():
                    raise SyntaxError("Invalid syntax")
                i += 5
                start = i
                while text[i] != ' ':
                    i += 1
                current_def = text[start:i] # имя константы
            elif char == 't' and text[i:i + 6] == 'table(':  # вложенный словарь
                depth += 1
                current_value += 'table('
                i += 5
            elif char == ')' and depth > 0:  # закончился вложенный словарь
                depth -= 1
                current_value += ')'
            elif char == ')' and depth == 0 and not current_def:  # лишняя скобка
                raise SyntaxError("Invalid syntax")
            elif char == ')' and depth == 0:  # окончание значения константы
                # end const
                self.constants[current_def] = self.parse_value(current_value.strip())
                current_def = None
                current_value = ""

            else:
                current_value += char
            i += 1

        if current_def:  # если константа не доопределена
            raise SyntaxError("Invalid syntax")

        print(self.constants)

        return yaml.dump(self.constants, Dumper=NoAliasDumper, default_flow_style=False, canonical=False)  # возвращаем в формате yaml
```

* Описание: обрабатывает полученные исходные данные - преобразует константы и находит массивы и словари.
* Принимаемые параметры:  `text` - введенный текст.
* Возвращаемые параметры: обработанный текст на языке yaml.

## Описание команд для сборки проекта

Для работы с проектом необходимо иметь установленный Python 3.11 или выше.

### Клонирование репозитория и запуск проекта

```bash
git clone https://github.com/nerlisse/conf_upr.git
cd homework3
```

### Установка зависимостей
В данном проекте используются сторонние библиотеки python, поэтому перед запуском проекта необходимо запустить скрипт из файла `requirements.sh`.

Запустить программу командой:

```bash
python src/ConfigParser.py
```

### Результат прогона тестов

![image.png](https://github.com/user-attachments/assets/ba710d87-e785-4edb-8c56-b647015fe735)
