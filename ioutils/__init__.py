"""
    Defines different IO utility methods and classes.
        Author: O.Z.
"""


# imports


import os
import sys
import shutil

from pathlib import Path


__all__ = ['has_attribute',
           'compare_paths',
           'is_subfolder',
           'extract_file_name',
           'get_current_package_path',
           'select_all_scripts',
           'safe_write',
           'safe_write_log',
           'TemporaryFolder',
           'TemporaryFile',
           'TemporaryDirectoryTree',
           'TemporaryFoldersManager']


# methods


class TemporaryPathsEntry(object):
    """Temporary entry to the sys.paths variable.
    """

    def __init__(self, entry_value):
        self.__entry_value = entry_value

    def __str__(self):
        return self.__entry_value

    def __enter__(self):
        sys.path.insert(0, self.__entry_value)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for i in range(0, len(sys.path)):
            if sys.path[i] == self.__entry_value:
                sys.path.pop(i)
                return

    @property
    def value(self):
        """Gets entry value.
        """
        return self.__entry_value

    def is_already_in_paths(self):
        """Returns True if the entry is already in the sys.path list.
        """
        for path in sys.path:
            if path == self.value:
                return True
        return False


def has_attribute(module_path, attribute):
    """Checks if the given module has a specific attribute.

    Args:
        module_path: a string, containing path to the module.
        attribute: an attribute to check.
    Returns:
        True if there's such attribute, False otherwise.
    Raises:
        OSError, ValueError.
    """
    module = Path(module_path)
    parent = module.parent
    with TemporaryFile.from_path(str(parent / "temp_module.py")) as temp:
        temp.fill(module_path)
        module_name = "temp_module"
        with TemporaryPathsEntry(str(parent)) as paths_entry:
            try:
                __import__(module_name)
                return hasattr(sys.modules[module_name], attribute)
            except ImportError as err:
                raise ValueError("failed to import from " + str(paths_entry) +
                                 " module " + module_name + " - " + str(err))


def compare_paths(first, second):
    """Checks if two given paths are equal.

    Paths can be non-existing.
    Non-sensitive to the case.

    Args:
        first: a string (or object with overriden __str__ method), containing
               the first path.
        second: a string (or object with overriden __str__method), containing
                the second path.
    Returns:
        True if paths are equal, False otherwise.
    Raises:
        nothing.
    """
    try:
        abs_first = os.path.abspath(str(first))
        abs_second = os.path.abspath(str(second))
        return abs_first.lower() == abs_second.lower()
    except (OSError, ValueError) as err:
        safe_write(sys.stderr, "ioutils.compare_paths error: " + str(err))
    return str(first).lower() == str(second).lower()


def is_subfolder(subfolder_path, parent_path):
    """Tries to check if given path is a subfolder of the given parent path.

    Args:
        subfolder_path: a string, which contains a path to check.
        parent_path: the parent path string.
    Returns:
        True if the given path is a subfolder.
    Raises:
        OSError, ValueError.
    """
    subfolder_parents = list(Path(os.path.abspath(subfolder_path)).parents)

    parent_parents = [Path(os.path.abspath(parent_path))]
    parent_parents.extend(list(parent_parents[0].parents))

    subfolder_parents.reverse()
    parent_parents.reverse()

    if len(subfolder_parents) < len(parent_parents):
        return False

    for i in range(0, len(parent_parents)):
        if not compare_paths(parent_parents[i], subfolder_parents[i]):
            return False

    return True

def extract_file_name(file_path, error_stream=sys.stderr):
    """Tries to extract a file name from the given path string.

    The file should exist.

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


# classes


class TemporaryFolder(object):
    """Temporary folder object, which manages (creates and removes) specified
    by the path folder.

    The object can be used only if the path specifies the folder inside
    existing directory. The folder shouldn't exist before the object is
    instantiated.
    Doesn't require manager.

    Attributes:
        __path: a string, which contains path to the folder.
        __folder: a pathlib.Path object for the folder.
    """

    def __init__(self, path):
        self.__path = os.path.abspath(path)
        self.__folder = Path(self.__path)

        self.__folder.mkdir()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

    def cleanup(self):
        """Removes the temporary directory.

        Returns:
            nothing.
        Raises:
            nothing.
        """
        try:
            self.__folder.rmdir()
        except OSError as err:
            safe_write(sys.stderr, "TemporaryFolder.cleanup error: " +
                       str(err))

    @property
    def full_path(self):
        """Gets the full path to the folder.

        Returns:
            string, which contains absolute full path to the folder.
        Raises:
            nothing.
        """
        return self.__path

    @property
    def folder(self):
        """Gets a pathlib.Path object, related to the folder.

        Returns:
            a pathlib.Path object.
        Raises:
            nothing.
        """
        return self.__folder


class TemporaryFile(object):
    """Temporary file object, which manages its disk representation.

    The file is created inside existing folder. The file shouldn't exist before
    the object is instantiated.
    Doesn't require manager.

    Attributes:
        __path: a string, which contains the path to the file.
        __file: a pathlib.Path object for the file.
        __name: a string, which contains the file name.
    """

    def __init__(self, folder, file_name):
        self.__path = os.path.join(str(folder), file_name)
        self.__file = Path(self.__path)
        self.__name = file_name

        self.__file.touch()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

    @staticmethod
    def from_path(file_path):
        """Creates a temporary file, using the given full path.

        Args:
            file_path: a string, containing the full path to the temp file (or
                       object with a __str__ method).
        Returns:
            a temporary file object.
        Raises:
            OSError, ValueError.
        """
        file_obj = Path(str(file_path))
        return TemporaryFile(file_obj.parent,
                             str(file_obj.relative_to(str(file_obj.parent))))

    def fill(self, another_file_name):
        """Copies the content of the specified file into the temporary file.

        Args:
            another_file_name: a string, containing the path to the file with
                               a content.
        Returns:
            nothing.
        Raises:
            OSError, ValueError.
        """
        with open(another_file_name, "r") as another_file:
            with open(self.__path, "w") as temp_file:
                for line in another_file:
                    temp_file.write(line)

    def cleanup(self):
        """Removes the temporary file.

        In case of error, writes to the sys.stderr the message.

        Returns:
            nothing.
        Raises:
            nothing.
        """
        try:
            self.__file.unlink()
        except OSError as err:
            safe_write(sys.stderr, "TemporaryFile.cleanup error: " +
                       str(err))

    @property
    def full_path(self):
        """Gets the full path to the file.

        Returns:
            string, which contains absolute full path to the file.
        Raises:
            nothing.
        """
        return self.__path

    @property
    def file(self):
        """Gets a pathlib.Path object, related to the file.

        Returns:
            a pathlib.Path object.
        Raises:
            nothing.
        """
        return self.__file

    @property
    def name(self):
        """Gets the file name.

        Returns:
            a string, which contains the file name.
        Raises:
            nothing.
        """
        return self.__name


class TemporaryDirectoryTree(object):
    """An object, which creates and manages a directory tree, specified in
    constructor.

    The directory is specified by the dictionary object with two keys: name and
    subs. 'name' specifies the name of the directory tree node and 'subs' is a
    list of similar dictionary objects (nodes of the directory tree, which are
    children of current node).

    Attributes:
        __tree_path: a string, containing path to the tree.
        __cleanup_list: a list of TemporaryFolder objects sorted in order for
                        the cleanup.
    """
    def __init__(self, root_node, root_path=os.getcwd()):
        self.__tree_path = os.path.abspath(root_path)
        self.__cleanup_list = []

        creation_stack = [root_node]
        while len(creation_stack) > 0:
            cur_node = creation_stack[0]

            folder_path = os.path.join(root_path, cur_node['name'])
            self.__cleanup_list.append(TemporaryFolder(folder_path))

            for child in cur_node['subs']:
                child_path = os.path.join(cur_node['name'], child['name'])
                creation_stack.append(dict(name=child_path,
                                           subs=child['subs']))
            creation_stack.pop(0)

        self.__cleanup_list.reverse()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

    def cleanup(self):
        """Removes the temporary directory tree from the disk.

        In case of error, writes message to the sys.stderr.

        Returns:
            nothing.
        Raises:
            nothing.
        """
        try:
            for folder in self.__cleanup_list:
                folder.cleanup()
            self.__cleanup_list = []
        except (OSError, ValueError) as err:
            safe_write(sys.stderr, "TemporaryDirectoryTree.cleanup error: " +
                       str(err))

    @property
    def root_path(self):
        """Gets a tree root path.

        Returns:
            a string, containing path to the root of the tree.
        Raises:
            nothing.
        """
        return self.__tree_path


class ManagedTemporaryFolder(object):
    """Temporary folder object, which is managed by the temporary folders
    manager.

    Should be instantiated by the manager.

    Attributes:
        __path: a string, which contains path to the folder.
        __folder: a pathlib.Path object for the folder.
        __manager: a manager, which has tracks the folder.
    """

    def __init__(self, path, manager):
        self.__path = os.path.abspath(path)
        self.__folder = Path(self.__path)
        self.__manager = manager

        if not os.path.exists(str(self.__folder.parent)):
            manager.get_folder(str(self.__folder.parent))

        if not self.__folder.exists():
            self.__folder.mkdir()

    @property
    def absolute_path(self):
        """Gets an absolute path to the folder.

        Returns:
            a string, which contains an absolute path to the folder.
        Raises:
            nothing.
        """
        return self.__path

    @property
    def folder(self):
        """Gets a pathlib Path object for the folder.

        Returns:
            a pathlib Path object for the folder.
        Raises:
            OSError, ValueError
        """
        return self.__folder

    @property
    def parent(self):
        """Gets a parent directory of the folder.

        Returns:
            a temp folder object, corresponding to the parent directory.
        Raises:
            nothing.
        """
        return self.__manager.get_folder(str(self.__folder.parent))

    def create_file(self, file_name):
        """Asks the manager to create a temporary file inside the folder.

        Args:
            file_name: the name of the created file.
        Returns:
            nothing.
        Raises:
            OSError, ValueError.
        """
        temp_file = self.__folder / file_name
        self.__manager.track_file(temp_file.path)


class TemporaryFoldersManager(object):
    """Manager class of the temporary folders.

    It is a class, which manages created folders and tracks them. When the
    'cleanup' method is called (or the manager is been destroyed), these
    folders are removed.

    Attributes:
        __folders: list of temp folders objects.
        __files: list of paths to the temp files.
    """

    def __init__(self):
        self.__folders = []
        self.__files = []
        self.__force_remove = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.cleanup(self.__force_remove)
        except (OSError, ValueError) as err:
            safe_write(sys.stderr, str(err))

    @staticmethod
    def from_list(paths, force_remove=False):
        """Creates temporary folders manager from the list of entries with
        'path' and 'isdir' keys.

        Args:
            paths: list of dicts with 'path' and 'isdir' keys.
            force_remove: value of the force_remove of newly created manager.
        Returns:
            a temporary folders manager.
        Raises:
            OSError, ValueError.
        """
        temp_manager = TemporaryFoldersManager()
        for path in paths:
            if path['isdir']:
                temp_manager.get_folder(path['path'])
            else:
                temp_manager.track_file(path['path'])
        temp_manager.set_force_remove(force_remove)
        return temp_manager

    def set_force_remove(self, force_remove=True):
        """Sets the force_remove flag.

        Args:
            force_remove: new value of the flag.
        Returns:
            nothing.
        Raises:
            nothing.
        """
        self.__force_remove = force_remove

    def get_folder(self, folder_path):
        """Gets a temporary folder object for the specified path.

        If the temporary folder already exists, returns the registered object.
        Otherwise creates the folder, registers it and returns the object.

        Args:
            folder_path: a string, which contains a path to the folder.
        Returns:
            a temporary folder object.
        Raises:
            OSError, ValueError.
        """
        folder_abs_path = os.path.abspath(folder_path)

        for temp_folder in self.__folders:
            if temp_folder.absolute_path.upper() == folder_abs_path.upper():
                return temp_folder

        folder = Path(folder_path)
        if folder.exists():
            if not folder.is_dir():
                raise ValueError()
            return ManagedTemporaryFolder(folder_path, self)

        result = ManagedTemporaryFolder(folder_path, self)
        self.__folders.append(result)

        return result

    def is_temporary(self, path):
        """Checks if given folder or file is registered as temporary.

        Args:
            path: a string, which contains the path.
        Returns:
            True if the path is temporary.
        Raises:
            OSError.
        """
        folder = Path(path)
        if not folder.exists():
            return False

        ref_paths = []
        if folder.is_file():
            ref_paths = [temp for temp in self.__files]
        else:
            ref_paths = [temp.absolute_path for temp in self.__folders]

        for ref_path in ref_paths:
            if compare_paths(ref_path, str(folder)):
                return True
        return False

    def track_file(self, file_path):
        """Registers the given file as temporary.

        If the file doesn't exist, it will be created.

        Args:
            file_path: a string, which contains path to the file.
        Returns:
            nothing.
        Raises:
            OSError.
        """
        file_object = Path(file_path)
        for temp_file in self.__files:
            if compare_paths(file_path, temp_file):
                return

        self.get_folder(str(file_object.parent))

        if not file_object.exists():
            file_object.touch()

        self.__files.append(os.path.abspath(file_path))

    def cleanup(self, force_remove=False):
        """Removing all temporary folders and files.

        Args:
            force_remove: determines if non-registered subfolders should be
                          removed.
        Returns:
            nothing.
        Raises:
            OSError, ValueError.
        """
        for temp_file_path in self.__files:
            temp_file = Path(temp_file_path)
            if temp_file.exists() and temp_file.is_file():
                temp_file.unlink()
        self.__files = []

        cleanup_queue = []
        sorting_queue = [temp for temp in self.__folders]
        while len(sorting_queue) > 0:
            not_parent = None
            for i in range(0, len(sorting_queue)):
                is_not_parent = True
                for j in range(0, len(sorting_queue)):
                    if i == j:
                        continue
                    if is_subfolder(sorting_queue[j].absolute_path,
                                    sorting_queue[i].absolute_path):
                        is_not_parent = False
                        break
                if is_not_parent:
                    not_parent = i
                    break
            assert not not_parent is None

            cleanup_queue.append(sorting_queue[not_parent])
            sorting_queue.pop(not_parent)

        for temp in cleanup_queue:
            if not force_remove:
                temp.folder.rmdir()
            else:
                shutil.rmtree(temp.absolute_path)


# testing


def main():
    """Checking and Testing method
    """
    pass


if __name__ == '__main__':
    main()
