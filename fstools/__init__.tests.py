"""
    Defines different unit test case classes for fstools package.
        Author: O.Z.
"""

# imports

import os
import unittest

from pathlib import Path

from oztoolz.fstools import FileManipulator
from oztoolz.fstools.errors import EFailedToInitialize
from oztoolz.fstools.errors import EFailedToManipulate

from oztoolz.ioutils import TemporaryFoldersManager

# test cases

class TestFileManipulator(unittest.TestCase):
    """Tests FileManipulator class.
    """

    def test_create(self):
        """Tests static 'create' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/existing.tmp", isdir=False)]
        created_files = [dict(path="root/with_parent.tmp",
                              force=False, success=True),
                         dict(path="root/foo/without_parent.tmp",
                              force=True, success=True),
                         dict(path="root/bar/without_parent.tmp",
                              force=False, success=False),
                         dict(path="root/existing.tmp",
                              force=False, success=True)]
        with TemporaryFoldersManager.from_list(test_dirs, True):
            for entry in created_files:
                if entry['success']:
                    manipulator = FileManipulator.create(entry['path'],
                                                         entry['force'])
                    self.assertTrue(manipulator.exists())
                else:
                    with self.assertRaises(EFailedToInitialize):
                        manipulator = FileManipulator.create(entry['path'],
                                                             entry['force'])
                        self.assertFalse(manipulator.exists())

    def test_temp(self):
        """Tests static 'temp' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/existing.tmp", isdir=False)]
        temp_files = [dict(path="root/existing.tmp", success=True),
                      dict(path="root/foo/without_parent.tmp", success=False),
                      dict(path="root/non_existing.tmp", success=True)]
        with TemporaryFoldersManager.from_list(test_dirs, True):
            for entry in temp_files:
                if entry['success']:
                    with FileManipulator.temp(entry['path']) as manipulator:
                        self.assertTrue(manipulator.exists())
                else:
                    with self.assertRaises(EFailedToInitialize):
                        with FileManipulator.temp(entry['path']):
                            pass
                self.assertFalse(Path(entry['path']).exists())

    def test_copy(self):
        """Tests 'copy' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/existing.tmp", isdir=False)]
        cases = [dict(src="root/self.tmp", dst="root",
                      overwrite=True, success=True),
                 dict(src="root/self.tmp", dst="root",
                      overwrite=False, success=False),
                 dict(src="root/foo/from_subfolder.tmp", dst="root",
                      overwrite=False, success=True),
                 dict(src="root/foo/existing.tmp", dst="root",
                      overwrite=True, success=True),
                 dict(src="root/foo/existing.tmp", dst="root",
                      overwrite=False, success=False)]
        with TemporaryFoldersManager.from_list(test_dirs, True) as temp_manager:
            for case in cases:
                temp_manager.track_file(case['src'])
                manipulator = FileManipulator(case['src'])
                if case['success']:
                    another = manipulator.copy(case['dst'], case['overwrite'])
                    self.assertTrue(another.exists())
                    dst_path = os.path.join(case['dst'], manipulator.target())
                    self.assertEqual(os.path.abspath(dst_path).lower(),
                                     str(another).lower())
                else:
                    with self.assertRaises(EFailedToManipulate):
                        manipulator.copy(case['dst'], case['overwrite'])

    def test_move(self):
        """Tests 'move' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/existing.tmp", isdir=False)]
        cases = [dict(src="root/self.tmp", dst="root/self_renamed.tmp",
                      success=True),
                 dict(src="root/to_subfolder.tmp", dst="root/foo/from_root.tmp",
                      success=True),
                 dict(src="root/failed.tmp", dst="root/existing.tmp",
                      success=False),
                 dict(src="root/bar/to_root.tmp", dst="root/from_subfolder.tmp",
                      success=True)]
        with TemporaryFoldersManager.from_list(test_dirs, True) as temp_manager:
            for case in cases:
                temp_manager.track_file(case['src'])
                manipulator = FileManipulator(case['src'])
                if case['success']:
                    manipulator.move(case['dst'])
                    self.assertTrue(manipulator.exists())
                    self.assertFalse(Path(case['src']).exists())
                    self.assertEqual(os.path.abspath(case['dst']).lower(),
                                     str(manipulator).lower())
                else:
                    with self.assertRaises(EFailedToManipulate):
                        manipulator.move(case['dst'])

    def test_remove(self):
        """Tests 'remove' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/existing.tmp", isdir=False)]
        with TemporaryFoldersManager.from_list(test_dirs, True):
            manipulator = FileManipulator(test_dirs[1]['path'])
            manipulator.remove()
            self.assertFalse(manipulator.exists())
            with self.assertRaises(EFailedToManipulate):
                manipulator.remove()

    def test_pure_name(self):
        """Tests 'pure_name' method.
        """
        cases = [dict(path="root/simple.tmp",
                      name="simple"),
                 dict(path="root/foo/simple.tmp",
                      name="simple"),
                 dict(path="root/suffix.tmp.tmp",
                      name="suffix"),
                 dict(path="root/suffix.dmp.tmp",
                      name="suffix"),
                 dict(path="root/_complex_suffix__.dmp.tmp",
                      name="_complex_suffix__")]
        with TemporaryFoldersManager() as temp_manager:
            for case in cases:
                temp_manager.track_file(case['path'])
                manipulator = FileManipulator(case['path'])
                self.assertEqual(manipulator.pure_name(), case['name'])

    def test_extension(self):
        """Tests 'extension' method.
        """
        cases = [dict(path="root/simple.tmp", ext="tmp"),
                 dict(path="root/suffix.temp.tmp", ext="tmp"),
                 dict(path="root/foo/simple.tmp", ext="tmp"),
                 dict(path="root/foo/suffix.temp.tmp", ext="tmp"),
                 dict(path="root/long.temp", ext="temp")]
        with TemporaryFoldersManager() as temp_manager:
            for case in cases:
                temp_manager.track_file(case['path'])
                manipulator = FileManipulator(case['path'])
                self.assertEqual(manipulator.extension(), case['ext'])
