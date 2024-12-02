import struct
import yaml
import sys

# функция преобразования инструкции в массив байтов (4 байта)
def instruction_to_bytes(instruction):
    raw_bytes = struct.pack("<I", instruction)
    return [f"0x{b:02X}" for b in raw_bytes]

# функция для извлечения значения из инструкции
def extract_field(instruction, shift, bit_length):
    mask = (1 << bit_length) - 1  # маска для извлечения нужного поля
    value = (instruction >> shift) & mask  # извлечение значения поля
    return value

def interpret(binary_file, result_file, memory_range):
    with open(binary_file, "rb") as f:
        data = f.read()

    memory = [0] * memory_range  # Простая модель памяти
    print(f"memory range: {memory_range}")
    stack = []  # Стек для выполнения операций
    program_counter = 0
    log_data = []

    while program_counter < len(data):
        # Читаем инструкцию
        instruction = int.from_bytes(data[program_counter:program_counter + 4], "little")
        program_counter += 4

        # Распаковка команды
        #A = extract_field(instruction, 0, 5)  # Первые 5 бит — команда
        A = instruction & 0x1F
        bit_length = (13 if (A == 26) else (11 if (A == 17) else 23))
        B = extract_field(instruction, 5, bit_length)


        print(f"A : {A}  B: {B}")
        # Выполнение команды
        if A == 26:  # LOAD_CONST
            print("load const")
            stack.append(B)
        elif A == 18:  # READ_FROM_MEMORY
            if B > memory_range:
                raise ValueError(
                    f"binary file contains invalid data: accessing a memory cell at an address out of range")
            print("read mem")
            value = memory[B]
            stack.append(value)
        elif A == 23:  # WRITE_MEM
            if B > memory_range:
                raise ValueError(
                    f"binary file contains invalid data: accessing a memory cell at an address out of range")
            print("write mem")
            value = stack.pop()
            memory[B] = value  # Запись значения в память
        elif A == 17:  # NOT_EQUAL
            print("not equal")
            value1 = stack.pop()
            if B+value1 > memory_range:
                raise ValueError(
                    f"binary file contains invalid data: accessing a memory cell at an address out of range")
            value2 = memory[B+value1]
            result = 1 if value1 != value2 else 0
            stack.append(result)
        else:
            raise ValueError("binary file contains invalid data: invalid bytecode")

        # Логирование текущей инструкции и состояния
        log_data.append({
            "instruction":  instruction_to_bytes(instruction),
            "A": A,
            "B": B,
            "stack_snapshot": stack[:10],  # Вывод первых 10 элементов стека
            "memory_snapshot": memory[:10],  # Вывод первых 10 элементов памяти
        })

    # Сохраняем результат в диапазоне памяти
    result = {"log": log_data, "memory": memory}
    with open(result_file, "w") as f:
        yaml.dump(result, f, default_flow_style=False)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python interpreter.py <binary_file> <result_file> <range_start> <range_end>")
        sys.exit(1)

    binary_file = sys.argv[1]
    result_file = sys.argv[2]
    range_start = int(sys.argv[3])
    range_end = int(sys.argv[4])
    interpret(binary_file, result_file, range_end - range_start)
