"""
    Defines exception classes for the test framework module (testfwk).
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
        super().__init__("testfwk.EFileDoesntExist error: file '" +
                         file_name + "' doesn't exist.")


class EFailedToReview(EUnknown):
    """An exception, which is raised when the code reviewer failed to
    do his job due to the error.
    """

    def __init__(self, reason_string):
        super().__init__("testfwk.EFailedToReview error: " + reason_string +
                         ".")


class ENoSuchChild(EUnknown):
    """An exception, which is raised when there's an attempt to access
    non-existing child.
    """

    def __init__(self, child_name):
        super().__init__("testfwk.ENoSuchChild error: " + child_name +
                         "doesn't exist.")


# testing


def main():
    """Performs testing and e.t.c.
    """
    pass


if __name__ == "__main__":
    main()
