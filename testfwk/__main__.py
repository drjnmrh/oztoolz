"""
    Runs a code review tool for each script in the 'testfwk' package.
        Author: O.Z.
"""


# imports


from oztoolz.testfwk import review_current_package

from oztoolz.streams import StdoutStream


# testing


def main():
    """Runs code review for all scripts of the 'testfwk' package and logs out
    which scripts were checked.

    This method is executed when the whole package is executed.
    """
    review_current_package(StdoutStream())

if __name__ == '__main__':
    main()
