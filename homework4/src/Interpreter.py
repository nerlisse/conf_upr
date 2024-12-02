import struct
import yaml
import sys

class Interpreter:
    def __init__(self, binary_file, result_file, memory_range):
        self.binary_file = binary_file
        self.result_file = result_file
        self.memory_range = memory_range

        self.memory = [0] * memory_range  # модель памяти
        self.stack = []  # стек для выполнения операций
        self.program_counter = 0
        self.log_data = []

    def interpret(self):
        with open(binary_file, "rb") as f:
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

    # функция сохранения результата
    def save_result(self):
        result = {"log": self.log_data, "memory": self.memory}
        with open(result_file, "w") as f:
            yaml.dump(result, f, default_flow_style=False)

    # функция преобразования инструкции в массив байтов (4 байта)
    def instruction_to_bytes(self, instruction):
        raw_bytes = struct.pack("<I", instruction)
        return [f"0x{b:02X}" for b in raw_bytes]

    # функция для извлечения значения из инструкции
    def extract_field(self, instruction, shift, bit_length):
        mask = (1 << bit_length) - 1  # маска для извлечения нужного поля
        value = (instruction >> shift) & mask  # извлечение значения поля
        return value


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python interpreter.py <binary_file> <result_file> <range_start> <range_end>")
        sys.exit(1)

    binary_file = sys.argv[1]
    result_file = sys.argv[2]
    range_start = int(sys.argv[3])
    range_end = int(sys.argv[4])

    interpreter = Interpreter(binary_file, result_file, range_end - range_start)
    try:
        interpreter.interpret()
    except ValueError as e:
        print(e)
    print(f"interpretation completed. result file: {result_file}")