import unittest

from utesting import *
from errors import *

from pathlib import Path


# test cases


class TestResourceText(unittest.TestCase):

    def test_load_from_file(self):
        temp_file_name = "test_resource_text__tmp.txt"

        lines = "this is a sample text\nWith a new file\n\tAnd tabs"
        with open(temp_file_name, "w") as file_object:
            file_object.write(lines)

        try:
            resource = ResourceText.load_from_file("temp", temp_file_name)
            self.assertEqual(lines, str(resource))

            Path(temp_file_name).unlink()
        except EUnknown as err:
            self.fail("caught an unexpected exception: " + str(err))


# testing


def main():
    unittest.main()


if __name__ == '__main__':
    main()