"""
    Defines different unit test case classes for testfwk.utesting module.
        Author: O.Z.
"""


# imports


import os
import sys
import unittest

if __name__ == '__main__':
    from oztoolz.ioutils import TemporaryFoldersManager

    from oztoolz.testfwk.utesting import has_module_tests
    from oztoolz.testfwk.utesting import ResourceText
    from oztoolz.testfwk.utesting import ResourceManager
else:
    from ...ioutils import TemporaryFoldersManager

    from . import has_module_tests
    from . import ResourceText
    from . import ResourceManager


# test cases


class TestUTestingMethods(unittest.TestCase):
    """Defines tests for the modules API methods
    """

    def test_has_module_tests(self):
        """Tests the 'has_module_tests' method.
        """
        modules = [dict(name='simple', path='foo', has=True),
                   dict(name='notests', path='foo', has=False),
                   dict(name='simple_tests', path='foo', has=False),
                   dict(name='another', path='foo/bar', has=True),
                   dict(name='another_tests', path='foo/baz', has=False)]

        with TemporaryFoldersManager() as temp_manager:
            for module in modules:
                module_path = os.path.join(module['path'], module['name'])
                temp_manager.track_file(module_path + '.py')
                if module['has']:
                    temp_manager.track_file(module_path + '.tests.py')

            had_errors = False
            for module in modules:
                module_path = os.path.join(module['path'],
                                           (module['name'] + '.py'))
                try:
                    self.assertEqual(has_module_tests(module_path, sys.stdout),
                                     module['has'])
                except AssertionError:
                    print('failed on: ' + module_path)
                    had_errors = True

            self.assertFalse(had_errors)

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


class TestResourcesManager(unittest.TestCase):
    """Implements tests for the ResourceManager class.
    """

    def test_reload(self):
        """Tests the 'reload' method of the ResourceManager class.
        """
        resources = [dict(path='foo/text_lines.txt', # 0 +
                          text='lolz'),
                     dict(path='not_resource.tmp', # 1 -
                          text='dump'),
                     dict(path='foo/bar/text_lines.txt', # 2 +
                          text='double lolz'),
                     dict(path='foo/baz/another_lines.txt', # 3 +
                          text='triple lolz'),
                     dict(path='foo/bar/not_resource.tmp', # 4 -
                          text='dump')]

        resources_tree = dict(name='foo',
                              id=-1,
                              children=[dict(name='bar',
                                             id=-1,
                                             children=[dict(name='text',
                                                            id=2,
                                                            children=[])]),
                                        dict(name='baz',
                                             id=-1,
                                             children=[dict(name='another',
                                                            id=3,
                                                            children=[])]),
                                        dict(name='text',
                                             id=0,
                                             children=[])])

        with TemporaryFoldersManager() as temp_manager:

            for resource in resources:
                temp_manager.track_file(resource['path'])
                with open(resource['path'], "w") as file_object:
                    file_object.write(resource['text'])

            res_manager = ResourceManager()
            res_manager.reload()

            nodes_to_bypass = [dict(ref=resources_tree, res=res_manager.root)]
            while len(nodes_to_bypass) > 0:
                cur_node = nodes_to_bypass[0]
                nodes_to_bypass.pop(0)

                child = cur_node['res'].child(cur_node['ref']['name'])

                self.assertEqual(cur_node['ref']['name'],
                                 child.name)

                if cur_node['ref']['id'] < 0:
                    self.assertEqual(len(cur_node['ref']['children']),
                                     child.children_number())
                    for node_child in cur_node['ref']['children']:
                        nodes_to_bypass.append(dict(ref=node_child, res=child))
                else:
                    self.assertEqual(resources[cur_node['ref']['id']]['text'],
                                     str(child))


# testing


def main():
    """Performs unit testing.
    """
    unittest.main()


if __name__ == '__main__':
    main()
