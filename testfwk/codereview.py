"""
    Defines classes and tools, which are used for automatic code review.
        Author: O.Z.

    The base class for code reviewers is CodeReviewer. Derived classes are:
    PyLintCodeReviewer.

    Also contains 'get_default_reviewer' method, which can be used to get a
    default code reviewer object.

    Classes and methods use exceptions from 'errors' module.
"""


# imports


import io
import os

from subprocess import Popen
from subprocess import PIPE
from subprocess import SubprocessError

from .errors import EUnknown
from .errors import EFileDoesntExist
from .errors import EFailedToReview

from oztoolz.streams.aligners import CenterAligner as Center
from oztoolz.streams.aligners import RightAligner as Right


# classes


class CodeReviewer(object):
    """Base class for automatic code reviewers.

    Concrete reviewers should override _execute_review and _name methods.
    The _execute_review performs the review and writes results into the
    out_stream. The _name method returns readable name of the code reviewer.

    Attributes:
        __out_stream: an object with 'append' and 'write' methods, which is
                      used for strings output.
    """

    def __init__(self, out_stream):
        self.__out_stream = out_stream

    # protected methods

    def _execute_review(self, file_path, out_stream):
        """Protected method, which should be implemented by the concrete code
        reviewers to run a review.

        This method should run code reviewer for the specified file and reports
        into the given output stream object.

        Derived classes can use EFailedToReview exception in case of errors.

        Args:
            file_path: a string path to the file to review.
            out_stream: an output stream object to write report to.
        Returns:
            nothing.
        Raises:
            NotImplementedError: since CodeReviewer is an abstract class.
        """
        raise NotImplementedError()

    def _name(self):
        """Protected method, which should be implemented by the concrete code
        reviewers to get a readable name of the reviewer.

        Returns:
            a string, which contains readable name of the reviewer.
        Raises:
            NotImplementedError: since CodeReviewer is an abstract class.
        """
        raise NotImplementedError()

    # public methods

    def attach(self, out_stream):
        """Changes output stream object to write report to.

        Args:
            out_stream: an output stream object to write report to.
        Returns:
            nothing.
        Raises:
            nothing.
        """
        self.__out_stream = out_stream

    def review(self, file_path):
        """Runs a code review for the given source file.

        This method uses specified in the constructor of the reviewer output
        stream object to log out the review report.

        Args:
            file_path: a string path to the source file to review.
        Returns:
            nothing.
        Raises:
            EFileDoesntExist: if the specified source file doesn't exist.
            EFailedToReview: if failed to perform the review process.
        """
        try:

            if not os.path.exists(file_path):
                raise EFileDoesntExist(file_path)

            self.__out_stream.append(Center(self._name()))
            self.__out_stream.append("\nReport:\n\n")

            self.__out_stream.push_aligner(Right(""))

            self._execute_review(file_path, self.__out_stream)

            self.__out_stream.pop_aligner()

            self.__out_stream.append(Center("finished"))

        except EUnknown:
            raise
        except (OSError, ValueError) as err:
            raise EFailedToReview("unexpected exception was risen - " +
                                  str(err))


class PyLintCodeReviewer(CodeReviewer):
    """A code reviewer class, which uses a PyLint tool to review python
    scripts.
    """

    def __init__(self, out_stream):
        super().__init__(out_stream)

    # protected methods

    def _name(self):
        """Protected method, which gets a readable name of the reviewer.

        Returns:
            a string, which contains readable name of the reviewer.
        Raises:
            nothing.
        """
        return "PyLint Code Reviewer"

    def _execute_review(self, file_path, out_stream):
        """Runs a PyLint tool for the specified source file in a separate
        process and writes the resulting report into the output stream
        object.

        Args:
            file_path: a string path to the file to review.
            out_stream: an output stream object to write report to.
        Returns:
            nothing.
        Raises:
            EFailedToReview: if failed to perform the review process.
        """
        try:

            with Popen(['pylint.exe', file_path],
                       stdout=PIPE, stderr=PIPE) as proc:
                for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
                    out_stream.write(line)

        except (OSError, ValueError, SubprocessError):
            raise EFailedToReview("error in subprocess")


# methods


def get_default_reviewer(out_stream):
    """Instantiates and returns a default code reviewer.

    Args:
        out_stream: an output stream object to write a report to.
    Returns:
        a concrete code reviewer object.
    Raises:
        nothing.
    """
    return PyLintCodeReviewer(out_stream)


# testing


def main():
    """Performs testing and e.t.c.
    """
    pass


if __name__ == "__main__":
    main()
