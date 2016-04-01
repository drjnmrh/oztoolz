"""
    Runs a code review tool pylint for each script in the 'streams' package.
        Author: O.Z.
"""

# imports


import os
import sys

from pathlib import Path

from subprocess import Popen
from subprocess import PIPE

from oztoolz.ioutils import select_all_scripts

from oztoolz.ioutils import safe_write_log as write_log
from oztoolz.ioutils import get_current_package_path as find_package_sources


# utility methods


def run_pylint(script_name, package_path):
    """Executes a pylint code analyzer for the given script in a separate
    subprocess and writes the stdout of the subprocess into the .txt file.

    The created .txt file is named as the script name + '_report' suffix.

    Args:
        script_name: the name of the script to check.
        package_path: the path string to the package, which scripts are
                      analyzed.
    """
    script_path = os.path.join(package_path, script_name)
    with Popen(['pylint.exe', script_path], stdout=PIPE) as proc:
        script_file_name = str(Path(script_path).relative_to(package_path))
        write_log(script_file_name[:-3] + '_report.txt',
                  os.path.abspath(os.path.join(package_path, 'reports')),
                  proc.stdout.read(),
                  sys.stdout)


def review_code():
    """Runs an automatic code review tool 'pylint' for each script of the
    'streams' package.

    Returns:
        list of strings, each entry is a name of the checked script.
    """
    package_path = find_package_sources(sys.stdout)
    sys.stdout.write("# 'streams' package was found in [" +
                     package_path + "];\n")

    scripts = select_all_scripts(package_path, sys.stdout)
    for script_name in scripts:
        run_pylint(script_name, package_path)

    return scripts


# the main method


def main():
    """Runs code review for all scripts of the 'streams' package and logs out
    which scripts were checked.

    This method is executed when the whole package is executed.
    """
    sys.stdout.write("\nPyLint code review of the 'streams' package:\n")

    reviewed_scripts = review_code()

    sys.stdout.write("\treviewed scripts:\n")
    for script_name in reviewed_scripts:
        sys.stdout.write("\t\t" + script_name + "\n")

    sys.stdout.write("\ttotal number of the reviewed scripts: " +
                     str(len(reviewed_scripts)) + ";\n")

    sys.stdout.write("OK.\n")


if __name__ == '__main__':
    main()
