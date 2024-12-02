import os
import unittest
import struct
from homework4.src.Assembler import Assembler

class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.assembler = Assembler("test_input.asm", "test_output.bin", "test_log.yaml")

    def test_load_const(self):
        with open("test_input.asm", "w") as f:
            f.write("LOAD_CONST 100\n")
        self.assembler.assemble()
        with open("test_output.bin", "rb") as f:
            data = f.read()
        instruction = struct.unpack("<I", data)[0]
        self.assertEqual(instruction & 0x1F, 26)  # A = 26 (LOAD_CONST)
        self.assertEqual((instruction >> 5) & 0x1FFF, 100)  # B = 100
        os.remove("test_input.asm")
        os.remove("test_log.yaml")
        os.remove("test_output.bin")

    def test_read_from_memory(self):
        with open("test_input.asm", "w") as f:
            f.write("READ_FROM_MEMORY 2000\n")
        self.assembler.assemble()
        with open("test_output.bin", "rb") as f:
            data = f.read()
        instruction = struct.unpack("<I", data)[0]
        self.assertEqual(instruction & 0x1F, 18)  # A = 18 (READ_FROM_MEMORY)
        self.assertEqual((instruction >> 5) & 0x7FFFFF, 2000)  # B = 2000
        os.remove("test_input.asm")
        os.remove("test_log.yaml")
        os.remove("test_output.bin")

    def test_write_to_memory(self):
        with open("test_input.asm", "w") as f:
            f.write("WRITE_TO_MEMORY 3000\n")
        self.assembler.assemble()
        with open("test_output.bin", "rb") as f:
            data = f.read()
        instruction = struct.unpack("<I", data)[0]
        self.assertEqual(instruction & 0x1F, 23)  # A = 23 (WRITE_TO_MEMORY)
        self.assertEqual((instruction >> 5) & 0x7FFFFF, 3000)  # B = 3000
        os.remove("test_input.asm")
        os.remove("test_log.yaml")
        os.remove("test_output.bin")

    def test_not_equal(self):
        with open("test_input.asm", "w") as f:
            f.write("NOT_EQUAL 500\n")
        self.assembler.assemble()
        with open("test_output.bin", "rb") as f:
            data = f.read()
        instruction = struct.unpack("<I", data)[0]
        self.assertEqual(instruction & 0x1F, 17)  # A = 17 (NOT_EQUAL)
        self.assertEqual((instruction >> 5) & 0x7FF, 500)  # B = 500
        os.remove("test_input.asm")
        os.remove("test_log.yaml")
        os.remove("test_output.bin")

    def test_invalid_command(self):
        with open("test_input.asm", "w") as f:
            f.write("LEE_KNOW 100\n")
        with self.assertRaises(SyntaxError):
            self.assembler.assemble()
        os.remove("test_input.asm")


    def test_out_of_range(self):
        with open("test_input.asm", "w") as f:
            f.write("LOAD_CONST 99999\n")
        with self.assertRaises(ValueError):
            self.assembler.assemble()
        os.remove("test_input.asm")

if __name__ == "__main__":
    unittest.main()
