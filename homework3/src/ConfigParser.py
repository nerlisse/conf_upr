import sys
import regex as re
import yaml


class ConfigParser:
    # регулярные выражения, необходимые для работы
    PATTERN_TABLE = r'table\((?:[^()]*|(?R))*\)'
    PATTERN_ARRAY = r'<<\s*(?:[^<>]|table\((?:[^()]*|(?R))*\)|(?R))*\s*>>'
    #PATTERN_DEF = r'\(def\s+([a-zA-Z][_a-zA-Z0-9]*)\s+(.*?)\)'
    #PATTERN_DEF = r'\(def\s+([a-zA-Z][_a-zA-Z0-9]*)\s+(table\((?:[^()]*|(?R))*\)|<<(?:[^<>]|(?R))*>>|\d+)\)'
    PATTERN_DEF = r'\(def\s+([a-zA-Z][_a-zA-Z0-9]*)\s+((?:table\((?:[^()]*|(?R))*\)|<<\s*(?:[^<>]|(?R))*\s*>>|\d+|.*?))\s*\)'
    PATTERN_CONST = r'#\[([a-zA-Z][_a-zA-Z0-9]*)\]'

    def __init__(self):
        self.constants = {}  # массив с константами

    # функция обработки словаря
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

    # функция обработки массива
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

    # функция обработки значения (число, словарь, массив)
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

    # обработка входных данных
    def process_config(self, text):
        # обработка констант
        for match in re.findall(self.PATTERN_DEF, text):
            name, value = match
            self.constants[name] = self.parse_value(value.strip())
            text = re.sub(re.escape(f"(def {name} {value})"), '', text, count=1)
        #print(self.constants)
        yaml_data = []
        combined_pattern = f"{self.PATTERN_TABLE}|{self.PATTERN_ARRAY}"
        matches = re.findall(combined_pattern, text, flags=re.DOTALL)  # находим массивы и словари

        for match in matches:  # обрабатываем каждый
            if match.startswith('table('):
                yaml_data.append(self.parse_table(match[6:-1]))
            elif match.startswith('<<'):
                yaml_data.append(self.parse_array(match[2:-2]))

        return yaml.dump(yaml_data, default_flow_style=False)  # возвращаем в формате yaml


# пример использования
if __name__ == "__main__":
    input_text = ""
    while True:
        # получаем строку из потока стандартного ввода
        line = input()
        #print(line)
        if not line:
            break
        input_text += line
    parser = ConfigParser()
    try:
        result = parser.process_config(input_text)
        print(result)
    except ValueError as e:
        print(f"Syntax error: {e}")
