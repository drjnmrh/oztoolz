"""
    Defines different IO utility methods.
        Author: O.Z.
"""


# imports


import os
import sys

from pathlib import Path


__all__ = ['extract_file_name',
           'get_current_package_path',
           'select_all_scripts',
           'safe_write',
           'safe_write_log']


# methods


def extract_file_name(file_path, error_stream=sys.stderr):
    """Tries to extract a file name from the given path string.

    Args:
        file_path: a path string to get the file name from.
        error_stream: a stream to write error messages to.
    Returns:
        a string, containing file name if succeeded, an empty string
        otherwise.
    Raises:
        nothing.
    """
    try:
        file_object = Path(file_path)
        if not file_object.is_file():
            safe_write(error_stream, "ioutils.extract_file_name error: " +
                       file_path + " is not a file")
            return ""

        return str(file_object.relative_to(str(file_object.parent)))
    except (OSError, ValueError) as err:
        safe_write(error_stream, "ioutils.extract_file_name error: " +
                   str(err))
    return ""

def get_current_package_path(error_stream=sys.stderr):
    """Tries to get current executed scripts package path.

    Args:
        error_stream: a stream to write error messages to.
    Returns:
        a string, containing package path if succeeded, an empty string
        otherwise.
    Raises:
        nothing.
    """
    try:

        current_module_path = Path(os.path.join(os.getcwd(), sys.argv[0]))
        if not current_module_path.exists():
            safe_write(error_stream, "ioutils.get_current_package_path error")
            return ""

        if current_module_path.is_file():
            return os.path.abspath(str(current_module_path.parent))
        return os.path.abspath(str(current_module_path))

    except OSError as err:
        safe_write(error_stream, "ioutils.get_current_package_path error: " +
                   str(err))
        return ""

    return ""

def select_all_scripts(path_string, error_stream=sys.stderr):
    """Gets the list of the scripts inside the specified package.

    The package is specified by the path to the folder with scripts.
    The method seeks the scripts recursively. The result is a list of
    strings, each entry is a relative path to the script (including file
    name).

    Args:
        path_string: a path string to the package, which scripts are selected.
        error_stream: a stream to write error to.
    Returns:
        list of strings, each entry is a relative to the specified package path
        (with file name) to the script. Returns an empty list in case of the
        error.
    Raises:
        nothing.
    """
    scripts = []
    try:

        path_object = Path(path_string)
        script_objects = list(path_object.glob("**/*.py"))

        for script in script_objects:
            scripts.append(str(Path(str(script)).relative_to(path_string)))

    except (OSError, ValueError):
        safe_write(error_stream, "ioutils.select_all_scripts error.")

    return scripts


def safe_write(file_object, string_buffer):
    """Writes a string buffer using 'write' method of the given file object.

    Doesn't raise exceptions, but returns False if wasn't successful (and True
    otherwise).

    Args:
        file_object: the file object to use for output.
        string_buffer: a string buffer to write.
    Returns:
        True if succeeded.
    Raises:
        nothing.
    """
    try:
        file_object.write(string_buffer)
        return True
    except ValueError:
        if not file_object == sys.stderr:
            safe_write(sys.stderr, "ioutils.safe_write: ValueError.\n")

    return False


def safe_write_log(log_file_name, logs_folder, string_buffer,
                   error_stream=sys.stderr):
    """Writes specified string buffer into the log file.

    It is assumed, that the log files should be placed into the specified
    folder. If the folder doesn't exist, it is created. If the log file
    already exists, it is rewritten.

    Args:
        log_file_name: the name of the log file.
        logs_folder: the folder, where the log file should be placed into.
        string_buffer: the string buffer to write.
        error_stream: an object with 'write' method, to write erros to.
    Returns:
        True if succeeded.
    Raises:
        nothing.
    """
    try:
        if not os.path.exists(logs_folder):
            os.mkdir(logs_folder)
    except OSError:
        safe_write(error_stream,
                   "ioutils.safe_write_log: failed to create " + logs_folder)
        return False

    log_path = ""

    try:
        log_path = os.path.join(logs_folder, log_file_name)
    except OSError:
        safe_write(error_stream,
                   "ioutils.safe_write_log: failed to join file path.")
        return False

    try:
        if not os.path.exists(log_path):
            os.close(os.open(log_path, os.O_CREAT))
    except OSError:
        safe_write(error_stream,
                   "ioutils.safe_write_log: failed to create " + log_file_name)
        return False

    try:
        log_object = os.open(log_path, os.O_WRONLY)
        os.write(log_object, string_buffer)
        os.close(log_object)
    except OSError:
        safe_write(error_stream,
                   "ioutils.safe_write_log: failed to write " + log_file_name)
        return False

    return True


# testing


def main():
    """Checking and Testing method
    """
    pass


if __name__ == '__main__':
    main()
