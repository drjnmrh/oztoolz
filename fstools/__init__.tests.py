"""
    Defines different unit test case classes for fstools package.
        Author: O.Z.
"""

# imports

import os
import unittest

from pathlib import Path

from oztoolz.fstools import FileManipulator, FolderManipulator
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

class TestFolderManipulator(unittest.TestCase):
    """Tests FolderManipulator class.
    """
    def test_create(self):
        """Tests 'create' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/foo", isdir=True)]
        cases = [dict(path="root/bar", force=False, success=True),
                 dict(path="root/foo/bar", force=False, success=True),
                 dict(path="root/baz/bar", force=True, success=True),
                 dict(path="root/zip/foo", force=False, success=False)]
        with TemporaryFoldersManager.from_list(test_dirs, True):
            for case in cases:
                if case['success']:
                    manipulator = FolderManipulator.create(case['path'],
                                                           case['force'])
                    self.assertTrue(manipulator.exists())
                else:
                    with self.assertRaises(EFailedToInitialize):
                        FolderManipulator.create(case['path'], case['force'])

    def test_temp(self):
        """Tests 'temp' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/foo", isdir=True),
                     dict(path="root/bar", isdir=True)]
        cases = [dict(path="root/temp", success=True),
                 dict(path="root/bar", success=True),
                 dict(path="root/foo/temp", success=True),
                 dict(path="root/foo/bar/temp", success=False)]
        with TemporaryFoldersManager.from_list(test_dirs, True):
            for case in cases:
                if case['success']:
                    with FolderManipulator.temp(case['path']) as manipulator:
                        self.assertTrue(manipulator.exists())
                        self.assertTrue(os.path.exists(case['path']))
                    self.assertFalse(os.path.exists(case['path']))
                else:
                    with self.assertRaises(EFailedToInitialize):
                        FolderManipulator.temp(case['path'])

    def test_copy(self):
        """Tests 'copy' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/foo", isdir=True),
                     dict(path="root/foo/temp.tmp", isdir=False),
                     dict(path="root/foo/bar/temp.tmp", isdir=False),
                     dict(path="root/bar", isdir=True),
                     dict(path="root/temp", isdir=True),
                     dict(path="root/zip/temp/temp.tmp", isdir=False),
                     dict(path="root/abc/temp", isdir=True),
                     dict(path="root/qwe/temp", isdir=True)]
        cases = [dict(src="root/foo/bar", dst="root/baz",
                      success=True, overwrite=False),
                 dict(src="root/bar", dst="root/zip",
                      success=True, overwrite=True),
                 dict(src="root/zip/temp", dst="root",
                      success=True, overwrite=True),
                 dict(src="root/abc/temp", dst="root/qwe",
                      success=False, overwrite=False)]
        with TemporaryFoldersManager.from_list(test_dirs, True):
            for case in cases:
                manipulator = FolderManipulator(case['src'])
                if case['success']:
                    copy_man = manipulator.copy(case['dst'], case['overwrite'])
                    self.assertTrue(copy_man.exists())
                    dst_path = os.path.join(case['dst'], manipulator.target())
                    self.assertEqual(str(copy_man).lower(),
                                     os.path.abspath(dst_path).lower())
                else:
                    with self.assertRaises(EFailedToManipulate):
                        manipulator.copy(case['dst'], case['overwrite'])

    def test_move(self):
        """Tests 'move' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/with_content", isdir=True),
                     dict(path="root/with_content/foo", isdir=True),
                     dict(path="root/with_content/bar", isdir=True),
                     dict(path="root/with_content/temp.tmp", isdir=False),
                     dict(path="root/empty", isdir=True),
                     dict(path="root/for_moved", isdir=True),
                     dict(path="root/failed_src", isdir=True),
                     dict(path="root/for_moved/failed_dst", isdir=True)]
        cases = [dict(src="root/with_content", dst="root/for_moved/content",
                      success=True),
                 dict(src="root/empty", dst="root/for_moved/moved_empty",
                      success=True),
                 dict(src="root/failed_src", dst="root/for_moved/failed_dst",
                      success=False)]
        with TemporaryFoldersManager.from_list(test_dirs, True):
            for case in cases:
                manipulator = FolderManipulator(case['src'])
                if case['success']:
                    manipulator.move(case['dst'])
                    self.assertTrue(manipulator.exists())
                    self.assertEqual(os.path.abspath(case['dst']).lower(),
                                     str(manipulator).lower())
                else:
                    with self.assertRaises(EFailedToManipulate):
                        manipulator.move(case['dst'])

    def test_remove(self):
        """Tests 'remove' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/with_content", isdir=True),
                     dict(path="root/with_content/foo", isdir=True),
                     dict(path="root/with_content/bar", isdir=True),
                     dict(path="root/with_content/foo/temp.tmp", isdir=False),
                     dict(path="root/empty", isdir=True)]
        cases = [dict(src="root/with_content", success=True),
                 dict(src="root/empty", success=True)]
        with TemporaryFoldersManager.from_list(test_dirs, True):
            for case in cases:
                manipulator = FolderManipulator(case['src'])
                if case['success']:
                    manipulator.remove()
                    self.assertFalse(manipulator.exists())
                else:
                    with self.assertRaises(EFailedToManipulate):
                        manipulator.remove()

    def test_is_empty(self):
        """Tests 'is_empty' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/with_files/temp1.tmp", isdir=False),
                     dict(path="root/with_files/temp2.tmp", isdir=False),
                     dict(path="root/with_folders/temp1", isdir=True),
                     dict(path="root/with_folders/temp2", isdir=True),
                     dict(path="root/with_content/foo", isdir=True),
                     dict(path="root/with_content/bar/temp.tmp", isdir=False),
                     dict(path="root/empty", isdir=True)]
        cases = [dict(src="root/with_files", res=False),
                 dict(src="root/with_folders", res=False),
                 dict(src="root/with_content", res=False),
                 dict(src="root/empty", res=True)]
        with TemporaryFoldersManager.from_list(test_dirs, True):
            for case in cases:
                manipulator = FolderManipulator(case['src'])
                self.assertEqual(case['res'], manipulator.is_empty())

    def test_list(self):
        """Tests 'list' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/empty", isdir=True),
                     dict(path="root/with_content", isdir=True),
                     dict(path="root/with_content/dirAA", isdir=True),
                     dict(path="root/with_content/dirAB", isdir=True),
                     dict(path="root/with_content/dirBA", isdir=True),
                     dict(path="root/with_content/dirBB", isdir=True),
                     dict(path="root/with_content/AA.tmp", isdir=False),
                     dict(path="root/with_content/AB.tmp", isdir=False),
                     dict(path="root/with_content/BA.tmp", isdir=False),
                     dict(path="root/with_content/BB.tmp", isdir=False),
                     dict(path="root/with_content/dirAA/sub", isdir=True),
                     dict(path="root/with_content/dirBB/temp.tmp", isdir=False)]
        cases = [dict(path="root/empty", res=[]),
                 dict(path="root/with_content",
                      res=[dict(path="root/with_content/dirAA", isdir=True),
                           dict(path="root/with_content/dirAB", isdir=True),
                           dict(path="root/with_content/dirBA", isdir=True),
                           dict(path="root/with_content/dirBB", isdir=True),
                           dict(path="root/with_content/AA.tmp", isdir=False),
                           dict(path="root/with_content/AB.tmp", isdir=False),
                           dict(path="root/with_content/BA.tmp", isdir=False),
                           dict(path="root/with_content/BB.tmp", isdir=False)])]
        with TemporaryFoldersManager.from_list(test_dirs, True):
            for case in cases:
                manipulator = FolderManipulator(case['path'])
                result = manipulator.list()
                self.assertEqual(len(result), len(case['res']))
                for i in range(0, len(result)):
                    self.assertTrue(result[i].is_same(case['res'][i]['path']))
                    self.assertEqual(isinstance(result[i], FolderManipulator),
                                     case['res'][i]['isdir'])

    def test_files(self):
        """Tests 'files' method.
        """
        test_dirs = [dict(path="root", isdir=True),
                     dict(path="root/empty", isdir=True),
                     dict(path="root/only_files/AA.tmp", isdir=False),
                     dict(path="root/only_files/BA.tmp", isdir=False),
                     dict(path="root/only_files/AB.tmp", isdir=False),
                     dict(path="root/only_folders/foo", isdir=True),
                     dict(path="root/only_folders/bar", isdir=True),
                     dict(path="root/mixed/temp.tmp", isdir=False),
                     dict(path="root/mixed/foo/temp.tmp", isdir=False),
                     dict(path="root/mixed/bar", isdir=True),
                     dict(path="root/mixed/baz/AA.tmp", isdir=False)]
        cases = [dict(path="root/empty",
                      res=[],
                      recoursive=False),
                 dict(path="root/only_files",
                      res=["root/only_files/AA.tmp",
                           "root/only_files/AB.tmp",
                           "root/only_files/BA.tmp"],
                      recoursive=False),
                 dict(path="root/only_folders",
                      res=[],
                      recoursive=False),
                 dict(path="root/mixed",
                      res=["root/mixed/baz/AA.tmp",
                           "root/mixed/foo/temp.tmp",
                           "root/mixed/temp.tmp"],
                      recoursive=True),
                 dict(path="root/mixed",
                      res=["root/mixed/temp.tmp"],
                      recoursive=False)]
        with TemporaryFoldersManager.from_list(test_dirs, True):
            for case in cases:
                manipulator = FolderManipulator(case['path'])
                result = manipulator.files(case['recoursive'])
                self.assertEqual(len(result), len(case['res']))
                for i in range(0, len(result)):
                    self.assertTrue(result[i].is_same(case['res'][i]))
                    self.assertTrue(isinstance(result[i], FileManipulator))
