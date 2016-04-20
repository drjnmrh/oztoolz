"""
    Defines different unit test case classes for ioutils package.
        Author: O.Z.
"""


# imports


import os
import unittest

from pathlib import Path

from oztoolz.ioutils import is_subfolder
from oztoolz.ioutils import extract_file_name
from oztoolz.ioutils import TemporaryFoldersManager
from oztoolz.ioutils import TemporaryDirectoryTree


# Test Cases


class TestUtilityMethods(unittest.TestCase):
    """The test case class, which defines test methods for each utility method
    of the package.
    """

    file_names = [dict(path='simple.txt',
                       name='simple.txt'),
                  dict(path='foo/bar/inside_folders.tmp',
                       name='inside_folders.tmp'),
                  dict(path='without_extension',
                       name='without_extension')]

    subfolder_cases = [dict(sub='foo/bar', parent='foo', ref=True),
                       dict(sub='foo/bar', parent='bar', ref=False),
                       dict(sub='foo', parent='foo', ref=False),
                       dict(sub='foo/bar/baz', parent='foo', ref=True),
                       dict(sub='foo/bar/baz', parent='baz', ref=False),
                       dict(sub='FOO/bar', parent='foo', ref=True)]

    def test_is_subfolder(self):
        """Tests 'is_subfolder' method.

        For each pair of paths compares the result of the call of is_subfolder
        with a reference.
        """
        try:
            for case in self.subfolder_cases:
                self.assertEqual(is_subfolder(case['sub'], case['parent']),
                                 case['ref'])
        except (OSError, ValueError) as err:
            self.fail("unexpected exception - " + str(err))

    def test_extract_file_name(self):
        """Tests 'extract_file_name' method.

        For each reference file name from the list creates the file, checks
        the result of the call of the 'extract_file_name' method, and at last
        removes created file.
        """
        try:
            for file_name in self.file_names:

                file_object = None
                parents = None
                first_existing_parent_index = 0

                file_object = Path(file_name['path'])

                parents = list(file_object.parents)

                for i in range(0, len(parents)):
                    if parents[i].exists():
                        first_existing_parent_index = i
                        break

                self.assertLess(first_existing_parent_index,
                                len(parents))

                parents[0].mkdir(0o777, True, True)
                file_object.touch(0o777, True)

                try:
                    self.assertEqual(file_name['name'],
                                     extract_file_name(file_name['path']))
                except AssertionError:
                    raise
                finally:
                    file_object.unlink()
                    for i in range(0, first_existing_parent_index):
                        parents[i].rmdir()
        except (OSError, ValueError) as err:
            self.fail("unexpected exception - " + str(err))


class TestTemporaryFoldersManager(unittest.TestCase):
    """The test case class, which defines unit tests for the
    TemporaryFoldersManager class.
    """

    def test_get_folder(self):
        """Tests 'get_folder' method using simple cases: creates several
        folders and then checks if these folders where removed when it's
        necessary.
        """
        paths = ['foo',
                 'bar',
                 'foo/bar',
                 'baz/foo',
                 'bar/foo',
                 'foo/bar/baz']

        with TemporaryFoldersManager() as manager:
            folders = [manager.get_folder(path) for path in paths]

            self.assertEqual(len(folders), len(paths))

            for folder in folders:
                self.assertTrue(folder.folder.exists())

        for path in paths:
            self.assertFalse(os.path.exists(path))

    def test_force_remove(self):
        """Tests force remove behavior.
        """
        paths = ['root', 'root/foo/bar']
        non_registered = [dict(path="root/temp.tmp", isdir=False),
                          dict(path="root/foo/bar/baz", isdir=True),
                          dict(path="root/bar/baz/temp.tmp", isdir=False)]
        with TemporaryFoldersManager() as temp_manager:
            for path in paths:
                temp_manager.get_folder(path)
            for path in non_registered:
                if path['isdir']:
                    Path(path['path']).mkdir(0o777, True, True)
                else:
                    if not Path(str(Path(path['path']).parent)).exists():
                        Path(str(Path(path['path']).parent)).mkdir(0o777,
                                                                   True, True)
                    Path(path['path']).touch(0o777, True)
            temp_manager.set_force_remove()
        for path in non_registered:
            self.assertFalse(Path(path['path']).exists())

    def test_is_temporary(self):
        """Tests 'is_temporary' method.

        Creates directory tree, creates several temporary folders and then
        for each path in the sample list checks if it is a temporary folder.
        """
        dir_tree = dict(name='root',
                        subs=[dict(name='subA',
                                   subs=[]),
                              dict(name='subB',
                                   subs=[dict(name='grandA', subs=[]),
                                         dict(name='grandB', subs=[])])])

        temp_paths = [dict(path='root/foo', isdir=True),
                      dict(path='root/temp.tmp', isdir=False),
                      dict(path='root/subA/foo/bar', isdir=True),
                      dict(path='baz', isdir=True),
                      dict(path='root/subB/grandB/foo/bar/tmp.t', isdir=False)]

        sample_list = [dict(path='root', res=False),
                       dict(path='baz', res=True),
                       dict(path='root/temp.tmp', res=True),
                       dict(path='root/subA', res=False),
                       dict(path='root/subA/foo', res=True),
                       dict(path='root/subA/foo/bar', res=True),
                       dict(path='root/subB/grandA', res=False),
                       dict(path='root/subB/grandB/foo/bar/tmp.t', res=True)]

        with TemporaryDirectoryTree(dir_tree) as dir_tree:

            with TemporaryFoldersManager() as manager:
                for temp_path in temp_paths:
                    if temp_path['isdir']:
                        manager.get_folder(temp_path['path'])
                    else:
                        manager.track_file(temp_path['path'])

                for sample in sample_list:
                    try:
                        self.assertEqual(sample['res'],
                                         manager.is_temporary(sample['path']))
                    except AssertionError:
                        print("Failed with path: " + sample['path'])
                        raise

    def test_track_file(self):
        """Tests the 'track_file' method of the temporary folders manager.
        """

        temp_files = ['root/temp.tmp',
                      'root/foo/temp.tmp',
                      'root/sub/foo/bar/temp.tmp']

        with TemporaryFoldersManager() as manager:
            for temp_file in temp_files:
                manager.track_file(temp_file)

            for temp_file in temp_files:
                self.assertTrue(os.path.exists(temp_file))

        for temp_file in temp_files:
            self.assertFalse(os.path.exists(temp_file))


# testing


def main():
    """Running test cases.
    """
    unittest.main()


if __name__ == '__main__':
    main()
