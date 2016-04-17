"""
    Defines basic streams classes for the 'streams' module.
        Author: O.Z.
"""

# imports


import sys
import os

from .errors import EFileDoesntExist
from .errors import EFailedToInitialize
from .errors import EFailedToWriteToFile

from ..ioutils import safe_write as write


# globals


__all__ = ['OutputStream', 'StdoutStream', 'FileOutStream']


# classes


class OutputStream(object):
    """The base class for the Output Streams.

    Derived classes should implement '_write' method with one string parameter.

    Attributes:
        __last_string: saved last written string.
        __aligners_stack: a stack of aligners, which are applied to the string.
    """

    def __init__(self):
        self.__last_string = ""
        self.__aligners_stack = []

    # private methods

    def __apply_aligners(self, string):
        """Applies aligners from the stack to the given string and returns the
        result.

        Args:
            string: the string to align.
        Returns:
            the aligned string.
        Raises:
            nothing.
        """

        aligned_string = string
        for aligner in self.__aligners_stack:
            aligned_string = aligner.prototype(aligned_string)

        return aligned_string

    # protected methods

    def _write(self, string):
        """Should be overriden by the concrete output streams to print given
        string.

        Args:
            string: the passed string to print.
        Returns:
            nothing.
        Raises:
            NotImplementedError: since the method should be overriden
        """
        raise NotImplementedError()

    # public methods

    def push_aligner(self, aligner):
        """Pushes aligner to the stack.

        Args:
            aligner: an aligner to push to the stack.
        Returns:
            nothing.
        Raises:
            nothing.
        """
        self.__aligners_stack.insert(0, aligner)

    def pop_aligner(self):
        """Pops an aligner from the top of the aligners stack.

        Returns:
            nothing.
        Raises:
            nothing.
        """
        self.__aligners_stack.pop()

    def write(self, string):
        """Saves the passed string as the last passed string and calls virtual
        _write method to print the aligned string.

        Applies aligners from the stack to the given string.

        Args:
            string: the passed string to save.
        Returns:
            nothing.
        Raises:
            depends on what exceptions are risen by the overriden _write method.
        """
        self._write(self.__apply_aligners(string))

        self.__last_string = string

    def append(self, string):
        """Appends the passed string as a new line to the buffer.

        Args:
            string: the passed string to append.
        Returns:
            nothing.
        Raises:
            depends on which exceptions are raised in the 'write' method.
        """
        self.write('\n')
        self.write(string)


class DummyOutStream(OutputStream):
    """An output stream, which doesn't write anything.
    """
    def __init__(self):
        super().__init__()

    def _write(self, string):
        """Does nothing.
        """
        return string


class StdoutStream(OutputStream):
    """An output stream, which writes characters to the stdout.
    """
    def __init__(self):
        super().__init__()

    def _write(self, string):
        """Writes passed string to the stdout stream.

        Args:
            string: a string to write.
        Returns:
            nothing.
        Raises:
            nothing.
        """

        write(sys.stdout, str(string))


class FileOutStream(OutputStream):
    """An output stream, which writes characters to the specified file.

    The stream creates the file if it doesn't exist or clears it otherwise.
    Constructor might raise EFailedToInitialize exception.

    Attributes:
        __file_name: the absolute path string to the specified file.
    """
    def __init__(self, file_name):
        super().__init__()

        self.__file_name = ""

        try:

            open(file_name, "w").close()

            self.__file_name = os.path.abspath(file_name)

        except OSError:
            raise EFailedToInitialize("OSError while working with " +
                                      file_name)

    def _write(self, string):
        """Writes the given string to the file.

        Args:
            string: the string to write.
        Returns:
            nothing.
        Raises:
            EFileDoesntExist: exception, if the given file doesn't exist.
            EFailedToWriteToFile: if failed to open and write to the file.
        """

        try:

            if not os.path.exists(self.__file_name):
                raise EFileDoesntExist(self.__file_name)

            with open(self.__file_name, 'a') as file_object:
                file_object.write(str(string))

        except OSError:
            raise EFailedToWriteToFile("OSError while working with " +
                                       self.__file_name)
        except EFileDoesntExist:
            raise


def main():
    """The main method, which is called if the current scripts was executed
    explicitly.
    """
    pass


if __name__ == '__main__':
    main()
