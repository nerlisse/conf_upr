import os
import unittest
from homework4.src.Interpreter import Interpreter

class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter("test_output.bin", "test_result.yaml", 1024)

    def test_load_const(self):
        self.interpreter.memory = [0] * 1024
        self.interpreter.stack = []
        self.interpreter.binary_file = "load_const_test.bin"
        with open(self.interpreter.binary_file, "wb") as f:
            f.write((26 | (100 << 5)).to_bytes(4, "little"))  # LOAD_CONST 100
        self.interpreter.interpret()
        self.assertEqual(self.interpreter.stack[-1], 100)
        os.remove("load_const_test.bin")
        os.remove("test_result.yaml")

    def test_read_from_memory(self):
        self.interpreter.memory = [0] * 1024
        self.interpreter.memory[10] = 42
        self.interpreter.stack = []
        self.interpreter.binary_file = "read_mem_test.bin"
        with open(self.interpreter.binary_file, "wb") as f:
            f.write((18 | (10 << 5)).to_bytes(4, "little"))  # READ_FROM_MEMORY 10
        self.interpreter.interpret()
        self.assertEqual(self.interpreter.stack[-1], 42)
        os.remove("read_mem_test.bin")
        os.remove("test_result.yaml")

    def test_write_to_memory(self):
        self.interpreter.memory = [0] * 1024
        self.interpreter.stack = [99]
        self.interpreter.binary_file = "write_mem_test.bin"
        with open(self.interpreter.binary_file, "wb") as f:
            f.write((23 | (20 << 5)).to_bytes(4, "little"))  # WRITE_TO_MEMORY 20
        self.interpreter.interpret()
        self.assertEqual(self.interpreter.memory[20], 99)
        os.remove("write_mem_test.bin")
        os.remove("test_result.yaml")

    def test_not_equal(self):
        self.interpreter.memory = [0] * 1024
        self.interpreter.memory[154] = 154
        self.interpreter.stack = [154]
        self.interpreter.binary_file = "not_equal_test.bin"
        with open(self.interpreter.binary_file, "wb") as f:
            f.write(((17 & 0x1F) | ((0 & 0x7FF) << 5)).to_bytes(4, "little"))  # NOT_EQUAL 15
        self.interpreter.interpret()
        self.assertEqual(self.interpreter.stack[-1], 0)  # 154 != 154 -> 0
        os.remove("not_equal_test.bin")
        os.remove("test_result.yaml")

    def test_invalid_bytecode(self):
        self.interpreter.binary_file = "invalid_test.bin"
        with open(self.interpreter.binary_file, "wb") as f:
            f.write(b"\xFF\xFF\xFF\xFF")
        with self.assertRaises(ValueError):
            self.interpreter.interpret()
        os.remove("invalid_test.bin")

if __name__ == "__main__":
    unittest.main()
