"""
    Defines different unit test case classes for testfwk.utesting module.
        Author: O.Z.
"""


# imports


import unittest

if __name__ == '__main__':
    from oztoolz.ioutils import TemporaryFoldersManager

    from oztoolz.testfwk.utesting import ResourceText
else:
    from ..ioutils import TemporaryFoldersManager

    from .utesting import ResourceText


# test cases


class TestResourceText(unittest.TestCase):
    """Defines tests for the ResourceText class.
    """

    def test_load_from_file(self):
        """Tests the 'load_from_file' method of the ResourceText class.
        """
        temp_file_name = "test_resource_text__tmp.txt"

        with TemporaryFoldersManager() as manager:
            manager.track_file(temp_file_name)

            lines = "this is a sample text\nWith a new file\n\tAnd tabs"
            with open(temp_file_name, "w") as file_object:
                file_object.write(lines)

            resource = ResourceText.load_from_file("temp", temp_file_name)
            self.assertEqual(lines, str(resource))

    def test_load(self):
        """Tests the 'load' method of the ResourceText class.
        """
        resource_file_names = [dict(path='first_lines.txt',
                                    text='some text\nnewline',
                                    name='first'),
                               dict(path='foo/second_lines.txt',
                                    text='another text',
                                    name='second')]

        fake_files = [dict(path='first.txt',
                           exists=True,
                           isfile=True),
                      dict(path='foo/second.txt',
                           exists=True,
                           isfile=True),
                      dict(path='first.tmp',
                           exists=True,
                           isfile=True),
                      dict(path='foo/bar/dump',
                           exists=True,
                           isfile=False),
                      dict(path='fake_lines.txt',
                           exists=False,
                           isfile=True)]

        with TemporaryFoldersManager() as temp_manager:
            for res_file in resource_file_names:
                temp_manager.track_file(res_file['path'])
                with open(res_file['path'], "w") as file_object:
                    file_object.write(res_file['text'])

                resource = ResourceText.prototype().load(res_file['path'])

                self.assertFalse(resource is None)
                self.assertEqual(resource.name, res_file['name'])
                self.assertEqual(str(resource), res_file['text'])

            for fake_file in fake_files:
                if not fake_file['exists']:
                    continue

                if fake_file['isfile']:
                    temp_manager.track_file(fake_file['path'])
                else:
                    temp_manager.get_folder(fake_file['path'])

                resource = ResourceText.prototype().load(fake_file['path'])

                self.assertTrue(resource is None)


# testing


def main():
    """Performs unit testing.
    """
    unittest.main()


if __name__ == '__main__':
    main()
