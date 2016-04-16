"""
    Defines tools for unit testing, e.g. resource management and e.t.c.
        Author: O.Z.
"""

# imports


import os
import re

from pathlib import Path

from .errors import EFailedToInit
from .errors import EFileDoesntExist
from .errors import ENoSuchChild
from .errors import EUnknown

from oztoolz.ioutils import compare_paths
from oztoolz.ioutils import extract_file_name


# API


class ResourceNode(object):
    """The base class for loadable resources.

    If the resource can be represented by the string, the __str__ method
    should be overriden.

    Attributes:
        __resource_name: the name of the resource
    Properties:
        name: the name of the resource
    """

    def __init__(self, resource_name):
        self.__resource_name = resource_name

    def __str__(self):
        raise NotImplementedError()

    @property
    def name(self):
        """Gets the name of the resource.

        Returns:
            a string, containing the name of the resource.
        Raises:
            nothing.
        """
        return self.__resource_name

    def child(self, child_name):
        """Gets the child resource by the name.
        """
        raise NotImplementedError()

    def children_number(self):
        """Returns number of the children.
        """
        raise NotImplementedError()

    def load(self, file_path):
        """Loads the resource from the disc, using the path to the file.
        """
        raise NotImplementedError()


class ResourceSuit(ResourceNode):
    """The set of the resource nodes.

    Attributes:
        __children: the table of the resources, paired with their names.
    """

    def __init__(self, suit_name):
        super().__init__(suit_name)

        self.__children = {}

    def __str__(self):
        result_string = ""
        for key, value in self.__children:
            result_string = (result_string + "[" + key + "]\n" +
                             str(value) + "\n")

        return result_string

    def load(self, file_path):
        """Not applicable for the suit.
        """
        raise NotImplementedError()

    def child(self, child_name):
        """Gets the child resource by the given name.

        Args:
            child_name: a string, containing the name of the child resource.
        Returns:
            the child resource object.
        Raises:
            ENoSuchChild if the child with such name wasn't found.
        """
        if not child_name in self.__children:
            raise ENoSuchChild(child_name)

        return self.__children[child_name]

    def children_number(self):
        """Returns number of the children.
        """
        return len(self.__children)

    def add_child(self, child_resource):
        """Adds the child resource to the suit.

        Rewrites the child resource if already has a child resource with such
        name.

        Args:
            child_resource: the child resource object.
        Returns:
            nothing.
        Raises:
            nothing.
        """
        self.__children[child_resource.name] = child_resource


class ResourceText(ResourceNode):
    """The text resource.

    Can be loaded from the .txt file with the _lines suffix.

    Args:
        __text_strings: a string, containing the text.
    """

    def __init__(self, resource_name, text_strings):
        super().__init__(resource_name)

        self.__text_strings = text_strings

    def __str__(self):
        return self.__text_strings

    def child(self, child_name):
        """Not applicable.
        """
        raise NotImplementedError()

    def children_number(self):
        """Not applicable.
        """
        raise NotImplementedError()

    def load(self, file_path):
        """Creates a new text resource from the given file.

        Only .txt files with _lines suffix are suitable for loading. If the
        resource can't be loaded the None value would be returned.

        The name of the resource would be the name of the file minus _lines.txt
        suffix.

        Args:
            file_path: a string, containing the path to the resource file.
        Returns:
            the loaded text resource object if it is possible to load, None
            otherwise.
        Raises:
            nothing.
        """
        try:
            file_object = Path(file_path)
            if not file_object.is_file():
                return None

            if file_object.suffix != '.txt':
                return None

            file_name = extract_file_name(file_path)
            if file_name == "":
                return None

            if re.compile("(.*)(?=_lines.txt)").match(file_name) is None:
                return None

            return ResourceText.load_from_file(file_name[:-10], file_path)
        except (EUnknown, OSError, ValueError):
            return None

    @staticmethod
    def load_from_file(resource_name, file_path):
        """Creates the new text resource with the specified name and content,
        loaded from the file with the given file path.

        Args:
            resource_name: the name of the resource.
            file_path: a string, containing the path to the file.
        Returns:
            a text resource object.
        Raises:
            EFileDoesntExist if the file with the content doesn't exist.
            OSError, ValueError.
        """
        if not os.path.exists(file_path):
            raise EFileDoesntExist(file_path)

        text_strings = ""
        with open(file_path, "r") as file_object:
            for line in file_object:
                text_strings = text_strings + line

        return ResourceText(resource_name, text_strings)

    @staticmethod
    def prototype():
        """Returns dummy text resource object.
        """
        return ResourceText("ResourceText prototype", "")


class ResourcesLoader(object):
    """The factory object, which creates a specific resource object, using
    the specified file.

    It has a number of prototypes. Each prototype is asked to load the
    resource from the file. The first non-None result is returned.

    Attributes:
        __prototypes: the list of the prototypes.
    """

    def __init__(self):
        self.__prototypes = [ResourceText.prototype()]

    def load(self, file_path):
        """Tries to load a resource from the specified file.

        The first non-None result of the 'load' method of the prototype, is
        returned by the method.

        Args:
            file_path: a string, containing the path to the resource file.
        Returns:
            a resource object, loaded from the file if any of the prototypes is
            suitable for loading, None otherwise.
        Raises:
            nothing.
        """
        for prototype in self.__prototypes:
            result = prototype.load(file_path)
            if not result is None:
                return result
        return None

    def add_prototype(self, prototype):
        """Adds a prototype to the prototypes list.

        The prototype should have no-throw method 'load'.

        Args:
            prototype: a prototype object to add.
        Returns:
            nothing.
        Raises:
            nothing.
        """
        self.__prototypes.append(prototype)

    @property
    def prototypes(self):
        """Gets the prototypes list.
        """
        return self.__prototypes


class ResourceManager(object):
    """The manager of the resources, which loads them from the given directory
    and groups them into suits.

    The suits correspond to the folders, the resources correspond to the files.

    Attributes:
        __root_resource: the root resource, which is a resource suit.
        __loader: the resource loader.
    """

    def __init__(self, resources_path, resources_loader=ResourcesLoader()):
        self.__root_resource = ResourceSuit("root")
        self.__loader = resources_loader

        self.reload(resources_path)

    def reload(self, resources_path, resources_loader=None):
        """Loads resources from the given folder.

        Uses its own loader if the given one is None.

        Args:
            resources_path: a string, containing the path to the resources.
            resources_loader: a loader of the resources; can be None.
        Returns:
            nothing.
        Raises:
            EFailedToInit.
        """
        self.__root_resource = ResourceSuit("root")
        if not resources_loader is None:
            self.__loader = resources_loader

        try:
            resources_folder = Path(resources_path)
            if not resources_folder.exists():
                raise EFailedToInit("the resources path doesn't exist (" +
                                    resources_path + ")")

            if not resources_folder.is_dir():
                raise EFailedToInit("given path is not a folder (" +
                                    resources_path + ")")

            files_in_folder = list(resources_folder.glob("**/*.*"))

            for file_object in files_in_folder:
                resource = self.__loader.load(str(file_object))
                if resource is None:
                    continue

                if compare_paths(str(file_object.parent), resources_path):
                    self.__root_resource.add_child(resource)
                    continue

                cur_suit = self.__root_resource
                rel_folder = file_object.parent.relative_to(resources_path)
                parts = rel_folder.parts
                for part in parts:
                    try:
                        cur_suit = cur_suit.child(part)
                    except ENoSuchChild:
                        cur_suit.add_child(ResourceSuit(part))
                        cur_suit = cur_suit.child(part)
                cur_suit.add_child(resource)
        except (OSError, ValueError) as err:
            raise EFailedToInit("unexpected exception [" + str(err) + "]")
        except ENoSuchChild as err:
            raise EFailedToInit("logic error - caught an exception [" +
                                str(err) + "]")


    @property
    def root(self):
        """Gets the root resource.
        """
        return self.__root_resource


# testing


def main():
    """Can be used for testing.
    """
    pass


if __name__ == '__main__':
    main()
