"""
    Defines exception classes for the streams tools module (streams).
        Author: O.Z.
"""


# classes


class EUnknown(Exception):
    """General purpose exception.

    Used as the base class for the more specific exceptions.

    Attributes:
        __error_message: a string, which contains description of the error.
    """

    def __init__(self, error_message):
        super().__init__()
        self.__error_message = error_message

    def __str__(self):
        return repr(self.__error_message)


class EFileDoesntExist(EUnknown):
    """An exception, which is raised when the specific file doesn't exist.
    """

    def __init__(self, file_name):
        super().__init__("streams.EFileDoesntExist error: file '" +
                         file_name + "' doesn't exist.")


class EFailedToInitialize(EUnknown):
    """An exception, which is raised when the stream object can't be
    initialized.
    """

    def __init__(self, reason_message):
        super().__init__("streams.EFailedToInitialize error: " +
                         reason_message + ".")


class EFailedToWriteToFile(EUnknown):
    """An exception, which is raised when the stream object can't write
    characters into the file.
    """

    def __init__(self, reason_message):
        super().__init__("streams.EFailedToWriteToFile error: " +
                         reason_message + ".")


# testing


def main():
    """Performs testing and e.t.c.
    """
    pass

if __name__ == '__main__':
    main()
