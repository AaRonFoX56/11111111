import unittest
from mail import generate_code


class TestGenerateCodeFunction(unittest.TestCase):

    def test_generate_code_length(self):
        code = generate_code()
        self.assertEqual(len(code), 6, "Generated code should have length 6")

    def test_generate_code_characters(self):
        code = generate_code()
        self.assertTrue(all(c.isalnum() for c in code), "Generated code should contain only alphanumeric characters")

    def test_generate_code_uniqueness(self):
        # Check if multiple generated codes are unique
        generated_codes = {generate_code() for _ in range(100)}
        self.assertEqual(len(generated_codes), 100, "Generated codes should be unique")


if __name__ == '__main__':
    unittest.main()