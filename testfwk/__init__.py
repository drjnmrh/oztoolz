"""
    Defines useful testing and code reviewing API methods.
        Author: O.Z.

    Content:

        review_code_and_report           - runs a code reviewer and writes
                                           report into the separate file in
                                           specified reports folder (if the
                                           reviewer wasn't explicitly given).

        review_current_package           - runs a default code reviewer for
                                           all scripts, found in the folder
                                           of the package, which contains
                                           current executed script.

        test_current_package             - runs unit tests for all scripts,
                                           found in the folder of the package,
                                           which contains current executed
                                           script; tests are assumed to be
                                           defined in the *.tests.py scripts
                                           for each script to test to.
"""


# imports

import os

from pathlib import Path

from ..streams import FileOutStream
from ..streams.errors import EFailedToInitialize

from ..ioutils import get_current_package_path
from ..ioutils import select_all_scripts

from .codereview import get_default_reviewer

from .utesting import has_module_tests
from .utesting import run_tests_for_module

from .errors import EFailedToReview
from .errors import EFailedToTest
from .errors import EFileDoesntExist

from ..streams.aligners import CenterAligner as Title
from ..streams.aligners import RightAligner as Tab


__all__ = ['review_code_and_report', 'review_current_package']


# API


def review_code_and_report(source_file_path, reports_folder, reviewer=None):
    """Runs a code reviewer for the specified source file.

    The report is written into the file inside the specified reports folder.
    The report name is the name of the source file + _review postfix and
    .txt extension. If the reports folder doesn't exist, it will be created.

    The reviewer can be specified. By default the reviewer, returned by the
    codereview.get_default_reviewer method is used.

    Args:
        source_file_path: a path string to the source file to review.
        reports_folder: a path string to the reports folder.
        reviewer: an optional parameter, to specify explicitly the reviewer.
    Returns:
        nothing.
    Raises:
        EFileDoesntExist: the specified source file doesn't exist.
        EFailedToReview: an error occured during the reviewing process.
    """
    out_stream = None

    try:

        report_name = Path(source_file_path).name + "_review.txt"

        reports_path = Path(reports_folder)
        if not reports_path.exists():
            reports_path.mkdir(0o777, True)

        out_stream = FileOutStream(str(reports_path.joinpath(report_name)))

    except EFailedToInitialize as err:
        raise EFailedToReview("failed to open output stream - " + str(err))
    except (OSError, ValueError):
        raise EFailedToReview("failed to generate report file path")

    if reviewer is None:
        reviewer = get_default_reviewer(out_stream)
    else:
        reviewer.attach(out_stream)

    reviewer.review(source_file_path)


def review_current_package(out_stream):
    """Runs a default automatic code reviewer for all scripts inside the
    package, which contains current executed script.

    Writes report into the 'reports' folder inside the current package
    directory. If the 'reports' folder doesn't exist, it will be created.

    Args:
        out_stream: a stream, to log to.
    Returns:
        nothing.
    Raises:
        EFailedToReview: if an error during review occured.
    """
    out_stream.append(Title("Running a code review for current package"))

    package_path = get_current_package_path()
    if package_path == '':
        raise EFailedToReview("failed to get package path")

    out_stream.append("# found package in [" + package_path + "];")

    scripts = select_all_scripts(package_path)
    if len(scripts) == 0:
        raise EFailedToReview("failed to select scripts of the package")

    out_stream.append("running review for [" + str(len(scripts)) + "] scripts:")
    out_stream.push_aligner(Tab(""))

    try:

        for script in scripts:
            out_stream.append(script + "...")

            script_full_path = os.path.join(package_path, script)
            reports_full_path = os.path.join(package_path, "reports")

            review_code_and_report(script_full_path,
                                   reports_full_path)

            out_stream.write("Ok;")

    except EFileDoesntExist as err:
        raise EFailedToReview("the source file is missing [" + str(err) + "]")
    except OSError as err:
        raise EFailedToReview("failed to get path [" + str(err) + "]")

    out_stream.pop_aligner()
    out_stream.append("finished :)")


def test_current_package(out_stream):
    """Runs unit tests (<script_name>.tests.py files) for all scripts in the
    current package.

    Writes report into the 'reports' folder inside the current package
    directory. If the 'reports' folder doesn't exist, it will be created.

    Args:
        out_stream: a stream, to log to.
    Returns:
        nothing.
    Raises:
        EFailedToTest: if an error during testing occured.
    """
    out_stream.append(Title("Running unit tests for current package"))

    package_path = get_current_package_path()
    if package_path == '':
        raise EFailedToTest("failed to get package path")

    out_stream.append("# found package in [" + package_path + "];")

    scripts = select_all_scripts(package_path)
    if len(scripts) == 0:
        raise EFailedToTest("failed to select scripts of the package")

    try:
        scripts_with_tests = []
        for script in scripts:
            script_path = os.path.join(package_path, script)
            if has_module_tests(script_path):
                scripts_with_tests.append(script)

        out_stream.append("found tests for [" +
                          str(len(scripts_with_tests)) + "] scripts:")
        out_stream.push_aligner(Tab(""))

        for script in scripts_with_tests:
            try:
                out_stream.append(script + "...")

                script_full_path = os.path.join(package_path, script)
                reports_full_path = os.path.join(package_path, "reports")

                run_tests_for_module(script_full_path, reports_full_path)

                out_stream.write("Ok;")
            except EFileDoesntExist as err:
                out_stream.write("Failed (" + str(err) + ");")
            except EFailedToTest as err:
                out_stream.write("Failed (" + str(err) + ");")
    except (OSError, ValueError) as err:
        raise EFailedToTest("failed to get the path - " + str(err))

    out_stream.pop_aligner()
    out_stream.append("finished :)")


# testing


def main():
    """Performs testing and e.t.c.
    """
    pass


if __name__ == '__main__':
    main()
