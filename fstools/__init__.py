"""
    Defines file system and data manipulator classes.
        Author: O.Z.
"""


# imports


import os

from pathlib import Path

from oztoolz.fstools.errors import EFailedToInitialize
from oztoolz.fstools.errors import EFailedToManipulate
from oztoolz.fstools.errors import EPathDoesntExist


__all__ = ['PathManipulator']


# API


class PathManipulator:
    """Basic path manipulator class.

    The manipulator has a name and a corresponding pathlib object.
    Also the target object (which is pointed by the path) can be acquired.
    Derived classes should implement some specific methods, like copy, move and
    remove. These methods should raise EFailedToManipulate exception in case of
    errors.

    Attriubtes:
        self.__path_obj: a corresponding pathlib object.
        self.__notm_path: a string, containing absolute full path.
        self.__name: the name of the manipulator
    """

    def __init__(self, path, manipulator_name="Path Manipulator"):
        try:
            self.__path_obj = Path(path)
            if not self.__path_obj.exists():
                raise EPathDoesntExist(str(self.__path_obj))
            self.__norm_path = os.path.abspath(str(path)).lower()

            self.__name = manipulator_name
        except (OSError, ValueError) as err:
            raise EFailedToInitialize(manipulator_name, str(err))
        except EPathDoesntExist as err:
            raise EFailedToInitialize(manipulator_name, str(err))

    def __str__(self):
        return self.__norm_path

    # properties

    @property
    def normalized_path(self):
        """Gets an absolute full path.

        Returns:
            a string, containing normalized path.
        Raises:
            nothing.
        """
        return self.__norm_path

    @property
    def name(self):
        """Gets the name of the manipulator.

        Returns:
            a string, containing the name of the manipulator.
        Raises:
            nothing.
        """
        return self.__name

    @property
    def path(self):
        """Gets a corresponding pathlib Path object.

        Returns:
            a pathlib.Path object.
        Raises:
            nothing.
        """
        return self.__path_obj

    # public API

    def exists(self):
        """Checks if the path exists.

        Returns:
            True if the path exists, False otherwise.
        Raises:
            EFailedToManipulate.
        """
        try:
            return os.path.exists(self.normalized_path)
        except (OSError, ValueError) as err:
            raise EFailedToManipulate(self.name, "exists", str(err))

    def target(self):
        """Gets the target object, pointed by the path.

        Returns:
            a string, containing the target.
        Raises:
            EFailedToManipulate.
        """
        try:
            if self.path.parent is None:
                return str(self.path)

            return str(self.path.relative_to(str(self.path.parent)))
        except (OSError, ValueError) as err:
            raise EFailedToManipulate(self.name, "target", str(err))

    # abstract API

    def copy(self, destination):
        """An abstract method, which copies the target object to the
        destination path.

        Args:
            destination: a convertable to string object, which specifies the
                         destination path.
        Returns:
            nothing.
        Raises:
            EFailedToManipulate, NotImplementedError.
        """
        raise NotImplementedError()

    def move(self, destination):
        """An abstract method, which moves the target object to the specified
        destination.

        Args:
            destination: a convertable to string object, which specifies the
                         destination path.
        Returns:
            nothing.
        Raises:
            EFailedToManipulate, NotImplementedError.
        """
        raise NotImplementedError()

    def remove(self):
        """An abstract method, which removes the target object.

        Returns:
            nothing.
        Raises:
            EFailedToManipulate, NotImplementedError.
        """
        raise NotImplementedError()


# testing


def main():
    """Can be used for testing.
    """
    pass


if __name__ == '__main__':
    main()
