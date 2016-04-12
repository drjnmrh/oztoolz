"""
    Defines tools for unit testing, e.g. resource management and e.t.c.
        Author: O.Z.
"""

# imports


import os

from errors import *


# API


class ResourceNode(object):

    def __init__(self, resource_name):
        self.__resource_name = resource_name

    def __str__(self):
        raise NotImplementedError()

    def name(self):
        return self.__resource_name

    def child(self, child_name):
        raise NotImplementedError()


class ResourceSuit(ResourceNode):

    def __init__(self, suit_name):
        super().__init__(suit_name)

        self.__children = {}

    def __str__(self):
        result_string = ""
        for k, v in self.__children:
            result_string = result_string + "[" + k + "]\n" + str(v) + "\n"

        return result_string

    def child(self, child_name):
        if not child_name in seld.__children:
            raise ENoSuchChild(child_name)

        return self.__children[child_name]

    def add_child(self, child_resource):
        self.__children[child_resource.name()] = child_resource


class ResourceText(ResourceNode):

    def __init__(self, resource_name, text_strings):
        super().__init__(resource_name)

        self.__text_strings = text_strings

    def __str__(self):
        return self.__text_strings

    @staticmethod
    def load_from_file(resource_name, file_path):
        if not os.path.exists(file_path):
            raise EFileDoesntExist(file_path)

        text_strings = ""
        with open(file_path, "r") as file_object:
            for line in file_object:
                text_strings = text_strings + line

        return ResourceText(resource_name, text_strings)


class ResourceManager(object):

    def __init__(self, resources_path):
        pass


# testing


def main():
    """Can be used for testing.
    """
    pass


if __name__ == '__main__':
    main()
