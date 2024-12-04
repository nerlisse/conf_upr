import unittest
import yaml
from homework3.src.ConfigParser import ConfigParser

class TestConfigParser(unittest.TestCase):

    def setUp(self):
        self.parser = ConfigParser()


    def test_table(self):
        input_text = """
        table(
            key1 => 325,
            key2 => table(
                nested_key => 2511,
            ),
            key3 => 914,
        )
        """
        result = self.parser.process_config(input_text)
        #print(result)
        expected = [{
            'key1': 325,
            'key2': {'nested_key': 2511},
            'key3': 914
        }]
        self.assertEqual(yaml.safe_load(result), expected)

    def test_array(self):
        input_text = """
        << 1, 2, table(key => 3), 4 >>
        """
        result = self.parser.process_config(input_text)
        expected = [[1, 2, {'key': 3}, 4]]
        self.assertEqual(yaml.safe_load(result), expected)

    def test_undefined_constant(self):
        input_text = """
        table(key => #[undefined_const])
        """
        with self.assertRaises(ValueError):
            self.parser.process_config(input_text)

    def test_invalid_syntax(self):
        input_text = """
        table(key => #![invalid])
        """
        with self.assertRaises(ValueError):
            self.parser.process_config(input_text)

    def test_program(self):
        input_text = """
        (def myconst table(
            leeknow => 2511,
        ))
        table(
            key1 => 143,
            key2 => << 1, 2, table( 
                nested => #[myconst],
            ), 4, >>,
        )
        << table(key => 1), 3, 4, >>
        """
        result = self.parser.process_config(input_text)
        expected = [{
            'key1': 143,
            'key2': [1, 2, {'nested': {'leeknow':2511}}, 4]
        }, [{'key': 1}, 3, 4]]
        self.assertEqual(yaml.safe_load(result), expected)

if __name__ == "__main__":
    unittest.main()
