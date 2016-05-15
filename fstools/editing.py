"""
    Defines file data manipulator classes.
        Author: O.Z.
"""

# imports

import os
import sys
import shutil

from oztoolz.ioutils import safe_write

from oztoolz.fstools import FileManipulator
from oztoolz.fstools.errors import EFailedToManipulate

from oztoolz.streams.errors import EUnknown as EStreamError

# manipulators

class Buffer(object):
    """An abstract buffer, which can be loaded from file and saved to the file.
    The file is represented by the file manipulator.
    """

    def __init__(self, file_manipulator):
        self.__file_manipulator = file_manipulator

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.save()
        except EFailedToManipulate as err:
            safe_write(sys.stderr, "fstools Buffer failed to save " + str(err))

    @property
    def manipulator(self):
        """Gets attached file manipulator.

        Returns:
            a file manipulator.
        """
        return self.__file_manipulator

    def load(self):
        """Loads buffer from the attached file manipulator.

        Returns:
            nothing.
        Raises:
            NotImplementedError, EFailedToManipulate.
        """
        raise NotImplementedError()

    def save(self):
        """Saves buffer to the attached file.

        Returns:
            nothing.
        Raises:
            NotImplementedError, EFailedToManipulate.
        """
        raise NotImplementedError()


class Text(Buffer):
    """A text buffer class.

    The text is assumed to be consisted from paragraphs. Each paragraph is
    consisted from the words. The paragraphs are specified by the paragraph
    prototypes - objects with the 'load' method, which creates the concrete
    paragraph, using text string and the list of words prototypes.

    Attributes:
        __paragraph_prototypes: a list of paragraph prototypes.
        __unrecognized_indices: a list of indices of the unrecognized
                                paragraphs (the indicies a related to the
                                indices of the list of paragraphs).
        __indices: a table, which has names of the recognized paragraphs
                   as keys and indices in the list of paragraphs as
                   values.
        __paragraphs: a list of paragraphs in order of appearance in the text.
    """

    def __init__(self, file_manipulator, paragraph_prototypes=[],
                 default_words=[]):
        super().__init__(file_manipulator)

        self.__paragraph_prototypes = paragraph_prototypes
        
        self.__unrecognized_indices = []
        self.__indices = {}

        self.__paragraphs = []

    def __str__(self):
        text = ""
        for par in self.__paragraphs:
            text = text + str(par)
        return text

    @property
    def paragraphs(self):
        """Gets the list of paragraphs of the text.

        Returns:
            a list of paragraph objects (including unrecognized paragraphs).
        """
        return self.__paragraphs

    def get_paragraphs(self, paragraph_name):
        """Gets lists of paragraphs with specific names.

        Args:
            paragraph_name: a string, containing name of paragraphs.
        Returns:
            a list of paragraphs.
        Raises:
            nothing.
        """
        if not paragraph_name in self.__indices:
            indices = self.__indices[paragraph_name]
            return [self.__paragraphs[i] for i in indicies]
        return []

    def load(self):
        """Loads character paragraphs from the attached file manipulator.

        Returns:
            nothing.
        Raises:
            EFailedToManipulate.
        """
        try:
            text = ""
            with open(str(self.manipulator), "r") as stream:
                for line in stream:
                    text = text + str(line)
            
            start = 0
            subtext = text[start:]

            while len(subtext) != 0:
                start = len(subtext)
                cur_prototype = None
                for prototype in paragraph_prototypes:
                    cur_start_index = prototype.find_start(subtext)
                    if start > cur_start_index:
                        cur_prototype = prototype
                        start = cur_start_index

                if cur_prototype is None:
                    self.__unrecognized_indices.append(len(self.__paragraphs))
                    self.__paragraphs.append(Unrecognized(subtext,
                                                          default_words))
                    return

                if start != 0:
                    self.__unrecognized_indices.append(len(self.__paragraphs))
                    self.__paragraphs.append(Unrecognized(subtext[:start],
                                                          default_words))
                    subtext = subtext[start:]

                paragraph, finish = cur_prototype.load(subtext,
                                                       default_words)
                
                if not paragraph.name in self.__indices_table:
                    self.__indices[paragraph.name] = []

                self.__indices[paragraph.name].append(len(self.__paragraphs))
                self.__paragraphs.append(paragraph)

                if finish == len(subtext):
                    break

                subtext = subtext[finish:]
                start = 0
        except (OSError, ValueError) as err:
            raise EFailedToManipulate("Text", "load", str(err))

    def save(self):
        """Saves text to the attached file.

        Returns:
            nothing.
        Raises:
            EFailedToManipulate.
        """
        try:
            text = str(self)
            with open(str(self.manipulator)) as stream:
                stream.write(text)
        except (OSError, ValueError) as err:
            raise EFailedToManipulate("Text", "save", str(err))

# testing

def main():
    """Can be used for simple testing.
    """
    pass

if __name__ == '__main__':
    main()
