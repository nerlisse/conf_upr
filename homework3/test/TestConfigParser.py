import unittest
import yaml
from homework3.src.ConfigParser import ConfigParser

class TestConfigParser(unittest.TestCase):

    def setUp(self):
        self.parser = ConfigParser()


    def test_table(self):
        input_text = """
        (def const table(
            key1 => 325,
            key2 => table(
                nested_key => 2511,
            ),
            key3 => 914,
        ) )
        """
        result = self.parser.process_config(input_text)
        #print(result)
        expected = {'const':{
            'key1': 325,
            'key2': {'nested_key': 2511},
            'key3': 914
        }}
        self.assertEqual(yaml.safe_load(result), expected)

    def test_array(self):
        input_text = """
        (def const << 1, 2, table(key => 3), 4 >>)
        """
        result = self.parser.process_config(input_text)
        expected = {'const': [1, 2, {'key': 3}, 4]}
        self.assertEqual(yaml.safe_load(result), expected)

    def test_undefined_constant(self):
        input_text = """
        (def const table( key => #[undefined_const], ) )
        """
        with self.assertRaises(ValueError):
            self.parser.process_config(input_text)

    def test_invalid_syntax(self):
        input_text = """
        (def const table(key => 43 )
        """
        with self.assertRaises(SyntaxError):
            self.parser.process_config(input_text)

    def test_program(self):
        input_text = """
        (def const1 4)
        (def const2 << 1, 2, #[const1], >> )
        (def const3 table(
            key1 => #[const2], 
            key2 => #[const1],
        ) )
        """
        result = self.parser.process_config(input_text)
        expected = {
            'const1': 4,
            'const2': [1, 2, 4],
            'const3': {'key1': [1, 2, 4], 'key2': 4}
        }
        self.assertEqual(yaml.safe_load(result), expected)

if __name__ == "__main__":
    unittest.main()
