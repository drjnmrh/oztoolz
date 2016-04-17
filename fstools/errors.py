"""
    Defines exception classes for the file system tools module (fstools).
        Author: O.Z.
        Version: 0.9
"""


# classes


class EUnknown(Exception):
    """General purpose exception.

    Used as the base class for more specific exceptions.

    Attributes:
        _msg: a string, which describes an exception for the user
    """

    def __init__(self, msg):
        super().__init__()
        self._msg = msg

    def __str__(self):
        """Gets an exception message.
        Returns:
            exception message string.
        """
        return self._msg


class EPathDoesntExist(EUnknown):
    """An exception, which is raised when the specified path doesn't exist.
    """

    def __init__(self, path):
        super().__init__("FS ERROR: path doesn't exist [" + path + "]")


class EFolderDoesntExist(EPathDoesntExist):
    """An exception, which is raised when the specified folder doesn't exist.
    """

    def __init__(self, folderPath):
        super().__init__(folderPath + "(folder)")


class EFileDoesntExist(EPathDoesntExist):
    """An exception, which is raised when the specified file doesn't exist.
    """

    def __init__(self, filePath):
        super().__init__(filePath + "(file)")


# testing the module


def main():
    """Can be used for testing.
    """
    pass


if __name__ == '__main__':
    main()
