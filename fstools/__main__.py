"""
    Performs pylint check and unit testing of the hole package.
        Author: O.Z.
        Version: 1.0
"""

from oztoolz.testfwk import review_current_package
from oztoolz.testfwk import test_current_package

from oztoolz.streams import StdoutStream


# testing


def main():
    """Runs tests and code review for all scripts of the package and logs out
    which scripts were checked.

    This method is executed when the whole package is executed.
    """
    review_current_package(StdoutStream())
    test_current_package(StdoutStream())

if __name__ == '__main__':
    main()
