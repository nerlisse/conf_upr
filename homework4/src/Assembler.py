import struct
import yaml
import sys


class Assembler:
    # определяем опкоды команд
    COMMANDS = {
        "LOAD_CONST": 26,
        "READ_FROM_MEMORY": 18,
        "WRITE_TO_MEMORY": 23,
        "NOT_EQUAL": 17
    }

    def __init__(self, input_file, output_file, log_file):
        self.output_file = output_file
        self.input_file = input_file
        self.log_file = log_file

        self.binary_data = bytearray()
        self.log_data = []

    # функция преобразования инструкции в массив байтов (4 байта)
    def instruction_to_bytes(self, instruction):
        raw_bytes = struct.pack("<I", instruction)
        return [f"0x{b:02X}" for b in raw_bytes]

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

    # функция сохранения бинарного файла
    def save_binary(self):
        with open(self.output_file, "wb") as f:
            f.write(self.binary_data)

    # функция сохранения лог-файла
    def save_log(self):
        with open(self.log_file, "w") as f:
            yaml.dump(self.log_data, f, default_flow_style=False)


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: python src/Assembler.py <input_file> <output_file> <log_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    log_file = sys.argv[3]
    assembler = Assembler(input_file, output_file, log_file)
    try:
        assembler.assemble()
    except ValueError as e:
        print(e)
    print(f"assembly completed. output file: {output_file}")
