"""
    Defines file system and data manipulator classes.
        Author: O.Z.
"""

# imports

import os
import sys
import shutil

from pathlib import Path

from oztoolz.ioutils import safe_write

from oztoolz.streams import DummyOutStream

from oztoolz.fstools.errors import EFailedToInitialize
from oztoolz.fstools.errors import EFailedToManipulate
from oztoolz.fstools.errors import EPathDoesntExist

from oztoolz.streams.errors import EUnknown as EUnknownStreamsError

from oztoolz.streams.aligners import AutoAligner as Scope
from oztoolz.streams.aligners import RightAligner as Tab


# public API declarations


__all__ = ['PathManipulator',
           'FileManipulator',
           'FolderManipulator']


# API




def _safe_append(log_stream, message_object):
    """Appends the message to the log stream, without raising exceptions.
    """
    try:
        log_stream.append(message_object)
    except EUnknownStreamsError as error:
        safe_write(sys.stderr, "fstools failed to log " + str(message_object) +
                   " - " + str(error))




# classes




class PathManipulator:
    """Basic path manipulator class.

    The manipulator has a name and a corresponding pathlib object.
    Also the target object (which is pointed by the path) can be acquired.
    Derived classes should implement some specific methods, like copy, move and
    remove. These methods should raise EFailedToManipulate exception in case of
    errors.

    Attriubtes:
        self.__path_obj: a corresponding pathlib object.
        self.__notm_path: a string, containing absolute full path.
        self.__name: the name of the manipulator
    """

    def __init__(self, path, manipulator_name="Path Manipulator"):
        try:
            self.__path_obj = Path(str(path))
            if not self.__path_obj.exists():
                raise EPathDoesntExist(str(self.__path_obj))
            self.__norm_path = os.path.abspath(str(path)).lower()

            self.__name = manipulator_name
        except (OSError, ValueError) as err:
            raise EFailedToInitialize(manipulator_name, str(err))
        except EPathDoesntExist as err:
            raise EFailedToInitialize(manipulator_name, str(err))

    def __str__(self):
        return self.__norm_path

    # properties

    @property
    def normalized_path(self):
        """Gets an absolute full path.

        Returns:
            a string, containing normalized path.
        Raises:
            nothing.
        """
        return self.__norm_path

    @property
    def name(self):
        """Gets the name of the manipulator.

        Returns:
            a string, containing the name of the manipulator.
        Raises:
            nothing.
        """
        return self.__name

    @property
    def path(self):
        """Gets a corresponding pathlib Path object.

        Returns:
            a pathlib.Path object.
        Raises:
            nothing.
        """
        return self.__path_obj

    # public API

    def exists(self):
        """Checks if the path exists.

        Returns:
            True if the path exists, False otherwise.
        Raises:
            EFailedToManipulate.
        """
        try:
            return os.path.exists(self.normalized_path)
        except (OSError, ValueError) as err:
            raise EFailedToManipulate(self.name, "exists", str(err))

    def target(self):
        """Gets the target object, pointed by the path.

        Returns:
            a string, containing the target.
        Raises:
            EFailedToManipulate.
        """
        try:
            if self.path.parent is None:
                return str(self.path)

            return str(self.path.relative_to(str(self.path.parent)))
        except (OSError, ValueError) as err:
            raise EFailedToManipulate(self.name, "target", str(err))

    def reset(self, path):
        """Resets the manipulator to another path.

        It is strongly recommended to override this method for derived classes,
        calling the base class implementation in the process.

        Args:
            path: a convertable to string object, which specifies the new path.
        Returns:
            a string, containing an old path.
        Raises:
            EFailedToManipulate.
        """
        old_path = self.normalized_path

        try:
            self.__path_obj = Path(str(path))
            if not self.__path_obj.exists():
                raise EPathDoesntExist(str(self.__path_obj))
            self.__norm_path = os.path.abspath(str(path)).lower()
        except (OSError, ValueError) as err:
            raise EFailedToManipulate(self.name, "reset", str(err))
        except EPathDoesntExist as err:
            raise EFailedToManipulate(self.name, "reset", str(err))

        return old_path


    # abstract API

    def copy(self, destination, overwrite=False, log_stream=DummyOutStream()):
        """An abstract method, which copies the target object to the
        destination path.

        Args:
            destination: a convertable to string object, which specifies the
                         destination path.
            overwrite: a flag, which determines should the already existing
                       destination folder be overwritten or an exception should
                       be risen.
            log_stream: an output stream to write log messages to.
        Returns:
            nothing.
        Raises:
            EFailedToManipulate, NotImplementedError.
        """
        raise NotImplementedError()

    def move(self, destination, log_stream=DummyOutStream()):
        """An abstract method, which moves the target object to the specified
        destination.

        Args:
            destination: a convertable to string object, which specifies the
                         destination path.
            log_stream: an output stream to write log messages to.
        Returns:
            nothing.
        Raises:
            EFailedToManipulate, NotImplementedError.
        """
        raise NotImplementedError()

    def remove(self, log_stream=DummyOutStream()):
        """An abstract method, which removes the target object.

        Args:
            log_stream: an output stream to write log messages to.
        Returns:
            nothing.
        Raises:
            EFailedToManipulate, NotImplementedError.
        """
        raise NotImplementedError()




class FileManipulator(PathManipulator):
    """The file manipulating class.

    Provides control methods for files.

    Attributes:
        __is_temporary: the flag, which signalizes if the file is temporary.
    """

    def __init__(self, path, manipulator_name="File Manipulator"):
        super().__init__(path, manipulator_name)
        self.__is_temporary = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.__is_temporary:
                self.remove()
        except EFailedToManipulate as err:
            safe_write(sys.stderr,
                       "fstools.FileManipulator error: " +
                       "failed to remove temp file " + str(self) + " - " +
                       str(err))

    # static API

    @staticmethod
    def create(path, force_create=False):
        """Creates the file and instantiates the manipulator.

        If the parent folder doesn't exist, than the specified force_create
        flag is checked: if it is True, the parent folders are created,
        EFailedToInitialize exception is raised otherwise.

        Args:
            path: a convertable to string object, which specifies thepath to
                  the created file.
            force_create: the flag, which specifies if the file should be
                          created with its parent directories.
        Returns:
            a file manipulator.
        Raises:
            EFailedToInitialize.
        """
        try:
            path_object = Path(str(path))
            parent_path = Path(str(path_object.parent))
            if not parent_path.exists() and not force_create:
                raise EFailedToInitialize("File Manipulator",
                                          "parent folder doesn't exist [" +
                                          str(parent_path) + "]")
            elif not parent_path.exists():
                parent_path.mkdir(0o777, True, True)
            return FileManipulator(path)
        except (OSError, ValueError) as err:
            raise EFailedToInitialize("File Manipulator", str(err))

    @staticmethod
    def temp(path):
        """Creates temporary file and returns its manipulator.

        All parent folders must exist.

        Args:
            path: a string, containing path to the file.
        Returns:
            file manipulator.
        Raises:
            EFailedToInitialize.
        """
        try:
            path_object = Path(str(path))
            parent_path = Path(str(path_object.parent))
            if not parent_path.exists():
                raise EFailedToInitialize("File Manipulator",
                                          "parent folder doesn't exist - " +
                                          str(parent_path))
            if not path_object.exists():
                path_object.touch()

            manipulator = FileManipulator(str(path))
            manipulator.make_temporary()
            return manipulator
        except (OSError, ValueError) as err:
            EFailedToInitialize("File Manipulator", str(err))

    # property

    @property
    def is_temporary(self):
        """Checks if the file is temporary.

        Returns:
            True if the file is temporary.
        Raises:
            nothing.
        """
        return self.__is_temporary

    # overriden API

    def reset(self, path):
        """Resets the manipulator to another file.

        Args:
            path: a convertable to string object, which specifies the path to
                  the file.
        Returns:
            a string, containing an old path.
        Raises:
            EFailedToManipulate.
        """
        old_path = super().reset(path)

        try:
            if self.is_temporary:
                FileManipulator(self).remove()
        except EFailedToInitialize as err:
            raise EFailedToManipulate(self.name, "reset", str(err))

        return old_path

    def copy(self, destination, overwrite=False, log_stream=DummyOutStream()):
        """Copies the file to the destination path.

        Args:
            destination: a convertable to string object, which specifies where
                         should the copy be created.
            overwrite: a flag, which determines should the already existing
                       destination file be overwritten or an exception should
                       be risen.
            log_stream: an output stream to write log messages to.
        Returns:
            a file copy manipulator.
        Raises:
            EFailedToManipulate.
        """
        if not self.exists():
            raise EFailedToManipulate(self.name, "copy", self.normalized_path +
                                      " doesn't exist anymore")
        try:
            _safe_append(log_stream,
                         "coping " + self.target + " to " + str(destination) +
                         "...")

            if os.path.exists(str(destination)) and not overwrite:
                raise EFailedToManipulate(self.name, "copy", str(destination) +
                                          " already exists")
            shutil.copy(str(self), str(destination))

            safe_write(log_stream, "Ok")
            return FileManipulator(destination)
        except (OSError, ValueError, EFailedToInitialize) as err:
            raise EFailedToManipulate(self.name, "copy", str(err))

    def move(self, destination, log_stream=DummyOutStream()):
        """Moves the file to the destination path.

        This method will raise an exception, if the destination file already
        exists.

        Args:
            destination: a convertable to string object, which specifies where
                         should the file be moved.
            log_stream: an output stream to write log messages to.
        Returns:
            nothing.
        Raises:
            EFailedToManipulate.
        """
        if not self.exists():
            raise EFailedToManipulate(self.name, "move", self.normalized_path +
                                      " doesn't exist anymore")

        try:
            _safe_append(log_stream,
                         "moving " + self.target + " to " + str(destination) +
                         "...")

            if os.path.exists(str(destination)):
                raise EFailedToManipulate(self.name, "move", "destination " +
                                          str(destination) + " already exists")

            shutil.move(str(self), str(destination))
            self.reset(destination)

            safe_write(log_stream, "Ok")
        except (OSError, ValueError, EFailedToInitialize) as err:
            raise EFailedToManipulate(self.name, "move", str(err))

    def remove(self, log_stream=DummyOutStream()):
        """Removes the file.

        If the file doesn't exist it will raise a EFailedToManipulate
        exception.

        Args:
            log_stream: an output stream to write log messages to.
        Returns:
            nothing.
        Raises:
            EFailedToManipulate.
        """
        if not self.exists():
            raise EFailedToManipulate(self.name, "remove",
                                      self.normalized_path +
                                      " doesn't exist anymore")
        try:
            _safe_append(log_stream,
                         "removing " + self.target + "...")

            self.path.unlink()

            safe_write(log_stream, "Ok")
        except (OSError, ValueError) as err:
            raise EFailedToManipulate(self.name, "remove", str(err))

    # folder specific API

    def make_temporary(self):
        """Makes the file temporary.

        Returns:
            nothing.
        Raises:
            nothing.
        """
        self.__is_temporary = True

    def pure_name(self):
        """Gets the name of the file, excluding all suffixes.

        Returns:
            a string, containing name of the file without suffixes.
        Raises:
            EFailedToManipulate.
        """
        try:
            if self.target().rfind('.') == -1:
                return self.target()
            return self.target()[:self.target().rfind('.')]
        except (ValueError, IndexError) as err:
            raise EFailedToManipulate(self.name, "pure_name", str(err))

    def extension(self):
        """Gets an extension of the file, if the file has any.

        Returns:
            a string, containing extension (without the dot) of the file.
        Raises:
            EFailedToManipulate.
        """
        try:
            return self.path.suffix[1:]
        except (OSError, ValueError, IndexError) as err:
            raise EFailedToManipulate(self.name, "extension", str(err))




class FolderManipulator(PathManipulator):
    """The folder manipulating class.

    Provides control and manipulation methods for folders.

    Attributes:
        __is_temporary: the flag, which signalizes if the folder is temporary.
    """

    def __init__(self, path, manipulator_name="Folder Manipulator"):
        super().__init__(path, manipulator_name)
        self.__is_temporary = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.__is_temporary:
                self.remove()
        except EFailedToManipulate as err:
            safe_write(sys.stderr,
                       "fstools.FolderManipulator error: " +
                       "failed to remove temp folder " + self.normalized_path +
                       " - " + str(err))

    # static API

    @staticmethod
    def create(path, force_create=False):
        """Creates the folder and instantiates the manipulator.

        If the parent folder doesn't exist, than the specified force_create
        flag is checked: if it is True, the parent folders are created,
        EFailedToInitialize exception is raised otherwise.

        Args:
            path: a convertable to string object, which specifies the path to
                  the created folder.
            force_create: the flag, which specifies if the folder should be
                          created with its parent directories.
        Returns:
            a folder manipulator.
        Raises:
            EFailedToInitialize.
        """
        try:
            full_path = os.path.abspath(str(path))
            path_object = Path(full_path)
            parent_path = str(path_object.parent)
            if not Path(parent_path).exists() and not force_create:
                raise EFailedToInitialize("Folder Manipulator",
                                          "parent folder doesn't exist [" +
                                          parent_path + "]")
            path_object.mkdir(0o777, True, True)
            return FolderManipulator(full_path)
        except (OSError, ValueError) as err:
            raise EFailedToInitialize("Folder Manipulator", str(err))

    @staticmethod
    def temp(path):
        """Instantiates the temporary folder manipulator.

        All parent folders should exist.

        Args:
            path: a convertable to string object, which specifies the path to
                  the temporary directory.
        Returns:
            a folder manipulator.
        Raises:
            EFailedToInitialize.
        """
        try:
            full_path = os.path.abspath(str(path))
            path_object = Path(full_path)
            parent_path = str(path_object.parent)
            if not Path(parent_path).exists():
                raise EFailedToInitialize("Folder Manipulator",
                                          "parent folder doesn't exist [" +
                                          parent_path + "]")

            if not os.path.exists(full_path):
                path_object.mkdir()

            manipulator = FolderManipulator(full_path)
            manipulator.make_temporary()
            return manipulator
        except (OSError, ValueError) as err:
            raise EFailedToInitialize("Folder Manipulator", str(err))
        except EFailedToManipulate as err:
            raise EFailedToInitialize("Folder Manipulator",
                                      "failed to make temporary - " + str(err))

    # properties

    @property
    def is_temporary(self):
        """Checks if the folder is temporary.

        Returns:
            True if the folder is temporary, False otherwise.
        Raises:
            nothing.
        """
        return self.__is_temporary

    # overriden API

    def reset(self, path):
        """Resets the manipulator to the new path.

        Args:
            path: a convertable to string object, which specifies the new path.
        Returns:
            a string, containing an old path.
        Raises:
            EFailedToManipulate.
        """
        old_path = super().reset(path)

        try:
            if self.is_temporary:
                FolderManipulator(old_path).remove()
        except EFailedToInitialize as err:
            raise EFailedToManipulate(self.name, "reset",
                                      "failed to remove the temp folder - " +
                                      str(err))

        return old_path

    def copy(self, destination, overwrite=False, log_stream=DummyOutStream()):
        """Copies the folder and its content to the destination path.

        Args:
            destination: a convertable to string object, which specifies where
                         should the copy be created.
            overwrite: a flag, which determines should the already existing
                       destination folder be overwritten or an exception should
                       be risen.
            log_stream: an output stream to write log messages to.
        Returns:
            a folder copy manipulator.
        Raises:
            EFailedToManipulate.
        """
        if not self.exists():
            raise EFailedToManipulate(self.name, "copy", self.normalized_path +
                                      " doesn't exist anymore")
        try:
            _safe_append(log_stream,
                         "coping " + self.target + " to " + str(destination) +
                         "...")

            dir_copy = FolderManipulator.create(os.path.join(destination,
                                                             self.target),
                                                True)

            with Scope(log_stream, Tab("")) as scope:
                content = self.list()
                for path in content:
                    path.copy(dir_copy.normalized_path, scope.stream)

                if len(content) > 0:
                    _safe_append(scope.stream, "")

            safe_write(log_stream, "Ok")
            return dir_copy
        except (OSError, ValueError, EFailedToInitialize) as err:
            raise EFailedToManipulate(self.name, "copy", str(err))

    def move(self, destination, log_stream=DummyOutStream()):
        """Moves the folder and its content to the destination path.

        This method will raise an exception, if the destination folder already
        exists.

        Args:
            destination: a convertable to string object, which specifies where
                         should the folder be moved.
            log_stream: an output stream to write log messages to.
        Returns:
            nothing.
        Raises:
            EFailedToManipulate.
        """
        if not self.exists():
            raise EFailedToManipulate(self.name, "move", self.normalized_path +
                                      " doesn't exist anymore")

        try:
            _safe_append(log_stream,
                         "moving " + self.target + " to " + str(destination) +
                         "...")

            if os.path.exists(str(destination)):
                raise EFailedToManipulate(self.name, "move", "destination " +
                                          str(destination) + " already exists")

            with FolderManipulator.create(destination, True) as moved:
                with Scope(log_stream, Tab("")) as scope:
                    content = self.list()
                    for path in content:
                        path.move(os.path.join(str(moved), path.target),
                                  scope.stream)

                    if len(content) > 0:
                        _safe_append(scope.stream, "")

                self.remove()
                self.reset(destination)

            safe_write(log_stream, "Ok")
        except (OSError, ValueError, EFailedToInitialize) as err:
            raise EFailedToManipulate(self.name, "move", str(err))

    def remove(self, log_stream=DummyOutStream()):
        """Removes the folder and all its content.

        If the folder doesn't exist it will raise a EFailedToManipulate
        exception.

        Args:
            log_stream: an output stream to write log messages to.
        Returns:
            nothing.
        Raises:
            EFailedToManipulate.
        """
        if not self.exists():
            raise EFailedToManipulate(self.name, "remove",
                                      self.normalized_path +
                                      " doesn't exist anymore")
        try:
            _safe_append(log_stream,
                         "removing " + self.target + "...")

            with Scope(log_stream, Tab("")) as scope:
                content = self.list()
                for path in content:
                    path.remove(scope.stream)

                if len(content) > 0:
                    _safe_append(scope.stream, "")

            self.remove()

            safe_write(log_stream, "Ok")
        except (OSError, ValueError) as err:
            raise EFailedToManipulate(self.name, "remove", str(err))

    # folder specific API

    def make_temporary(self):
        """Makes the folder temporary.

        Returns:
            nothing.
        Raises:
            nothing.
        """
        self.__is_temporary = True

    def is_empty(self):
        """Checks if the folder is empty.

        Returns:
            True if the folder is empty.
        Raises:
            EFailedToManipulate.
        """
        try:
            return len(self.path.iterdir()) == 0
        except (OSError, ValueError) as err:
            raise EFailedToManipulate(self.name, "is_empty", str(err))

    def list(self, log_stream=DummyOutStream()):
        """Gets a list of directories and files inside the folder.

        Args:
            log_stream: a stream to log to.
        Returns:
            a list of path manipulators.
        Raises:
            EFailedToManipulate.
        """
        if not self.exists():
            raise EFailedToManipulate(self.name, "list", str(self) +
                                      " doesn't exist")
        try:
            _safe_append(log_stream,
                         "listing the " + self.target() + " folder:")
            directories = []
            files = []
            for child in self.path.iterdir():
                if child.is_dir():
                    directories.append(FolderManipulator(str(child)))
                else:
                    files.append(FileManipulator(str(child)))

            children = []
            with Scope(log_stream, Tab("")) as scope:
                for manipulator in directories:
                    _safe_append(scope.stream, manipulator.target())
                    children.append(manipulator)
                for manipulator in files:
                    _safe_append(scope.stream, manipulator.target())
                    children.append(manipulator)
            return children
        except (OSError, ValueError, EFailedToInitialize) as err:
            raise EFailedToManipulate(self.name, "list", str(err))

    def files(self, recoursive=False):
        """Gets a list of files inside the folder.

        In order to add to the list all files inside subfolders, the recoursive
        parameter can be set to True.

        Args:
            recoursive: a flag, which determines if the files search should
                        include subfolders.
        Returns:
            a list of file manipulators.
        Raises:
            EFailedToManipulate.
        """
        if not self.exists():
            raise EFailedToManipulate(self.name, "files", str(self) +
                                      "doesn't exist.")

        pat = "*.*"
        if recoursive:
            pat = "**/" + pat

        try:
            return [FileManipulator(it) for it in list(self.path.glob(pat))]
        except (OSError, ValueError, EFailedToInitialize) as err:
            raise EFailedToManipulate(self.name, "files", str(err))

    def mkdir(self, folder_name, ignore_existence=False):
        """Create folder inside the directory, controlled by the manipulator.

        If the sub-folder already exists, the EFailedToManipulate exception
        will be raised, depending on the value of the ignore_existence flag.

        Args:
            folder_name: a string, containing name of the sub-folder.
            ignore_existence: flag, which controls, if EFailedToManipulate
                              should be raised.
        Returns:
            the new folder manipulator.
        Raises:
            EFailedToManipulate.
        """
        try:
            subfolder = self.path / folder_name
            parts = os.path.split(str(subfolder))
            if parts[1].lower() != folder_name.lower():
                raise EFailedToManipulate(self.name, "mkdir", "incorrect " +
                                          folder_name + " name")
            if subfolder.exists():
                if not ignore_existence:
                    raise EFailedToManipulate(self.name, "mkdir", "subfolder " +
                                              folder_name + " already exists")
            else:
                subfolder.mkdir()

            return FolderManipulator(str(subfolder))
        except (OSError, ValueError, EFailedToInitialize) as err:
            raise EFailedToManipulate(self.name, "mkdir", str(err))

    def rmdir(self, folder_name, ignore_not_empty=True,
              ignore_not_exists=False):
        """Removes the subfolder.

        The behavior in specific cases is regulated by the flags:
        ignore_not_empty and ignore_not_exists. If the subfolder doesn't exist
        and ignore_not_exists is False, or if the subfolder is not empty and
        ignore_not_empty is False, than EFailedToManipulate is raised.

        Args:
            folder_name: a string, containing the name of the subfolder.
            ignore_not_empty: controls behavior if the subfolder is not empty.
            ignore_not_exists: controls behavior if the subfolder doesn't
                               exist.
        Returns:
            nothing.
        Raises:
            EFailedToManipulate.
        """
        try:
            full_sub_path = os.path.join(str(self), folder_name)
            if not os.path.exists(full_sub_path):
                if not ignore_not_exists:
                    raise EFailedToManipulate(self.name, "rmdir", "subfolder " +
                                              full_sub_path + " doesn't exist.")
                return
            subfolder = FolderManipulator(full_sub_path)
            if not subfolder.is_empty() and not ignore_not_empty:
                raise EFailedToManipulate(self.name, "rmdir", "subfolder " +
                                          full_sub_path + " is not empty")
            subfolder.remove()
        except (OSError, ValueError, EFailedToInitialize) as err:
            EFailedToManipulate(self.name, "rmdir", str(err))

    def sub(self, folder_name):
        """Gets a folder manipulator for the specified subfolder.

        The subfolder should exist.

        Args:
            folder_name: a string, containing the relative path to the
                         subfolder.
        Returns:
            a subfolder manipulator.
        Raises:
            EFailedToManipulate.
        """
        try:
            full_subfolder_path = self.path / folder_name
            if not full_subfolder_path.exists():
                raise EFailedToManipulate(self.name, "sub", "subfolder " +
                                          str(full_subfolder_path) +
                                          " doesn't exist")
            return FolderManipulator(str(full_subfolder_path))
        except (OSError, ValueError, EFailedToInitialize) as err:
            raise EFailedToManipulate(self.name, "sub", str(err))

    def contains(self, name):
        """Checks if the given subfolder or file is inside the folder.

        Args:
            name: the target name of the subfolder or file to check to.
        Returns:
            True if the subfolder or file is inside the folder.
        Raises:
            EFailedToManipulate.
        """
        if not self.exists():
            raise EFailedToManipulate(self.name, "contains", "the folder " +
                                      str(self) + " doesn't exist anymore")

        try:
            for root, dirs, files in os.walk(str(self), topdown=False):
                assert root != ""
                for file_name in files:
                    if name.lower() == file_name.lower():
                        return True
                for dir_name in dirs:
                    if name.lower() == dir_name.lower():
                        return True
            return False
        except (OSError, ValueError) as err:
            raise EFailedToManipulate(self.name, "contains", str(err))

    def select(self, file_name):
        """Gets a manipulator for the specified file inside the folder.

        Args:
            file_name: a string, which specifies the name of the file.
        Returns:
            a specified file manipulator.
        Raises:
            EFailedToManipulate.
        """
        try:
            return FileManipulator(os.path.join(str(self), file_name))
        except (OSError, ValueError, EFailedToInitialize) as err:
            raise EFailedToManipulate(self.name, "select", str(err))

    def make_current(self, log_stream=DummyOutStream()):
        """Makes the manipulated folder current working folder.

        Args:
            log_stream: a stream object to log to.
        Returns:
            old working folder manipulator.
        Raises:
            EFailedToManipulate.
        """
        try:
            old = FolderManipulator(os.getcwd())

            _safe_append(log_stream, "cd " + str(self))
            os.chdir(str(self))

            return old
        except (OSError, ValueError, EFailedToInitialize) as err:
            raise EFailedToManipulate(self.name, "make_current", str(err))




# testing




def main():
    """Can be used for testing.
    """
    pass


if __name__ == '__main__':
    main()
