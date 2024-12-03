# Ассемблер и интерпретатор для УВМ  

## Общее описание

Проект представляет собой ассемблер и интерпретатор для учебной виртуальной машины (УВМ). Система команд УВМ представлена далее.
Для ассемблера необходимо разработать читаемое представление команд УВМ. Ассемблер принимает на вход файл с текстом исходной программы, путь к которой задается из командной строки. Результатом работы ассемблера является бинарный файл в виде последовательности байт, путь к которому задается из командной строки. Дополнительный ключ командной строки задает путь к файлу-логу, в котором хранятся ассемблированные инструкции в духе списков “ключ=значение”, как в приведенных далее тестах.
Интерпретатор принимает на вход бинарный файл, выполняет команды УВМ и сохраняет в файле-результате значения из диапазона памяти УВМ. Диапазон также указывается из командной строки.
Форматом для файла-лога и файла-результата является yaml.
Тестовая программа: выполнить поэлементно операцию "!=" над вектором длины 8 и числом 154.
Результат записать в исходный вектор.

## Команды ассемблера

### Загрузка константы

| A        | B         |
|----------|-----------|
| Биты 0-4 | Биты 5-17 |
| 26       | Константа |

* Размер команды: 4 байт. 
* Операнд: поле B. 
* Результат: новый элемент на стеке.
* Тест при A=26, B=282:
`0x5A, 0x23, 0x00, 0x00`


### Чтение значения из памяти

| A        | B         |
|----------|-----------|
| Биты 0-4 | Биты 5-27 |
| 18       | Адрес     |

* Размер команды: 4 байт. 
* Операнд: значение в памяти по адресу, которым является поле B. 
* Результат: новый элемент на стеке.
* Тест при A=18, B=898:
`0x52, 0x70, 0x00, 0x00`

### Запись значения в память

| A        | B         |
|----------|-----------|
| Биты 0-4 | Биты 5-27 |
| 23       | Адрес     |

* Размер команды: 4 байт. 
* Операнд: элемент, снятый с вершины стека. 
* Результат: значение в памяти по адресу, которым является поле B.
* Тест при A=23, B=457:
`0x37, 0x39, 0x00, 0x00`


### Бинарная операция: "!="

| A        | B         |
|----------|-----------|
| Биты 0-4 | Биты 5-15 |
| 17       | Адрес     |

* Размер команды: 4 байт. 
* Первый операнд: элемент, снятый с вершины стека.
* Второй операнд: значение в памяти по адресу, которым является сумма адреса
(элемент, снятый с вершины стека) и смещения (поле B). 
* Результат: новый элемент на стеке.
* Тест при A=17, B=319:
`0xF1, 0x27, 0x00, 0x00`

## Описание функций и настроек

### Класс **`Assembler`**

`def __init__(self, input_file, output_file, log_file)`

```Python
    def __init__(self, input_file, output_file, log_file):
        self.output_file = output_file
        self.input_file = input_file
        self.log_file = log_file

        self.binary_data = bytearray()
        self.log_data = []
```

* Описание: инициализирует ассемблер.
* Принимаемые параметры:
  *  `input_file` - путь к файлу, содержащему команды для ассемблера
  * `output_file` - путь к бинарному файлу, где будет записан байт-код
  * `log_file` - путь к файлу лога.

`def instruction_to_bytes(self, instruction)`

```Python
    def instruction_to_bytes(self, instruction):
        raw_bytes = struct.pack("<I", instruction)
        return [f"0x{b:02X}" for b in raw_bytes]
```

* Описание: преобразует инструкцию в массив из байтов.
* Принимаемые параметры:
  * `instruction` - Целое число (32 бита), представляющее машинную инструкцию в виде единого значения.
* Возвращаемый параметр:
  * список строк, где каждая строка представляет один байт инструкции в шестнадцатеричном формате.

`def save_binary(self)`

```Python
    def save_binary(self):
        with open(self.output_file, "wb") as f:
            f.write(self.binary_data)
```

* Описание: сохраняет байт-код в бинарный файл.

`def save_log(self)`

```Python
    def save_log(self):
        with open(self.log_file, "w") as f:
            yaml.dump(self.log_data, f, default_flow_style=False)
```

* Описание: сохраняет логи в лог-файл.

`def assemble(self)`

```Python
    def assemble(self):
        with open(self.input_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            if not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) != 2:
                raise SyntaxError(f"{line}\noperation must have 2 arguments")
            command = parts[0]
            if command not in self.COMMANDS:
                raise SyntaxError(f"{line} incorrect command")
            A = self.COMMANDS[command]
            B = int(parts[1], 10)

            # формируем машинный код команды
            instruction = (A & 0x1F)
            match A:
                case 26:
                    if not (0 <= B < (1 << 13)):
                        raise ValueError("Константа B должна быть в пределах от 0 до 2^13-1")
                    instruction |= ((B & 0x1FFF) << 5)
                case 18 | 23:
                    if not (0 <= B < (1 << 23)):
                        raise ValueError("Адрес B должен быть в пределах от 0 до 2^23-1")
                    instruction |= ((B & 0x7FFFFF) << 5)
                case 17:
                    if not (0 <= B < (1 << 11)):
                        raise ValueError("Смещение B должно быть в пределах от 0 до 2^11-1")
                    instruction |= ((B & 0x7FF) << 5)

            # сохраняем бинарное представление
            self.binary_data.extend(struct.pack("<I", instruction))

            # логируем данные
            self.log_data.append({
                "command": command,
                "A": A,
                "B": B,
                "bytes": self.instruction_to_bytes(instruction)
            })

        self.save_binary()
        self.save_log()
```

* Описание: преобразовывает текстовые инструкции (в ассемблерном формате) из входного файла в их машинные аналоги.

### Класс **`Interpreter`**

`def __init__(self, binary_file, result_file, memory_range)`

```Python
    def __init__(self, binary_file, result_file, memory_range):
        self.binary_file = binary_file
        self.result_file = result_file
        self.memory_range = memory_range

        self.memory = [0] * memory_range  # модель памяти
        self.stack = []  # стек для выполнения операций
        self.program_counter = 0
        self.log_data = []
```

* Описание: инициализирует интерпретатор.
* Принимаемые параметры:
  *  `binary_file` - путь к бинарному файлу, где записан байт-код
  * `result_file` - путь к лог-файлу.
  * `memory_range` - диапазон адресов памяти, в пределах которого интерпретатор может производить чтение и запись.

`def save_result(self)`

```Python
     def save_result(self):
        result = {"log": self.log_data, "memory": self.memory}
        with open(self.result_file, "w") as f:
            yaml.dump(result, f, default_flow_style=False)
```

* Описание: сохраняет результат после выполнения всех операций в лог-файл.

`def instruction_to_bytes(self, instruction)`

```Python
    def instruction_to_bytes(self, instruction):
        raw_bytes = struct.pack("<I", instruction)
        return [f"0x{b:02X}" for b in raw_bytes]
```

* Описание: преобразует инструкцию в массив из байтов.
* Принимаемые параметры:
  * `instruction` - Целое число (32 бита), представляющее машинную инструкцию в виде единого значения.
* Возвращаемый параметр:
  * список строк, где каждая строка представляет один байт инструкции в шестнадцатеричном формате.

`def extract_field(self, instruction, shift, bit_length)`

```Python
    def extract_field(self, instruction, shift, bit_length):
        mask = (1 << bit_length) - 1  # маска для извлечения нужного поля
        value = (instruction >> shift) & mask  # извлечение значения поля
        return value
```

* Описание: извлекает определенное битовое поле из машинной инструкции для декодирования.
* Принимаемые параметры:
  *  `instruction` - машинная инструкция.
  * `shift` - количество бит, на которое нужно сдвинуть инструкцию вправо, чтобы извлечь нужное поле.
  * `bit_length` - длина битового поля, которое необходимо извлечь, начиная с позиции, заданной shift.

`def interpret(self)`

```Python
    def interpret(self):
        with open(self.binary_file, "rb") as f:
            data = f.read()

        while self.program_counter < len(data):
            # читаем инструкцию
            instruction = int.from_bytes(data[self.program_counter:self.program_counter + 4], "little")
            self.program_counter += 4

            # Распаковка команды
            A = instruction & 0x1F
            bit_length = (13 if (A == 26) else (11 if (A == 17) else 23))
            B = self.extract_field(instruction, 5, bit_length)

            # print(f"A : {A}  B: {B}")
            # Выполнение команды
            if A == 26:  # LOAD_CONST
                self.stack.append(B)
            elif A == 18:  # READ_FROM_MEMORY
                if B > self.memory_range:
                    raise ValueError(
                        f"binary file contains invalid data: accessing a memory cell at an address out of range")
                value = self.memory[B]
                self.stack.append(value)
            elif A == 23:  # WRITE_TO_MEMORY
                if B > self.memory_range:
                    raise ValueError(
                        f"binary file contains invalid data: accessing a memory cell at an address out of range")
                value = self.stack.pop()
                self.memory[B] = value
            elif A == 17:  # NOT_EQUAL
                value1 = self.stack.pop()
                if B + value1 > self.memory_range:
                    raise ValueError(
                        f"binary file contains invalid data: accessing a memory cell at an address out of range")
                value2 = self.memory[B + value1]
                result = 1 if value1 != value2 else 0
                self.stack.append(result)
            else:
                raise ValueError("binary file contains invalid data: invalid bytecode")

            # логируем текущую инструкцию и состояние
            self.log_data.append({
                "instruction": self.instruction_to_bytes(instruction),
                "A": A,
                "B": B,
                "stack_snapshot": self.stack[:10],  # вывод первых 10 элементов стека
                "memory_snapshot": self.memory[:10],  # вывод первых 10 элементов памяти
            })

        self.save_result()

```

* Описание: выполняет программу, представленную в виде бинарного файла с машинными инструкциями. 

## Описание команд для сборки проекта

Для работы с проектом необходимо иметь установленный Python 3.11 или выше.

### Клонирование репозитория и запуск проекта

```bash
git clone https://github.com/nerlisse/conf_upr.git
cd homework4
```

### Установка зависимостей
В данном проекте используются сторонние библиотеки python, поэтому перед запуском проекта необходимо запустить скрипт из файла `requirements.sh`.

Запустить ассемблер командой:

```bash
python src/Assembler.py <input_file> <output_file> <log_file>
```

`input_file` - путь к файлу с текстовыми командами для ассемблера.
`output_file` - путь к выходному бинарному файлу.
`log_file` - путь к файлу лога.

Пример команды:

```bash
python src/Assembler.py program.asm output.bin log.yaml
```

Запустить интерпретатор:

```bash
python src/Interpreter.py <binary_file> <result_file> <memory_start> <memory_end>
```

`binary_file` - путь к бинарному файлу с машинными инструкциями.
`result_file` - путь к лог-файлу.
`memory_start` - начальный адрес доступной области памяти.
`memory_end` - конечный адрес доступной области памяти.

Пример команды:

```bash
python src/Interpreter.py output.bin result.yaml 0 1024
```


### Результат прогона тестов

![testAssembler](https://github.com/user-attachments/assets/879c13a2-f5bf-4587-bda2-857c62336e48)
![testInterpreter](https://github.com/user-attachments/assets/7f6cdc1b-7474-4587-a4c5-2515bb9cb1de)
